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
import time

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
        self.start_time_res_ids = None
        self.start_time_other_res_ids = None
        self.s_ids = ['7218022493993829381', '7120081986766029829', '6507876374678061057', '6784027677595878405', 
                      '6829576898817836037', '6845876728959828997', '6860112465217422338', '6887634007472538629', 
                      '6891899169927152642', '6936210260559102982']
        self.res_ids = self.get_res_ids_from_resource_socials(self.s_ids)
    
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
	                    "x-rapidapi-key": "API-KEY",
	                    "x-rapidapi-host": "tokapi-mobile-version.p.rapidapi.com"
                    }
                    params = {"offset": "0", "count": "20"}
                    
                    yield scrapy.Request(url, headers=headers, method='GET', callback=self.parse, cb_kwargs={'params': params, 's_id': s_id, 'res_id': res_id})
            finally:
                db.close()
    
    def parse(self, response, params, s_id, res_id):
        data = json.loads(response.body)
        if 'aweme_list' in data and data['aweme_list']:
            aweme_list = data['aweme_list']

            if int(res_id) in self.res_ids:
                if self.start_time_res_ids is None:
                    self.start_time_res_ids = time.time() 
                self.executor_res_ids.submit(self.process_data, data, s_id, res_id)
            else:
                if self.start_time_other_res_ids is None:
                    self.start_time_other_res_ids = time.time()
                self.executor_other_res_ids.submit(self.process_data, data, s_id, res_id)
            self.log(f"Received {len(aweme_list)} videos for s_id: {s_id}")                
        
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
                            )
                            db.add(temp_post)

                            attachment_count = 0
                                
                            if self.check_attachment_type(share_url) == 0:
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
                                        type=self.check_attachment_type(share_url),
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
                                    type=2,
                                    attachment = attachments[2],
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

                            try:
                                db.commit()
                            except Exception as ex:
                                print(f"Изменения базы данных не зафиксированы: {ex}")

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
                        min_item_id=0
                    )
                    db.add(temp_post_max_date)
                try:
                    db.commit()    
                except Exception as ex:
                    print(f"\n\nОШИБКА ДОБАВЛЕНИЯ temp_posts_max_date: {ex}\n\n")
                

    def closed(self, reason):
        print(f"\n\nИнформация с {self.posts_added} записей была добавлена в базу данных.\n\n")

        if self.start_time_res_ids is not None:
            end_time_res_ids = time.time()
            execution_time_res_ids = end_time_res_ids - self.start_time_res_ids
            print("\n\n1 пул -", execution_time_res_ids, "секунд")

        if self.start_time_other_res_ids is not None:
            end_time_other_res_ids = time.time()
            execution_time_other_res_ids = end_time_other_res_ids - self.start_time_other_res_ids
            print("2 пул -", execution_time_other_res_ids, "секунд\n\n")

    def compare_date(self, date, res_id):
        with get_mysql_db() as db:
            latest_max_date = db.query(temp_posts_max_date.max_date).filter_by(res_id=res_id).order_by(temp_posts_max_date.max_date.desc()).first()
            if latest_max_date:
                latest_max_date_value = latest_max_date[0] if latest_max_date[0] is not None else 0
                return date > latest_max_date_value
            return True # Если таблица пуста, возвращаем True

    def check_attachment_type(self, share_url_link):
        if "video_id" in share_url_link or "video" in share_url_link:
            return 2
        elif "photo" in share_url_link:
            return 0
        else:
            return -1
        
    def get_res_ids_from_resource_socials(self, s_ids):
        with get_clickhouse_db() as db:
            query = db.query(resource_social.id).filter(resource_social.s_id.in_(s_ids))
            result = query.all()
            ids = [record.id for record in result]
            return ids