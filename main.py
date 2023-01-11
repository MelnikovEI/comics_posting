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
    comics_number = random.randint(1, get_last_comics_number())
    comics_url = f"https://xkcd.com/{comics_number}/info.0.json"
    xkcd_response = requests.get(comics_url)
    xkcd_response.raise_for_status()
    comics_item = xkcd_response.json()
    img_link = comics_item['img']
    comics_comment = comics_item['alt']
    if img_link:
        img_file_name = f'comics_{comics_number}{get_ext(img_link)}'
        download_image(img_link, img_file_name)
        return img_file_name, comics_comment


def get_vk_upload_url(vk_access_token, vk_group_id):
    params = {
        'access_token': vk_access_token,
        'v': VK_API_VERSION,
        'group_id': vk_group_id,
    }
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    vk_response = requests.get(url, params=params)
    vk_response.raise_for_status()
    upload_url = vk_response.json()['response']['upload_url']
    return upload_url


def upload_img_to_server(vk_upload_url, img_file_name):
    with open(img_file_name, 'rb') as file:
        files = {
            'photo': file,
        }
        vk_response = requests.post(vk_upload_url, files=files)
    vk_response.raise_for_status()
    uploaded_photo_params = vk_response.json()
    return uploaded_photo_params


def save_img_to_community(vk_access_token, vk_group_id, server, photo, photo_hash):
    params = {
        'access_token': vk_access_token,
        'v': VK_API_VERSION,
        'group_id': vk_group_id,
        'server': server,
        'photo': photo,
        'hash': photo_hash,
    }
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    vk_response = requests.post(url, params=params)
    vk_response.raise_for_status()
    uploaded_photo = vk_response.json()
    return uploaded_photo


def publish_comics(vk_access_token, owner_id, vk_group_id, photo_id, comics_comment):
    url = 'https://api.vk.com/method/wall.post'
    params = {
        'access_token': vk_access_token,
        'v': VK_API_VERSION,
        'attachments': f"photo{owner_id}_{photo_id}",
        'owner_id': f"-{vk_group_id}",
        'from_group': '1',
        'message': comics_comment,
    }
    vk_response = requests.post(url, params=params)
    vk_response.raise_for_status()


def main():
    img_file_name, comics_comment = download_rnd_comics()

    env = Env()
    env.read_env()
    vk_group_id = env('VK_GROUP_ID')
    vk_access_token = env('VK_ACCESS_TOKEN')

    try:
        vk_upload_url = get_vk_upload_url(vk_access_token, vk_group_id)

        uploaded_photo_params = upload_img_to_server(vk_upload_url, img_file_name)
        server = uploaded_photo_params['server']
        photo = uploaded_photo_params['photo']
        photo_hash = uploaded_photo_params['hash']

        uploaded_photo = save_img_to_community(vk_access_token, vk_group_id, server, photo, photo_hash)
        photo_id = uploaded_photo['response'][0]['id']
        owner_id = uploaded_photo['response'][0]['owner_id']

        publish_comics(vk_access_token, owner_id, vk_group_id, photo_id, comics_comment)
    finally:
        os.remove(img_file_name)


if __name__ == '__main__':
    main()
