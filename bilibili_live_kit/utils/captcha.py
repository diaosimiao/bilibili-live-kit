from PIL import Image

__ALL__ = ['get_captcha']


def get_samples() -> dict:
    from base64 import decodebytes
    from zlib import decompress
    from json import loads
    payload = b'''
    eAHt2AVOBEEUhOG4cAkkjlbjXGXl/sfAKp0fGX8Zn8J6vqxvbecN+/3F28X12f5C6Vf0iRfpT1qb
    vjN/I61MRUaiNv3X4Hj8qtbr4gsmYyZhyZTNR46UTZDKL1f8+nG/a/uQUbCX74KZyAAFE2aqMjkV
    JhvU3FRvKWjCTDETZoqZMFM3g2wu2PMCdjAnbtuY0MMO9tTjDkYCNrniiPRuCyjYo3ewov0Xq0es
    C2JdEOuEmP+0Rh90xWzdMP1NFAvmEfWCrt/Dok4BRLCK6S6ZMAiDai4HYuBK97f7lRYMKrYO4z6E
    QX8tNGJjULVBWCaMi2HBgiUXTOL9SDXLVLNMhUtp2UteUm3/eOzTtrOqm++CFV+SAy5/5UIGptw4
    9jfp9f3gj8fjyQckHWV1
    '''
    samples = loads(decompress(decodebytes(payload)).decode())
    return {key: '-'.join(sample) for key, sample in samples}


def get_symbol(code: str):
    from difflib import SequenceMatcher
    from math import fabs
    ratios = sorted(
        (
            (key, SequenceMatcher(None, sample, code).ratio())
            for key, sample
            in get_samples().items()
            if fabs(len(sample) - len(code)) <= 30
        ),
        key=lambda item: -item[1]
    )
    key, ratio = ratios[0]
    if ratio < 0.95:
        raise Exception('Unknown Char')
    return key


def trim_y(image: Image) -> Image:
    start, end = 0, 0
    width, height = image.size
    for y in range(height):
        found = False
        for x in range(width):
            point = image.getpixel((x, y))[0]
            if point < 0x7F:
                found = True
        if found:
            if start == 0:
                start = y
            end = y
    return image.crop((0, start, width, end))


def image_to_ascii_image(image: Image) -> str:
    def handle():
        width, height = image.size
        for y in range(height):
            for x in range(width):
                point = image.getpixel((x, y))[0]
                yield '1' if point < 0x7F else '0'
            yield '-'

    return ''.join(handle())


def get_sub_image(image: Image):
    width, height = image.size
    start = 0
    for x in range(width):
        found = False
        for y in range(height):
            point = image.getpixel((x, y))[0]
            if point < 0x7F:
                found = True
        if found and start == 0:
            start = x
        elif not found and start > 0:
            yield trim_y(image.crop((start, 0, x, height)))
            start = 0


def get_captcha(image):
    image = Image.open(image).convert('LA')
    images = get_sub_image(image)
    images = map(image_to_ascii_image, images)
    symbols = map(get_symbol, images)
    return ''.join(symbols)
