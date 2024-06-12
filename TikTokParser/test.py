import requests

url = "https://tokapi-mobile-version.p.rapidapi.com/v1/post/user/127905465618821121/posts"

querystring = {"offset":"0","count":"20"}

headers = {
	"x-rapidapi-key": "api-key",
	"x-rapidapi-host": "tokapi-mobile-version.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

data = response.json()

# Извлекаем массив aweme_list
aweme_list = data.get('aweme_list', [])

# Выводим количество элементов в aweme_list
print(len(aweme_list))
