from PIL import Image

__ALL__ = ['get_captcha']


def get_samples() -> dict:
    from base64 import a85decode
    from zlib import decompress
    from json import loads
    payload = r'''
    GQI2t7<ZU7$q0hM`OoL]9As,ei;Ub&r_P`]j?Z.Mg@`_!BX)4]m<$nnhk[S4r>4ZtI/p[AP6665"
    :jq_g?NdgB_OZN"$uDX`/=l)$.bLeq!<h7HZ7uKJt+g1H\mA/D'KMn^o'Fg3=l2j&"jp#])_s%?%
    ;qM3ktil"O-0`%W;/@%o?mm28)6>_9L!c!NLdcrFLCl4.lguE;`rNZC1slK)fWh:a:K'!O2KgYZ2
    oa'M5eq&p\u^&><lEokTF!8q7?j@5!WGI/<aH^P7m0<K#$$`W87,KqT)cR.!YrgR7jGi!nl`fE(7
    W#=6u"UIMse^4raf+'.6'gWtBVoUlhg0gGP$B6N&:R:>Eo4gLc<@XCo'<i_uCRh"S"
    '''
    return dict(loads(decompress(a85decode(payload)).decode()))


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
