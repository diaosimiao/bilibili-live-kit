import logging
import logging.config


def build_report(items):
    def handle(item):
        if isinstance(item, tuple) and len(item) == 2:
            return '%20s: %s' % item
        if isinstance(item, str) and '-' in item:
            return '-' * 48
        return item

    return '\n'.join(map(handle, items))


def set_logger_level(options):
    formatters = {
        'standard': {
            'format': '[%(asctime)s] [%(threadName)s] [%(levelname)s] %(name)s: %(message)s'
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
    loggers = {
        '': {
            'handlers': handlers.keys(),
            'level': 'INFO',
            'propagate': True
        }
    }
    logging.config.dictConfig({
        'version': 1,
        'formatters': formatters,
        'handlers': handlers,
        'loggers': loggers
    })
