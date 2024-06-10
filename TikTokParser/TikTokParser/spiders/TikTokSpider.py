import scrapy
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import sys
import os
import datetime
from scrapy.exceptions import CloseSpider
import threading
from concurrent.futures import ThreadPoolExecutor

# Добавление родительской директории в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_clickhouse_db, get_mysql_db
from models import resource_social, temp_posts, posts_likes, temp_attachments, temp_posts_max_date

class TikTokSpider(scrapy.Spider):
    name = "TikTokSpider"
    allowed_domains = ["tokapi-mobile-version.p.rapidapi.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executor_res_ids = ThreadPoolExecutor(max_workers=10)
        self.executor_other_res_ids = ThreadPoolExecutor(max_workers=10)
        self.lock = threading.Lock() # Блокировка для синхронизации доступа к глобальным переменным
        self.posts_added = 0
    
    def start_requests(self):
        with get_clickhouse_db() as db:
            try:
                # Получение всех записей из таблицы ResourceSocial
                resources = db.query(resource_social).all()
                for resource in resources:
                    s_id = resource.s_id
                    res_id = resource.id
                    url = f"https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/{s_id}/posts"
                    headers = {
	                    "x-rapidapi-key": "api-key",
	                    "x-rapidapi-host": "tokapi-mobile-version.p.rapidapi.com"
                    }
                    params = {"offset": "0", "count": "20"}
                    
                    yield scrapy.Request(url, headers=headers, method='GET', callback=self.parse, cb_kwargs={'params': params, 's_id': s_id, 'res_id': res_id})
            finally:
                db.close()
    
    res_ids = [549688410, 547711860, 543331562, 548551298, 536812226, 497395160, 536812293, 552287241, 543331560, 548214770, 534723034, 534723036, 534723037, 534723038, 534723039]

    def parse(self, response, params, s_id, res_id):
        data = json.loads(response.body)
        if int(res_id) in self.res_ids:
            self.executor_res_ids.submit(self.process_data, data, s_id, res_id)
        else:
            self.executor_other_res_ids.submit(self.process_data, data, s_id, res_id)

    def process_data(self, data, s_id, res_id):
        max_date = 0

        if 'aweme_list' in data and data['aweme_list']:
            for video in data['aweme_list']:
                if self.compare_date(video.get('create_time', 0), res_id):
                    aweme_id = video.get('aweme_id', 'No aweme id')
                    title = ''
                    desc = video.get('desc', 'No video_text')
                    attachments = video.get('video', {}).get('play_addr', {}).get('url_list', ['No link'])
                    create_time = video.get('create_time', 0)
                    statistics = video.get('statistics', {})
                    digg_count = statistics.get('digg_count', 0)
                    comment_count = statistics.get('comment_count', 0)
                    share_count = statistics.get('share_count', 0)
                    share_url = video.get('share_url', 'No share url')

                    try:
                        with get_mysql_db() as db:
                            temp_post = temp_posts(
                                owner_id=str(s_id),
                                from_id=str(s_id),
                                item_id=str(aweme_id),
                                res_id=res_id,
                                title=title,
                                text=desc,
                                date=create_time,
                                s_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                not_date=datetime.datetime.fromtimestamp(create_time),
                                link=share_url.split('?')[0],
                                # обрезать ссылку, оставить только https://www.tiktok.com/@newsnurkz/video/7377738742099938566
                            )
                            db.add(temp_post)

                            attachment_count = 0
                            if check_attachment_type(share_url) == 0:
                                #фото
                                display_image_urls = []

                                image_post_info = video.get('image_post_info', {})
                                images = image_post_info.get('images', [])
                                
                                if isinstance(images, list):
                                    for image in images:
                                        display_image = image.get('display_image', {})
                                        url_list = display_image.get('url_list', [])
                                        if len(url_list) > 1:
                                            display_image_urls.append(url_list[1])
                                else:
                                    display_image = images.get('display_image', {})
                                    url_list = display_image.get('url_list', [])
                                    if len(url_list) > 1:
                                        display_image_urls.append(url_list[1])

                                for image in display_image_urls:
                                    temp_attachment = temp_attachments(
                                        type=check_attachment_type(share_url),
                                        attachment = image,
                                        owner_id=s_id,
                                        from_id=s_id,
                                        item_id=str(aweme_id)
                                    )
                                    attachment_count += 1                                    
                                    db.add(temp_attachment)

                                print(f"Количество вложений с фото - {attachment_count}")
                            else:
                                #видео
                                temp_attachment = temp_attachments(
                                    type=check_attachment_type(share_url),
                                    attachment = attachments[0],
                                    owner_id=s_id,
                                    from_id=s_id,
                                    item_id=str(aweme_id)
                                )
                                db.add(temp_attachment)

                            if share_count != 0 or comment_count != 0 or digg_count != 0:
                                posts_like = posts_likes(
                                    owner_id=str(s_id),
                                    from_id=str(s_id),
                                    item_id=str(aweme_id),
                                    reposts=share_count,
                                    comments=comment_count,
                                    likes=digg_count
                                )
                                db.add(posts_like)

                            if create_time > max_date:
                                max_date = create_time

                            db.commit()

                            with self.lock:
                                self.posts_added += 1
                    except Exception as e:
                        print(f"Ошибка: {e}")
        else:
            self.log("No videos found or an error occurred.")

        if max_date > 0:
            with get_mysql_db() as db:
                existing_entry = db.query(temp_posts_max_date).filter_by(res_id=res_id).first()
                if existing_entry:
                    existing_entry.max_date = max_date
                else:
                    temp_post_max_date = temp_posts_max_date(
                        type=10,
                        res_id=res_id,
                        max_date=max_date,
                        min_date=0,
                        min_item_id='none'
                    )
                    db.add(temp_post_max_date)
                db.commit()

    def closed(self, reason):
        print(f"\n\nИнформация с {self.posts_added} записей была добавлена в базу данных.\n\n")

    def compare_date(self, date, res_id):
        with get_mysql_db() as db:
            latest_max_date = db.query(temp_posts_max_date.max_date).filter_by(res_id=res_id).order_by(temp_posts_max_date.max_date.desc()).first()
            if latest_max_date:
                return date > latest_max_date.max_date
            return True # Если таблица пуста, возвращаем True

def check_attachment_type(share_url_link):
    if "video_id" in share_url_link or "video" in share_url_link:
        return 2
    elif "photo" in share_url_link:
        return 0
    else:
        return -1