
import requests

VK_TOKEN_FILENAME = "vk_token.txt"

class VKException(Exception)
    """
    Класс для ошибок, возникающих при доступе к VK
    """
    pass


class VKConnector:
    """
    Класс для работы с VK
    """
    def __init__(self):
        with open(VK_TOKEN_FILENAME, "r", encoding="utf-8") as inf:
            token = inf.readline()
            if token == None or token == "":
                raise VKException(f'Не возможно считать токен из файла "{VK_TOKEN_FILENAME}"')
            self.token = token
            self.version = '5.131'
            self.params = {'access_token': self.token, 'v': self.version}

    def get_user_info(self, id: str) -> dict:
        """
        Возвращает информацию о пользователе
        :return:
        """
        url = 'https://api.vk.com/method/users.get'
        params = {
            'user_ids': id,
            "fields":"education,sex,bdate,city"
        }
        response = requests.get(url, params={**self.params, **params})
        if response.code != 200:
            raise(VKException(f'get_user_info: Ошибка при запросе фото'))
        return response.json()


    def get_user_photos(self, id: str, offset=0, number=1000):
        """
        Возвращает number фото, загруженных пользователем owner
        :param query:
        :return:
        """
        photo_params = {
            "owner_id": id,
            "album_id": "profile",
            "extended": 1,
            "offset": offset,
            "count": number
        }

        result = requests.get(
            "https://api.vk.com/method/photos.get",
            params={**self.params, **photo_params})
        if result.status_code != 200:
            raise(VKException(f'get_user_photos: Ошибка при запросе фото'))
        if "response" not in result.json():
            return None
        ret = []
        for ph in result.json()["response"]["items"]:
            size, url, img_type = None, None, None
            for s in ph["sizes"]:
                if not url or int(s["height"]) + int(s["width"]) > size or \
                        self._is_img_type_better(img_type, s["type"]):
                    size = int(s["height"]) + int(s["width"])
                    url = s["url"]
                    img_type = s["type"]
            ret.append({"likes": ph["likes"]["count"], "date": ph["date"], "url": url, "type": img_type})
        return ret

def main():
    vk = VKConnector()
    usr = vk.get_user("763904")
    print(usr)