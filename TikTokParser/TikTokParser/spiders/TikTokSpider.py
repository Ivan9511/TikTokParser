import scrapy
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import sys
import os
import datetime
import time
from scrapy.exceptions import CloseSpider

# Добавление родительской директории в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_clickhouse_db, get_mysql_db
from models import resource_social, temp_posts, posts_likes, temp_attachments, temp_posts_max_date

class TikTokSpider(scrapy.Spider):
    name = "TikTokSpider"
    allowed_domains = ["tokapi-mobile-version.p.rapidapi.com"]

    def start_requests(self):
        with get_clickhouse_db() as db:
            try:
                # Получение всех записей из таблицы ResourceSocial
                resources = db.query(resource_social).all()
                for resource in resources:
                    s_id = resource.s_id
                    url = f"https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/{s_id}/posts"
                    headers = {
	                    "x-rapidapi-key": "API-KEY",
	                    "x-rapidapi-host": "tokapi-mobile-version.p.rapidapi.com"
                    }
                    params = {"offset": "0", "count": "10"}
                    yield scrapy.Request(url, headers=headers, method='GET', callback=self.parse, cb_kwargs={'params': params, 's_id': s_id})
            finally:
                db.close()  

    def parse(self, response, params, s_id):        
        data = json.loads(response.body)
        max_date = 0

        if 'aweme_list' in data and data['aweme_list']:
            
            for video in data['aweme_list']:
                if self.compare_date(video.get('create_time', 0), s_id):
                    owner_id = s_id
                    from_id = s_id
                    aweme_id = video.get('aweme_id', 'No aweme id')
                    title = ''
                    desc = video.get('desc', 'No video_text')
                    attachments = video.get('video', {}).get('play_addr', {}).get('url_list', ['No link'])
                    create_time = video.get('create_time', 0)
                    statistics = video.get('statistics', {})
                    digg_count = statistics.get('digg_count', 0) # likes
                    comment_count = statistics.get('comment_count', 0) #comments
                    share_count = statistics.get('share_count', 0) #reposts
                    share_url = video.get('share_url', 'No share url')

                    with get_mysql_db() as db:
                        temp_post = temp_posts(
                            owner_id=str(owner_id),
                            from_id=str(from_id),
                            item_id=str(aweme_id),
                            res_id=self.get_res_id_from_clickhouse(owner_id),
                            title=title,
                            text=desc,
                            date=create_time,
                            s_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            not_date=datetime.datetime.fromtimestamp(create_time),
                            link=share_url,
                            type=0
                        )
                        
                        db.add(temp_post)

                        if share_count != 0 or comment_count != 0 or digg_count != 0:
                            posts_like = posts_likes(
                                owner_id = str(owner_id),
                                from_id = str(from_id),
                                item_id = str(aweme_id),
                                reposts = share_count,
                                comments = comment_count,
                                likes = digg_count
                            )
                            db.add(posts_like)
                        
                            for attachment in attachments:
                                attachment_type = check_attachment_type(share_url)
                                temp_attachment = temp_attachments(
                                    type=attachment_type,
                                    attachment=share_url if attachment_type == 0 else attachment,
                                    owner_id=str(owner_id),
                                    from_id=str(from_id),
                                    item_id=str(aweme_id)
                                )
                            db.add(temp_attachment)


                        if create_time > max_date:
                            max_date = create_time

                        db.commit()
                    
                    yield {
                        'link': attachment,
                        'attachment_type': check_attachment_type(share_url),
                        'share_url': share_url
                    }
                    

        else:
            self.log("No videos found or an error occurred.")

        if max_date > 0:
            with get_mysql_db() as db:
                existing_entry = db.query(temp_posts_max_date).filter_by(res_id=self.get_res_id_from_clickhouse(s_id)).first()
                if existing_entry:
                    existing_entry.max_date = max_date
                else:
                    temp_post_max_date = temp_posts_max_date(
                        type=10,
                        res_id=self.get_res_id_from_clickhouse(s_id),
                        max_date=max_date,
                        min_date=0,
                        min_item_id='none'
                    )
                    db.add(temp_post_max_date)
                
                db.commit()

    def get_res_id_from_clickhouse(self, owner_id):
        query = text(f"SELECT id FROM imas.resource_social WHERE s_id = '{owner_id}' LIMIT 1")
        with get_clickhouse_db() as db:
            result = db.execute(query).fetchone()
            return result[0] if result else None
    
    def compare_date(self, date, s_id):
        with get_mysql_db() as db:
            latest_max_date = db.query(temp_posts_max_date.max_date).filter_by(res_id=self.get_res_id_from_clickhouse(s_id)).order_by(temp_posts_max_date.max_date.desc()).first()
            if latest_max_date:
                return date > latest_max_date.max_date
            return True  # Если таблица пуста, возвращаем True

def check_attachment_type(link):
    if "video_id" in link or "video" in link:
        return 2  # Video attachment found
    elif "photo" in link:
        return 0
    else:
        return -1