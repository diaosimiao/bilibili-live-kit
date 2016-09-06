import logging
from datetime import datetime
from math import ceil
from time import sleep

from . import API_LIVE_ROOM, API_LIVE_USER_ONLINE_HEART, API_LIVE_USER_GET_USER_INFO, HEART_DELTA
from .passport import BiliBiliPassport
from ..utils import build_report


class BiliBiliLiveRoom:
    def __init__(self, passport: BiliBiliPassport):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.passport = passport
        self.session = passport.session

    def send_heart(self) -> bool:
        headers = {'Referer': API_LIVE_ROOM % self.passport.get_room_id()}
        rasp = self.session.post(API_LIVE_USER_ONLINE_HEART, headers=headers)
        payload = rasp.json()
        if payload['code'] != 0:
            self.logger.info('Open treasure failed: %(msg)s', payload)
            return False
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
        self.logger.info('\n%s', build_report(items))


def send_heart(passport):
    while True:
        live = BiliBiliLiveRoom(BiliBiliPassport(passport))
        heart_status = live.send_heart()
        user_info = live.get_user_info()
        if heart_status:
            live.print_heart_report(user_info)
        sleep(HEART_DELTA.total_seconds())
