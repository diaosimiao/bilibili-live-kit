import logging
from time import sleep

from . import API_LIVE_SIGN_GET_SIGN_INFO, API_LIVE_SIGN_DO_SIGN, HEART_DELTA
from .passport import BiliBiliPassport


class BiliBiliLiveCheckIn:
    def __init__(self, passport: BiliBiliPassport):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.passport = passport
        self.session = passport.session

    def has_check_in(self):
        rasp = self.session.get(API_LIVE_SIGN_GET_SIGN_INFO)
        payload = rasp.json()
        if payload['code'] == 0:
            return bool(payload['data']['status'])
        self.logger.info('Open has_check_in failed: %(msg)s', payload)
        return False

    def send_check_in(self):
        rasp = self.session.get(API_LIVE_SIGN_DO_SIGN)
        payload = rasp.json()
        return payload['code'] == 0


def send_check_in(passport: BiliBiliPassport):
    while True:
        if not passport.login():
            continue
        check_in = BiliBiliLiveCheckIn(passport)
        if not check_in.has_check_in():
            check_in.send_check_in()
        sleep(HEART_DELTA.total_seconds())
