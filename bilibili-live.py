#!/usr/bin/env python3
import json
import logging
import logging.config
import os
import re
from base64 import b64encode as base64_encode
from datetime import date, datetime, timedelta
from math import ceil
from threading import Thread
from time import sleep, time

import requests
import rsa
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

API_LIVE = 'http://live.bilibili.com'
API_LIVE_ROOM = '%s/%%s' % API_LIVE
API_LIVE_GET_ROOM_INFO = '%s/live/getInfo' % API_LIVE
API_LIVE_USER_GET_USER_INFO = '%s/User/getUserInfo' % API_LIVE
API_LIVE_USER_ONLINE_HEART = '%s/User/userOnlineHeart' % API_LIVE
API_LIVE_SIGN_DO_SIGN = '%s/sign/doSign' % API_LIVE
API_LIVE_SIGN_GET_SIGN_INFO = '%s/sign/GetSignInfo' % API_LIVE
API_LIVE_GIFT_PLAYER_BAG = '%s/gift/playerBag' % API_LIVE
API_LIVE_GIFT_BAG_SEND = '%s/giftBag/send' % API_LIVE
API_LIVE_SUMMER_HEART = '%s/summer/heart' % API_LIVE
API_LIVE_GIFT_BAG_GET_SEND_GIFT = '%s/giftBag/getSendGift' % API_LIVE
API_PASSPORT = 'https://passport.bilibili.com'
API_PASSPORT_GET_RSA_KEY = '%s/login?act=getkey' % API_PASSPORT
API_PASSPORT_MINILOGIN = '%s/ajax/miniLogin' % API_PASSPORT
API_PASSPORT_MINILOGIN_MINILOGIN = '%s/minilogin' % API_PASSPORT_MINILOGIN
API_PASSPORT_MINILOGIN_LOGIN = '%s/login' % API_PASSPORT_MINILOGIN

HEART_DELTA = timedelta(minutes=5, seconds=30)


def build_report(items):
    def build(items):
        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                yield '%20s: %s' % item
            elif isinstance(item, str) and '-' in item:
                yield '-' * 48
            else:
                yield item

    return '\n'.join(build(items))


class BiliBiliPassport:
    def __init__(
        self,
        username,
        password,
        room_id=None,
        cookies_path='bilibili.passport'
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.session()
        self.__room_id = room_id
        self.__cookies_load(username, cookies_path)
        if self.login(username, password):
            self.__cookies_save(username, cookies_path)
        else:
            self.logger.error('login faild')
            exit()

    def __handle_login_password(self, password):
        data = self.session.get(API_PASSPORT_GET_RSA_KEY).json()
        pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(data['key'])
        encrypted = rsa.encrypt((data['hash'] + password).encode(), pub_key)
        return base64_encode(encrypted).decode()

    def login(self, username, password):
        if not self.check_login():
            self.session.get(API_PASSPORT_MINILOGIN_MINILOGIN)
            payload = {
                'keep': 1,
                'captcha': '',
                'userid': username,
                'pwd': self.__handle_login_password(password)
            }
            rasp = self.session.post(API_PASSPORT_MINILOGIN_LOGIN, data=payload)
            self.logger.debug('login rasponse: %s', rasp.json())
            return rasp.json()['status']
        return True

    def check_login(self):
        rasp = self.session.get(API_LIVE_USER_GET_USER_INFO)
        return rasp.json()['code'] == 'REPONSE_OK'

    def get_room_id(self):
        if self.__room_id:
            return self.__room_id
        rasponse = self.session.get(API_LIVE)
        matches = re.search(r'data-room-id="(\d+)"', rasponse.text)
        if matches:
            return matches.group(1)

    def __cookies_load(self, username, path):
        data = {}
        if os.path.exists(path):
            with open(path, 'r') as fp:
                data = json.load(fp)
        if data and username in data:
            self.session.cookies.update(cookiejar_from_dict(data[username]))

    def __cookies_save(self, username, path):
        data = {}
        if os.path.exists(path):
            with open(path, 'r') as fp:
                data = json.load(fp)
        with open(path, 'w') as fp:
            data[username] = dict_from_cookiejar(self.session.cookies)
            json.dump(data, fp)


class BiliBiliLiveRoom:
    def __init__(self, passport: BiliBiliPassport):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.passport = passport
        self.session = passport.session

    def send_heart(self):
        headers = {'Referer': API_LIVE_ROOM % self.passport.get_room_id()}
        rasp = self.session.post(API_LIVE_USER_ONLINE_HEART, headers=headers)
        payload = rasp.json()
        if payload['code'] != 0:
            return payload['msg']
        return True

    def get_user_info(self):
        rasp = self.session.get(API_LIVE_USER_GET_USER_INFO)
        payload = rasp.json()
        if payload['code'] == 'REPONSE_OK':
            return payload
        return False

    def print_heart_report(self, user_info):
        if not user_info:
            return
        data = user_info['data']
        heart_time = datetime.now()
        upgrade_requires = data['user_next_intimacy'] - data['user_intimacy']
        upgrade_takes_time = ceil(upgrade_requires / 3000) * HEART_DELTA
        upgrade_done_time = heart_time + upgrade_takes_time
        # yapf: disable
        items = (
            '---------------------------------------',
            ('User name', data['uname']),
            ('User level', '%(user_level)s -> %(user_next_level)s' % data),
            ('User level rank', data['user_level_rank']),
            ('User intimacy', '%(user_intimacy)s -> %(user_next_intimacy)s' % data),
            ('Upgrade requires', upgrade_requires),
            ('Upgrade takes time', upgrade_takes_time),
            ('Upgrade done time', upgrade_done_time.isoformat()),
            ('Upgrade progress', '{:.6%}'.format(data['user_intimacy'] / data['user_next_intimacy'])),
            '---------------------------------------',
        )
        # yapf: enable
        self.logger.info('\n%s', build_report(items))


class BiliBiliLiveCheckIn:
    def __init__(self, passport: BiliBiliPassport):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.passport = passport
        self.session = passport.session

    def has_check_in(self):
        rasp = self.session.get(API_LIVE_SIGN_GET_SIGN_INFO)
        payload = rasp.json()
        return bool(payload['data']['status'])

    def send_check_in(self):
        rasp = self.session.get(API_LIVE_SIGN_DO_SIGN)
        payload = rasp.json()
        return payload['code'] == 0


class BiliBiliLiveGift:
    def __init__(self, passport: BiliBiliPassport):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.passport = passport
        self.session = passport.session

    def get_room_info(self, room_id):
        metainfo = self.get_room_metainfo(room_id)
        if not metainfo:
            return
        payload = {'roomid': metainfo['room_id']}
        rasp = self.session.post(API_LIVE_GET_ROOM_INFO, data=payload)
        payload = rasp.json()
        if payload['code'] == 0:
            payload['data'].update({'danmu_rnd': metainfo['danmu_rnd']})
            return payload['data']

    def get_room_metainfo(self, room_id):
        if not room_id:
            return
        rasp = self.session.get(API_LIVE_ROOM % room_id)
        pattern = r'var ROOMID = (\d+);\n.*var DANMU_RND = (\d+);'
        matches = re.search(pattern, rasp.text)
        if matches:
            return {'room_id': matches.group(1), 'danmu_rnd': matches.group(2)}

    def get_gift_renewal(self):
        self.session.get(API_LIVE_SUMMER_HEART)

    def get_gift_metainfo(self):
        rasp = self.session.get(API_LIVE_GIFT_PLAYER_BAG)
        items = rasp.json()['data']
        if not len(items):
            return
        room_id = self.passport.get_room_id()
        room_info = self.get_room_info(room_id)
        if not room_info:
            return
        return {'room_info': room_info, 'gift_items': items}

    def send_gift(self, gift_info, room_info, danmu_rnd):
        token = self.session.cookies.get(
            'LIVE_LOGIN_DATA', domain='.bilibili.com', path='/'
        )
        payload = dict(
            roomid=room_info['ROOMID'],
            ruid=room_info['MASTERID'],
            giftId=gift_info['gift_id'],
            num=gift_info['gift_num'],
            Bag_id=gift_info['id'],
            coinType='silver',
            timestamp=int(time()),
            rnd=danmu_rnd,
            token=token
        )
        rasp = self.session.post(API_LIVE_GIFT_BAG_SEND, data=payload)
        return rasp.json()['code'] == 0

    def print_gift_report(self, gift_info, room_info):
        items = (
            '---------------------------------------',
            ('Bag ID', gift_info['id']),
            ('Gift Name', gift_info['gift_name']),
            ('Gift Price', gift_info['gift_price']),
            ('Gift Number', gift_info['gift_num']),
            ('Gift Expireat', gift_info['expireat']),
            ('Sent Room ID', room_info['ROOMID']),
            '---------------------------------------',
        )
        self.logger.info('\n%s', build_report(items))


def set_logger_level(options):
    version = 1
    loggers = {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
    formatters = {
        'standard': {
            'format': '[%(asctime)s] [%(threadName)s] [%(levelname)s] ' \
                      '%(name)s: %(message)s'
        }
    }
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'level': 'INFO',
            'filename': options['filename'],
            'mode': options['filemode']
        }
    }
    logging.config.dictConfig(locals())


def send_heart(passport):
    while True:
        live = BiliBiliLiveRoom(BiliBiliPassport(**passport))
        heart_status = live.send_heart()
        user_info = live.get_user_info()
        if heart_status == True:
            live.print_heart_report(user_info)
        sleep(HEART_DELTA.total_seconds())


def send_gift(passport):
    while True:
        gift = BiliBiliLiveGift(BiliBiliPassport(**passport))
        gift.get_gift_renewal()
        metainfo = gift.get_gift_metainfo()
        if not metainfo:
            continue
        room_info = metainfo['room_info']
        danmu_rnd = room_info['danmu_rnd']
        for gift_info in metainfo['gift_items']:
            if gift_info['expireat'] != '今日':
                continue
            if gift.send_gift(gift_info, room_info, danmu_rnd):
                gift.print_gift_report(gift_info, room_info)
        sleep(HEART_DELTA.total_seconds())


def send_check_in(passport):
    while True:
        check_in = BiliBiliLiveCheckIn(BiliBiliPassport(**passport))
        if not check_in.has_check_in():
            check_in.send_check_in()
        sleep(HEART_DELTA.total_seconds())


def main():
    conf = json.load(open('configure.json'))
    set_logger_level(conf['logging'])

    for passport in conf['passports']:
        for handler in (send_heart, send_gift, send_check_in):
            thread = Thread(
                target=handler,
                name='%s ~ %s' % (handler.__name__, passport['username']),
                kwargs={'passport': passport}
            )
            thread.start()
            sleep(3)


if __name__ == '__main__':
    main()
