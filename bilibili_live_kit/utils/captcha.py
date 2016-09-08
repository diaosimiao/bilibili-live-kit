from functools import lru_cache

from PIL import Image

__ALL__ = ['get_captcha']


@lru_cache(maxsize=1)
def get_samples():
    import base64
    import gzip
    import json
    payload = b'''
    H4sIAJug0VcC/+2YbQ7CIAyGr7Lsr5q0futVjCcx3l3RbbQM1gFjm0P+iE8Io/SltDzKQ3ktbiUa
    rVwX8Qx0m5zpBrG2kelHZcS28VnIXt3fcP+RF7Wl8Qu1rw8kawuAVBn+kOnKG1as+vGF9YxhsFlP
    EMQ+jvaEhrSZ34eDSnyXr/gGPv+TnsM5nOtGLGnj4uxj23ZR8up2i7aNIxvjR7L+lsCaJdnCeCcT
    or0tMPNoKzGeVGjG0wxjGETL67z46GVeOSSymPIiO2C4lMumPc65f3qG7CK4ktdxCfKaZYGQfYKg
    5LXhdSUbx/+o0ViXCfrmQaGLQhetXXne3++qDV2RuiuucAqH6YqH1ItXO7jLOrvDdiaH7awNLVmb
    bZx1PnsGmcvDyCn1u5uLGdcgdrLOAgBcLu3JQGYYyUAsMrwYBBUoTgZBhYxY3Ch5wf/p488SRa/n
    CzyRsY42GAAA
    '''
    return json.loads(gzip.decompress(base64.decodebytes(payload)).decode())


def get_symbol(code, threshold):
    symbol_key = '?'
    symbol_score = 0
    for key, value in get_samples().items():
        value = '-'.join(value)
        if len(value) != len(code):
            continue
        score = len(list(filter(lambda offset: value[offset] == code[offset], range(len(value)))))
        score /= len(value)
        if score < symbol_score and score < threshold:
            continue
        symbol_key = key
        symbol_score = score
    return symbol_key


def trim_y(image):
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


def image_to_ascii_image(image):
    def handle():
        width, height = image.size
        for y in range(height):
            for x in range(width):
                point = image.getpixel((x, y))[0]
                yield '1' if point < 0x7F else '0'
            yield '-'

    return ''.join(handle()).strip('-')


def get_sub_image(image):
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

    def handle():
        for sub_image in get_sub_image(image):
            symbol = get_symbol(image_to_ascii_image(sub_image), threshold=0.95)
            if symbol == '?':
                raise Exception('Unknown Char')
            yield symbol

    return ''.join(handle())
