
import requests

VK_TOKEN_FILENAME = "vk_token.txt"

class VKException(Exception):
    """
    Класс для ошибок, возникающих при доступе к VK
    """
    pass


class VKUser():
    """
    Класс для хранения данных о пользователе VK
    """

    def __init__(self, id: str, name: str, bdate: str, sex: str, city: str, photos: list):
        if id == None or id == "":
            raise VKException(f'VKUser: id пользователя не может быть пустым')
        if name == None or name == "":
            raise VKException(f'VKUser: Имя пользователя не может быть пустым')
        if bdate == None or bdate == "":
            raise VKException(f'VKUser: Дата рождения пользователя не может быть пустой')
        if sex == None or sex == "":
            raise VKException(f'VKUser: Пол пользователя не может быть пустым')
        if  city == None or city == "":
            raise VKException(f'VKUser: Город проживания пользователя не может быть пустым')
        self.__id = id
        self.__name = name
        self.__bdate = bdate
        self.__sex = sex
        self.__city = city
        self.__photos = photos

    def __str__(self):
        return f'VKUser({self.__id}, {self.__name}, {self.__bdate}, {self.__sex}, {self.__city})'

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def bdate(self):
        return self.__bdate

    @property
    def sex(self):
        return self.__sex
    @property
    def city(self):
        return self.__city

    @property
    def photos(self):
        return self.__photos

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
        if response.status_code != 200:
            raise(VKException(f'get_user_info: Ошибка при запросе фото'))
        return response.json()


    def get_user(self, id: str) -> VKUser:
        ud = self.get_user_info(id)
        photos = sorted(self.get_user_photos(id), key=lambda p: int(p["likes"]), reverse=True)[:3]

        return VKUser(ud["response"][0]["id"],
                      ud["response"][0]["first_name"] + ' ' + ud["response"][0]["last_name"],
                      ud["response"][0]["bdate"], ud["response"][0]["sex"],
                      ud["response"][0]["city"]["title"], photos)

    def _is_img_type_better(self, type1, type2):
        """
        Сравнивает типы аватарок. Нужно для того, чтобы выбрать бОльшую по размеру.
        Связано с тем, что иногда VK не возвращает размер фото, и нужно смотреть на тип
        :return:
        """
        types = ['s', 'm', 'o', 'p', 'q', 'r', 'x', 'y', 'z', 'w']

        if type1 in types and type2 in types and types.index(type1) > types.index(type2):
            return False
        return True

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

if __name__ == "__main__":
    main()