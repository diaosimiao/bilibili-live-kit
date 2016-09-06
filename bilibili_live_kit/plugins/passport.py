import json
import logging
import os
import re
from base64 import b64encode as base64_encode

import requests
import rsa
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from . import API_LIVE, \
    API_PASSPORT_MINILOGIN_LOGIN, \
    API_LIVE_USER_GET_USER_INFO, \
    API_PASSPORT_GET_RSA_KEY, \
    API_PASSPORT_MINILOGIN_MINILOGIN


def cookies_load(session: requests.Session, username: str, path: str):
    data = {}
    if os.path.exists(path):
        with open(path, 'r') as fp:
            data = json.load(fp)
    if data and username in data:
        session.cookies.update(cookiejar_from_dict(data[username]))


def cookies_save(session: requests.Session, username: str, path: str):
    data = {}
    if os.path.exists(path):
        with open(path, 'r') as fp:
            data = json.load(fp)
    with open(path, 'w') as fp:
        data[username] = dict_from_cookiejar(session.cookies)
        json.dump(data, fp)


def handle_login_password(session: requests.Session, password: str) -> str:
    data = session.get(API_PASSPORT_GET_RSA_KEY).json()
    pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(data['key'])
    encrypted = rsa.encrypt((data['hash'] + password).encode(), pub_key)
    return base64_encode(encrypted).decode()


class BiliBiliPassport:
    def __init__(self, options: dict):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.session()
        self.options = options.get('options', {})

        self.username = options['username']
        self.password = options['password']
        self.cookies_path = options.get('cookies_path') or 'bilibili.passport'

    def login(self) -> bool:
        cookies_load(self.session, self.username, self.cookies_path)
        if not self.check_login():
            self.session.get(API_PASSPORT_MINILOGIN_MINILOGIN)
            payload = {
                'keep': 1,
                'captcha': '',
                'userid': self.username,
                'pwd': handle_login_password(self.session, self.password)
            }
            rasp = self.session.post(API_PASSPORT_MINILOGIN_LOGIN, data=payload)
            payload = rasp.json()
            status = payload['status']
            self.logger.debug('login response: %s', payload)
            if status:
                cookies_save(self.session, self.username, self.cookies_path)
            return status
        return True

    def check_login(self) -> bool:
        rasp = self.session.get(API_LIVE_USER_GET_USER_INFO)
        return rasp.json()['code'] == 'REPONSE_OK'

    def get_room_id(self) -> int:
        room_id = self.options.get('room_id')
        if isinstance(room_id, int):
            return int(room_id)
        response = self.session.get(API_LIVE)
        matches = re.search(r'data-room-id="(\d+)"', response.text)
        if matches:
            return int(matches.group(1))
