#!/usr/bin/env python3

from PIL import Image

samples = {}


def load_samples():
    with open('sample.dat') as file:
        contents = file.readlines()
        for line in contents:
            line = line.strip(' \t\n\r')
            if line == "":
                continue
            char = line[-1]
            samples[char] = line[:-1]


def get_captcha(image):
    img = Image.open(image)
    img = img.convert('LA')

    result = ''

    w, h = img.size
    start = 0
    for x in range(w):
        found = False
        for y in range(h):
            point = img.getpixel((x, y))
            if point[0] < 128:
                found = True
        if found and start == 0:
            start = x
        elif not found and start > 0:
            sub_img = img.crop((start, 0, x, h))
            sub_img = trim_y(sub_img)
            code = img_to_str(sub_img)
            char = '?'
            char_score = 0
            for key, value in samples.items():
                if len(value) == len(code):
                    score = 0
                    for offset in range(0, len(value)):
                        if value[offset] == code[offset]:
                            score += 1
                    score /= len(value)
                    if score > char_score and score > 0.95:
                        char = key
                        char_score = score
            if char != '?':
                result += char
            else:
                result += '?'
                raise Exception('Unknown Char')
            start = 0
    return result


def trim_y(img):
    start = end = 0
    w, h = img.size
    for y in range(h):
        found = False
        for x in range(w):
            point = img.getpixel((x, y))
            if point[0] < 128:
                found = True
        if found:
            if start == 0:
                start = y
            end = y
    return img.crop((0, start, w, end))


def img_to_str(img):
    result = ''
    w, h = img.size
    for y in range(h):
        for x in range(w):
            point = img.getpixel((x, y))
            if point[0] < 128:
                result += '1'
            else:
                result += '0'
        result += '-'
    return result.strip('-')

load_samples()