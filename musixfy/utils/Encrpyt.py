import base64
import os
from functools import lru_cache
import json
from Crypto import Random
from Crypto.Cipher import AES

iv = Random.new().read(AES.block_size)


def encode(key, message):
    obj = AES.new(key, AES.MODE_CFB, iv)
    return base64.urlsafe_b64encode(obj.encrypt(message))


def decode(key, cipher):
    obj2 = AES.new(key, AES.MODE_CFB, iv)
    return obj2.decrypt(base64.urlsafe_b64decode(cipher))


def encode_data(key, data):
    return encode(key, json.dumps(data).encode('utf8'))


def decode_data(key, data):
    return json.loads(decode(key, data).decode('utf8'))


def get_key():
    return os.environ.get('secret', 'redux').encode('utf8')
