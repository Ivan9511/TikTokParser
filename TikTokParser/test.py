def check_attachment_type(link):
    if "video_id" in link or "video" in link:
        return 2  # Video attachment found
    elif "photo" in link:
        return 0
    else:
        return -1

# Пример использования:
photo_link = "https://www.tiktok.com/@uzbekistannews/photo/7374363263619943685?_d=ed7862290bg182&_r=1&preview_pb=0&share_item_id=7374363263619943685&sharer_language=en&source=h5_m&u_code=ed787kamd935l7"

music_link = "https://sf16-music-sign.tiktokcdn.com/obj/tos-alisg-ve-2774/oYWiBQZMUjpCYK8DYKIEAFvgrANaiEBUj6U2M?lk3s=08d74b56&x-expires=1717694404&x-signature=h4TMkIJKE3RboGf84lp1ilL2t1I%3D"

attachment_type = check_attachment_type(music_link)
print("Attachment type:", attachment_type)

if check_attachment_type(music_link) == 0:
    print("True")
else:
    print("False")