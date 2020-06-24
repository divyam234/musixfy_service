import requests
import os
import json
from .Encrpyt import encode_data, get_key
import musixfy


class ApiClient(object):

    def __init__(self):
        self.access_token = os.getenv("token")
        self.default_headers = {
            'User-Agent': 'KateMobileAndroid/49 lite-434 (Android 8.1.0; SDK 27; armeabi-v7a; Motorola MotoG3; en)'
        }
        self.http = requests.Session()
        self.proxies = {
            "http": os.getenv("proxy"),
            "https": os.getenv("proxy")
        }

    def general_get(self, url, params):
        try:
            res = self.http.get(url, headers=self.default_headers, proxies=self.proxies, params=params)
            return {**json.loads(res.text), 'status': True}

        except Exception as e:
            musixfy.app.logger.info('Exception', e.with_traceback())
            return {'status': False}

    def get_songs_list(self, query, offset):
        url = 'https://api.vk.com/method/audio.search'
        params = {
            'access_token': self.access_token,
            'q': query,
            'offset': offset,
            'sort': 2,
            'count': 100,
            'v': '5.80'
        }

        res = self.general_get(url, params)
        items = res['response']['items']
        if len(items) > 0:
            for index, item in enumerate(items):
                entry = {'artist': item['artist'], 'title': item['title']}
                encode_result = encode_data(get_key(), {**entry, 'url': item['url']}).decode('utf8')
                entry['encoded_url'] = encode_result
                items[index] = entry
        res['response']['items'] = items
        return res

    def get_video_list(self, query, offset, adult=1):
        url = 'https://api.vk.com/method/video.search'
        params = {
            'access_token': self.access_token,
            'q': query,
            'offset': offset,
            'adult': adult,
            'hd': 1,
            'sort': 2,
            'count': 100,
            'v': '5.80'
        }
        res = self.general_get(url, params)
        return res
