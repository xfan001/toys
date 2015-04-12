#encoding=utf-8

from pytesseract import image_to_string
from StringIO import StringIO
from PIL import ImageEnhance, Image, ImageFilter


def recognise(bin_data):
    im = Image.open(StringIO(bin_data))
    im = im.filter(ImageFilter.MedianFilter)
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im = im.convert('1')
    return image_to_string(im, lang='eng')


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as f:
        bin_data = f.read()
    print recognise(bin_data)