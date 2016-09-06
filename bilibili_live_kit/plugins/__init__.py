from datetime import timedelta

API_LIVE = 'http://live.bilibili.com'
API_LIVE_ROOM = '%s/%%s' % API_LIVE
API_LIVE_GET_ROOM_INFO = '%s/live/getInfo' % API_LIVE
API_LIVE_USER_GET_USER_INFO = '%s/User/getUserInfo' % API_LIVE
API_LIVE_USER_ONLINE_HEART = '%s/User/userOnlineHeart' % API_LIVE
API_LIVE_SIGN_DO_SIGN = '%s/sign/doSign' % API_LIVE
API_LIVE_SIGN_GET_SIGN_INFO = '%s/sign/GetSignInfo' % API_LIVE
API_LIVE_GIFT_PLAYER_BAG = '%s/gift/playerBag' % API_LIVE
API_LIVE_GIFT_BAG_SEND = '%s/giftBag/send' % API_LIVE
API_LIVE_GIFT_BAG_GET_SEND_GIFT = '%s/giftBag/getSendGift' % API_LIVE
API_LIVE_FREE_SILVER_GET_AWARD = '%s/FreeSilver/getAward' % API_LIVE
API_LIVE_FREE_SILVER_GET_CAPTCHA = '%s/FreeSilver/getCaptcha' % API_LIVE
API_LIVE_FREE_SILVER_GET_TASK = '%s/FreeSilver/getCurrentTask' % API_LIVE
API_PASSPORT = 'https://passport.bilibili.com'
API_PASSPORT_GET_RSA_KEY = '%s/login?act=getkey' % API_PASSPORT
API_PASSPORT_MINILOGIN = '%s/ajax/miniLogin' % API_PASSPORT
API_PASSPORT_MINILOGIN_MINILOGIN = '%s/minilogin' % API_PASSPORT_MINILOGIN
API_PASSPORT_MINILOGIN_LOGIN = '%s/login' % API_PASSPORT_MINILOGIN

HEART_DELTA = timedelta(minutes=5, seconds=30)
