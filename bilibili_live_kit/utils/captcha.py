from PIL import Image

__ALL__ = ['get_captcha']


def get_samples() -> dict:
    from base64 import decodebytes
    from zlib import decompress
    from json import loads
    payload = b'''
    eNrtmN0OgjAMhV+FcKsmrf/6KsYnMb67DATWraNjA3TAruaXZZZyeuj2yjf5PXvkUA5Uo5rm22w6
    iOYYAE4T/LOguzKDfET0h1oNVb5pwGwWejMtvJUlzkJ0oOSFdTm3dYDCFIUpslN53/SnKqH7WdUr
    tINh7bNRxDEgrP4vgTUhcW7ayTgnZpiGaqajDkaQxoAytFlUvR4WLS+0pYS2bJCRDbeO3Y+XsHfM
    iX8Ojlp3p+mZK0kJxnVNTGH2gFwN+8Mvo9rwhvWOYbCJJwiO1xg7fHwwqMR3oo1xqI+5vY1a8K/Y
    gL4d40+L87bzHD6dfynD9SRVwMvY7uVixmvGTtbZvIOrG/JkIDOMZCAeEHoxCDpcOBkEHULEg4mS
    13X290BmR6NdK5hNuZYBI2X0NdvrnPlrd1ike93Wa8YxUmtLLu1+LEhe7w/Wq12z
    '''
    samples = loads(decompress(decodebytes(payload)).decode())
    return {key: '-'.join(sample) for key, sample in samples.items()}


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
