import requests
import os.path
from dotenv import load_dotenv
import logging
import json


def read_token():
    dotenv_path = 'tokens.txt'
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    vk_token = os.getenv('token_vk')
    yandex_token = os.getenv('token_yandex')
    return vk_token, yandex_token


def id_or_screenname():
    """проверяет, является ли id числом,
    если нет, то получаем id пользователя по screen_name"""
    if id.isdigit():
        user_id = id
    else:
        user_info = vk._get('users.get', user_ids=id, fields='id')
        user_id = user_info['response'][0]['id']
    return user_id


def save_json(data, filename):
    with open(filename + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class VKconnect:
    def __init__(self, access_token, v='5.132'):
        self._access_token = access_token
        self._v = v
        self._base_url = "https://api.vk.com/method/"
        self._params = {
            'access_token': self._access_token,
            'v': self._v,
        }

    def _get(self, method, **params):
        url = self._base_url + method
        response = requests.get(url, params={**self._params, **params})
        logger.info(f'VK response: {response.json()}')
        response.raise_for_status()
        return response.json()

    def photos_get1(self, owner_id, album_id='profile', count=5):
        """Выдаёт список фотографий пользователя"""
        logger.info(f'Get photos from VK for user id {owner_id}, album id {album_id} and count {count}')
        return self._get('photos.get', owner_id=owner_id, album_id=album_id, count=count)

    def get_likes_of_photos(self, photos):
        """Выдаёт список лайков фотографий"""
        logger.info(f'Get likes from VK for {len(photos)} photos')
        likes = []
        for photo in photos['response']['items']:
            likes.append(self._get('likes.getList', type='photo', owner_id=photo['owner_id'], item_id=photo['id'])['response']['count'])
        logger.info(f'VK response: {likes}')
        return likes

    def get_date_of_photos(self, photos):
        """Выдаёт список дат загрузки фотографий"""
        logger.info(f'Get date from VK for {len(photos)} photos')
        date = []
        for photo in photos['response']['items']:
            date.append(photo['date'])
        logger.info(f'VK response: {date}')
        return date

    def photos_get(self, owner_id, album_id='profile', count=5):
        """Выдаёт список фотографий пользователя"""
        logger.info(f'Get photos from VK for user id {owner_id}, album id {album_id} and count {count}')
        response = self._get('photos.get', owner_id=owner_id, album_id=album_id, count=count)
        logger.debug(f'VK response: {response}')
        return response


class Yandexconnect:
    _url = 'https://cloud-api.yandex.net/v1/disk/resources'


    def __init__(self, token):
        logger.info('Create Yandex connection')
        self._headers = {
            'Authorization': f'OAuth {token}',
        }

    def _put(self, path, params=None):
        response = requests.put(url=self._url + path, headers=self._headers, params=params)
        logger.info(f'Yandex response: {response.json()}')
        response.raise_for_status()
        return response.json()

    def _post(self, path, params=None):
        response = requests.post(url=self._url + path, headers=self._headers, params=params)
        logger.info(f'Yandex response: {response.json()}')
        response.raise_for_status()
        return response.json()

    def create_folder(self, folder_name):
        """Создаёт папку на Яндекс.Диске"""
        logger.info(f'Create folder {folder_name} on Yandex')
        return self._put('?path=' + folder_name)

    def upload_folder(self, folder_name, photo_url_list):
        """Загружает фотографии в указанную папку на Яндекс.Диске"""
        logger.info(f'Upload folder {folder_name} to Yandex')
        for i, photo_url in enumerate(photo_url_list):
            filename = str(user_likes[i])
            print(user_likes.count(user_likes[i]))
            if user_likes.count(user_likes[i]) > 1:
                filename += '_' + str(date_photos[i])
            params = {'path': folder_name + '/' + filename + '.jpg',
                      'url': photo_url}
            self._post('/upload', params=params)

    def create_folder_and_upload(self, folder_name, photo_url_list):
        """Создаёт папку на Яндекс.Диске и загружает туда фотографии"""
        logger.info(f'Create folder {folder_name} and upload it to Yandex')
        self.create_folder(folder_name)
        self.upload_folder(folder_name, photo_url_list)


if __name__ == '__main__':
    vk_token, ya_token = read_token()
    vk = VKconnect(vk_token)
    id = input('Введите id пользователя или его ник:')
    count = int(input('Введите количество фотографий, которые хотите получить:'))
    folder_name = input('Введите название папки для фотографий:')
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    user_id = id_or_screenname()
    user = vk.photos_get(user_id, album_id='profile', count=count)
    if 'error' in user:
        logger.error('Ошибка получения фотографий')
    else:
        user_likes = vk.get_likes_of_photos(user)
        date_photos = vk.get_date_of_photos(user)
        yandex = Yandexconnect(ya_token)
        yandex.create_folder_and_upload(folder_name, [photo['sizes'][-1]['url'] for photo in user['response']['items']])
        save_json(user, folder_name)