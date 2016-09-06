import logging
from datetime import timedelta
from io import BytesIO
from time import sleep

from . import API_LIVE_FREE_SILVER_GET_TASK, \
    API_LIVE_FREE_SILVER_GET_AWARD, \
    API_LIVE_FREE_SILVER_GET_CAPTCHA, HEART_DELTA
from .passport import BiliBiliPassport
from ..utils.captcha import get_captcha


class BiliBiliLiveTreasure:
    def __init__(self, passport: BiliBiliPassport):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.passport = passport
        self.session = passport.session
        self.time_start = 0
        self.time_end = 0
        self.amount = 0

    def get_wait_time(self) -> int:
        result = self.session.get(API_LIVE_FREE_SILVER_GET_TASK).json()
        if result['code'] == 0 and len(result['data']) > 0:
            data = result['data']
            self.logger.info('Get %(silver)d free silver in %(minute)d minutes', data)
            self.time_start = data['time_start']
            self.time_end = data['time_end']
            self.amount = data['silver']
            return int(data['minute'])
        return 0

    def open(self) -> bool:
        captcha_val = self.get_captcha()
        if captcha_val == -255:
            return False
        payload = dict(
            time_start=self.time_start,
            time_end=self.time_end,
            captcha=captcha_val
        )
        result = self.session.post(API_LIVE_FREE_SILVER_GET_AWARD, params=payload).json()
        if result['code'] == 0:
            self.logger.info('Open treasure, Got %d silver', self.amount)
            return True
        self.logger.info('Open treasure failed: %(msg)s', result)
        return False

    def get_captcha(self) -> int:
        rasp = self.session.get(API_LIVE_FREE_SILVER_GET_CAPTCHA)
        try:
            captcha = get_captcha(BytesIO(rasp.content))
            result = eval(captcha)
            self.logger.info('Resolved captcha: %s=%d', captcha, result)
            return result
        except OSError:
            self.logger.error('Request Failed!\n%s', rasp.content)
            return -255
        except 'Unknown Char':
            self.logger.error('Resolved captcha failed!')
            return -255


def send_treasure(passport):
    while True:
        treasure = BiliBiliLiveTreasure(BiliBiliPassport(passport))
        wait_time = treasure.get_wait_time()
        if wait_time > 0:
            sleep(timedelta(minutes=wait_time, seconds=1).total_seconds())
            retries = 3
            while retries > 0:
                if treasure.open():
                    break
                retries -= 1
        else:
            sleep(HEART_DELTA.total_seconds())
