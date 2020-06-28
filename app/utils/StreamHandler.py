import requests
import fcntl
import os
from app import config

settings = config.get_settings()


class StreamHandler(object):

    def __init__(self):
        self.content_path = settings.cache_path

    def get_range_bytes(self, from_bytes, until_bytes, payload):
        url = payload['url']
        key = payload['key']
        file_path = os.path.join(self.content_path, key + '.mp3')
        # check If we have access to file
        access = os.access(file_path, os.W_OK)
        if access is True:
            file_size = os.path.getsize(file_path)
            if from_bytes:
                from_bytes = int(from_bytes)
            if until_bytes:
                until_bytes = int(until_bytes)

            read_bytes = file_size - from_bytes
            if until_bytes:
                read_bytes = until_bytes - from_bytes + 1
            with open(file_path, 'rb') as f:
                f.seek(from_bytes)
                data = f.read(read_bytes)
            return {'content': data, 'content-range': f"bytes {from_bytes}-{from_bytes + read_bytes - 1}/{file_size}",
                    'content-length': read_bytes}
        else:
            if until_bytes:
                until_bytes = int(from_bytes) + int(1024 * 1024 * 1)
            headers = {'Range': 'bytes=%s-%s' % (from_bytes, until_bytes)}
            r = requests.get(url, headers=headers)
            return {'content': r.content, 'content-range': r.headers.get('Content-Range'),
                    'content-length': r.headers.get('Content-Length')}

    def download_file(self, data):
        url = data['url']
        key = data['key']
        file_name = os.path.join(self.content_path, key + '.mp3')
        if os.access(file_name, os.R_OK) is not True:
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(file_name, 'wb') as f:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            fcntl.flock(f, fcntl.LOCK_UN)
                        f.close()
                return True
            except Exception as e:
                # log Exception
                if os.access(file_name, os.X_OK) is True:
                    os.remove(file_name)
                return False
        return True
