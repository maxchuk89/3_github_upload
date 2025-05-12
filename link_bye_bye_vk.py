import os
import urllib.parse
import argparse

import requests
from dotenv import load_dotenv


def shorten_link(token, url):
    api_url = 'https://api.vk.com/method/utils.getShortLink'
    version = '5.199'

    params = {
        'access_token': token,
        'v': version,
        'url': url
    }

    response = requests.get(api_url, params=params)
    response.raise_for_status()
    reply = response.json()

    if 'error' in reply:
        raise requests.exceptions.HTTPError(reply['error']['error_msg'])

    return reply['response']['short_url']


def count_clicks(token, link):
    api_url = 'https://api.vk.com/method/utils.getLinkStats'
    version = '5.199'
    key = urllib.parse.urlparse(link).path.lstrip('/')

    params = {
        'access_token': token,
        'v': version,
        'key': key,
        'interval': 'forever'
    }

    response = requests.get(api_url, params=params)
    response.raise_for_status()
    reply = response.json()

    if 'error' in reply:
        raise requests.exceptions.HTTPError(reply['error']['error_msg'])

    stats = reply['response']['stats']
    return sum(item['views'] for item in stats)


def is_short_link(token, url):
    if urllib.parse.urlparse(url).netloc != 'vk.cc':
        return False

    api_url = 'https://api.vk.com/method/utils.getLinkStats'
    version = '5.199'
    key = urllib.parse.urlparse(url).path.lstrip('/')

    params = {
        'access_token': token,
        'v': version,
        'key': key,
        'interval': 'forever'
    }

    response = requests.get(api_url, params=params)
    response.raise_for_status()
    reply = response.json()

    return 'response' in reply and 'error' not in reply


def main():
    load_dotenv()

    token = os.getenv('VK_SERVICE_TOKEN')
    if not token:
        print('Переменная VK_SERVICE_TOKEN не найдена')
        return

    parser = argparse.ArgumentParser(description='Утилита для сокращения ссылок через VK API')
    parser.add_argument('url', help='Ссылка для сокращения или подсчёта кликов')
    args = parser.parse_args()

    try:
        if is_short_link(token, args.url):
            clicks = count_clicks(token, args.url)
            print('Кликов по ссылке:', clicks)
        else:
            short = shorten_link(token, args.url)
            print('Сокращённая ссылка:', short)
    except (requests.exceptions.RequestException, KeyError) as error:
        print('Ошибка:', error)


if __name__ == '__main__':
    main()