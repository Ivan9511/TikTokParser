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
from models import resource_social, temp_posts, posts_likes

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
	                    "x-rapidapi-key": "4ef3c9f057msh0d9b9675baa5a51p1241f1jsn736936ae741f",
	                    "x-rapidapi-host": "tokapi-mobile-version.p.rapidapi.com"
                    }
                    params = {"offset": "0", "count": "1"}
                    yield scrapy.Request(url, headers=headers, method='GET', callback=self.parse, cb_kwargs={'params': params, 's_id': s_id})
            finally:
                db.close()  

    def parse(self, response, params, s_id):
        time.sleep(1)

        data = json.loads(response.body)
        if 'aweme_list' in data and data['aweme_list']:
            
            for video in data['aweme_list']:
                owner_id = s_id
                from_id = s_id
                aweme_id = video.get('aweme_id', 'No aweme id')
                title = ''
                desc = video.get('desc', 'No video_text')
                link = video.get('video', {}).get('play_addr', {}).get('url_list', ['No link'])[0]
                create_time = video.get('create_time', 0)
                statistics = video.get('statistics', {})
                digg_count = statistics.get('digg_count', 0) # likes
                comment_count = statistics.get('comment_count', 0) #comments
                share_count = statistics.get('share_count', 0) #reposts
                
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
                        link=link,
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
                    
                    db.commit()
                
                yield {
                    'owner_id': owner_id,
                    'from_id': from_id,
                    'item_id': aweme_id,
                    'reports': share_count,
                    'comments': comment_count,
                    'likes': digg_count,
                }

        else:
            self.log("No videos found or an error occurred.")

    def get_res_id_from_clickhouse(self, owner_id):
        query = text(f"SELECT id FROM imas.resource_social WHERE s_id = '{owner_id}' LIMIT 1")
        with get_clickhouse_db() as db:
            result = db.execute(query).fetchone()
            return result[0] if result else None