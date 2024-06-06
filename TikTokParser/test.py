def check_attachment_type(link):
    if ".jpg" in link or ".jpeg" in link or ".png" in link or ".gif" in link or ".webp" in link:
        return 0  # Image attachment found
    elif ".mp4" in link or ".mov" in link or "mime_type=video" in link:
        return 2  # Video attachment found
    else:
        return -1  # No attachment type found

# Пример использования:
link = "https://v19.tiktokcdn-eu.com/a6cb5a1cc86f20da9a91d0acbab0747b/6661b570/video/tos/useast2a/tos-useast2a-pve-0068/o4zdWhLQEEYlrf3BIk8tIi0qGuBzAKopuyIzAg/?a=1233&bti=M0BzMzU8OGYpNzo5Zi5wIzEuLjpkNDQwOg%3D%3D&ch=0&cr=13&dr=0&er=0&lr=all&net=0&cd=0%7C0%7C0%7C&cv=1&ev=2&br=568&bt=284&cs=0&ds=6&ft=td_Lr8QLodzR12Nv3W4RhIxR~1z_XF_45SY&mime_type=video_mp4&qs=4&rc=MzQ7ZDk4PDo6ZDk8ZzdkPEBpajtkcWU6Zm85bjMzNzgzM0AzYF9fYGJhXjYxYzBiYzNjYSNtcGBocjRvMWtgLS1kLzZzcw%3D%3D&vvpl=1&l=202406060710330532C83657BACBA07D23&btag=e00088000"

attachment_type = check_attachment_type(link)
print("Attachment type:", attachment_type)