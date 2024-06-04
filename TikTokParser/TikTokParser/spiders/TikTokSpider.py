import scrapy
import json

class TikTokSpider(scrapy.Spider):
    name = "TikTokSpider"
    allowed_domains = ["tokapi-mobile-version.p.rapidapi.com"]
    start_urls = [
        "https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/127905465618821121/posts"
    ]

    def start_requests(self):
        url = self.start_urls[0]
        headers = {
            "X-RapidAPI-Key": "7592632d81mshd53d10cc05bcca8p107475jsn6ef58b0782ae",
            "X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
        }
        params = {"offset": "0", "count": "10", "with_pinned_posts": "1"}
        yield scrapy.Request(url, headers=headers, method='GET', callback=self.parse, cb_kwargs={'params': params})

    def parse(self, response, params):
        data = json.loads(response.body)
        if 'aweme_list' in data and data['aweme_list']:
            for video in data['aweme_list']:
                desc = video.get('desc', 'No description')
                create_time = video.get('create_time', 'No creation time')
                statistics = video.get('statistics', {})
                digg_count = statistics.get('digg_count', 0)
                comment_count = statistics.get('comment_count', 0)
                share_count = statistics.get('share_count', 0)
                play_addr = video.get('video', {}).get('play_addr', {}).get('url_list', [])

                yield {
                    'description': desc,
                    'create_time': create_time,
                    'likes': digg_count,
                    'comments': comment_count,
                    'shares': share_count,
                    'video_links': play_addr,
                }
        else:
            self.log("No videos found or an error occurred.")
#scrapy crawl TikTokSpider -o output.json