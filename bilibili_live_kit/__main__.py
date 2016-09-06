import json
import os
import sys
from threading import Thread
from time import sleep

__ALL__ = ['main']


def start_service():
    from .plugins.live_check_in import send_check_in
    from .plugins.live_gift import send_gift
    from .plugins.live_room import send_heart
    from .plugins.live_treasure import send_treasure
    from .utils import set_logger_level
    conf = json.load(open('configure.json'))
    set_logger_level(conf['logging'])

    for passport in conf['passports']:
        for handler in (send_heart, send_gift, send_check_in, send_treasure):
            thread = Thread(
                target=handler,
                name='%s ~ %s' % (handler.__name__, passport['username']),
                kwargs={'passport': passport}
            )
            thread.start()
            sleep(3)


def main():
    if sys.hexversion < 0x3050000:
        print('requires Python 3.5+.')
        exit(-1)
    if not os.path.exists('configure.json'):
        print('please "configure.json" configuration file.')
        exit(-1)
    start_service()


if __name__ == '__main__':
    main()
