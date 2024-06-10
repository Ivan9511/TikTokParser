import requests
import json

url = "https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/7100191919926346753/posts"

querystring = {"offset":"0","count":"3"}

headers = {
	"x-rapidapi-key": "api-key",
	"x-rapidapi-host": "tokapi-mobile-version.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

data = response.json()
results = []
display_image_urls = []

if 'aweme_list' in data and data['aweme_list']:
    for video in data['aweme_list']:
        attachments = video.get('video', {}).get('play_addr', {}).get('url_list', ['No link'])
        share_url = video.get('share_url', 'No share url')

        image_post_info = video.get('image_post_info', {})
        images = image_post_info.get('images', [])

        results.append({
            'attachments': attachments,
            'share_url': share_url
        })
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

print(display_image_urls)
print(share_url)
print("Number of URLs:", len(display_image_urls))

#print(json.dumps(data, indent=4))

# with open('results2.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)