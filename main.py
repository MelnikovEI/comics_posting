import os
import random
import urllib
from pathlib import Path
import requests
from environs import Env

VK_API_VERSION = '5.131'


def download_image(url, file_name, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(Path.cwd() / file_name, 'wb') as file_to_save:
        file_to_save.write(response.content)


def get_ext(url: str) -> str:
    split_url = urllib.parse.urlsplit(url)
    split_path = os.path.split(split_url.path)
    split_file_name = os.path.splitext(split_path[1])
    return split_file_name[1]


def get_last_comics_number():
    last_comics_url = "https://xkcd.com/info.0.json"
    xkcd_response = requests.get(last_comics_url)
    xkcd_response.raise_for_status()
    comics_item = xkcd_response.json()
    return comics_item['num']


def download_rnd_comics():
    numb = random.randint(1, get_last_comics_number())
    comics_url = f"https://xkcd.com/{numb}/info.0.json"
    xkcd_response = requests.get(comics_url)
    xkcd_response.raise_for_status()
    comics_item = xkcd_response.json()
    img_link = comics_item['img']
    comics_comment = comics_item['alt']
    if img_link:
        img_file_name = f'comics_{numb}{get_ext(img_link)}'
        download_image(img_link, img_file_name)
        return img_file_name, comics_comment


def comics_posting(params, img_file_name, comics_comment):
    params = params
    # Получаем адрес сервера для загрузки фото
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    vk_response = requests.get(url, params=params)
    vk_response.raise_for_status()
    upload_url = vk_response.json()['response']['upload_url']

    # Отправляем фото на сервер
    with open(img_file_name, 'rb') as file:
        files = {
            'photo': file,
        }
        vk_response = requests.post(upload_url, files=files)
        vk_response.raise_for_status()
        uploaded_photo_params = vk_response.json()

    # Сохраняем фото на стене
    params.update({
        'server': uploaded_photo_params['server'],
        'photo': uploaded_photo_params['photo'],
        'hash': uploaded_photo_params['hash'],
    })
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    vk_response = requests.post(url, params=params)
    vk_response.raise_for_status()
    uploaded_photo = vk_response.json()

    # Публикуем комикс в группе
    photo_id = uploaded_photo['response'][0]['id']
    owner_id = uploaded_photo['response'][0]['owner_id']
    url = 'https://api.vk.com/method/wall.post'
    params.update({
        'attachments': f"photo{owner_id}_{photo_id}",
        'message': comics_comment,
    })
    vk_response = requests.post(url, params=params)
    vk_response.raise_for_status()


def main():
    env = Env()
    env.read_env()
    params = {
        'access_token': env('ACCESS_TOKEN'),
        'v': VK_API_VERSION,
        'group_id': env('VK_GROUP_ID'),
        'owner_id': f"-{env('VK_GROUP_ID')}",
        'from_group': '1',
    }

    # Скачиваем комикс
    img_file_name, comics_comment = download_rnd_comics()
    # Публикуем комикс
    comics_posting(params, img_file_name, comics_comment)
    # Удаляем скачанный файл
    os.remove(img_file_name)


if __name__ == '__main__':
    main()
