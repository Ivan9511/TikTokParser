import requests

url = "https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/127905465618821121/posts"

querystring = {"offset":"0","count":"3", "with_pinned_posts":"1"}

headers = {
	"X-RapidAPI-Key": "7592632d81mshd53d10cc05bcca8p107475jsn6ef58b0782ae",
	"X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

data = response.json()

if 'aweme_list' in data and data['aweme_list']:
    for video in data['aweme_list']:
        desc = video.get('desc', 'No description')
        create_time = video.get('create_time', 'No creation time')
        statistics = video.get('statistics', {})
        digg_count = statistics.get('digg_count', 0)
        comment_count = statistics.get('comment_count', 0)
        share_count = statistics.get('share_count', 0)
        play_addr = video.get('video', {}).get('play_addr', {}).get('url_list', [])
        
        print(f"Описание: {desc}")
        print(f"Дата создания (unixtime): {create_time}")
        print(f"Лайки: {digg_count}")
        print(f"Комментарии: {comment_count}")
        print(f"Репосты: {share_count}")
        print(f"Ссылки на видео: {play_addr}")
        print("\n")
else:
    print("Видео не найдены или возникла ошибка")