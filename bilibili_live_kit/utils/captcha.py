from PIL import Image

from .captcha_sample import payload as __samples

__ALL__ = ['get_captcha']


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


def img_to_str(image):
    def handle():
        width, height = image.size
        for y in range(height):
            for x in range(width):
                point = image.getpixel((x, y))[0]
                yield '1' if point < 0x7F else '0'
            yield '-'

    return ''.join(handle()).strip('-')


def get_symbol_score(code, samples):
    symbol_key = '?'
    symbol_score = 0
    for key, value in samples.items():
        value = '-'.join(value)
        if len(value) != len(code):
            continue
        score = len(list(filter(lambda offset: value[offset] == code[offset], range(len(value)))))
        score /= len(value)
        if score < symbol_score and score < .95:
            continue
        symbol_key = key
        symbol_score = score
    return symbol_key, symbol_score


def get_captcha(image):
    image = Image.open(image)
    image = image.convert('LA')

    def handle():
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
                sub_img = image.crop((start, 0, x, height))
                sub_img = trim_y(sub_img)
                code = img_to_str(sub_img)
                symbol_key, symbol_score = get_symbol_score(code, __samples)
                if symbol_key == '?':
                    raise Exception('Unknown Char')
                yield symbol_key
                start = 0

    return ''.join(handle())
