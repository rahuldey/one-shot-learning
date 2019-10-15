import os
import random
import string
from PIL import Image


def random_string(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def covert_images_jpg(infile, outfile):
    im = Image.open(infile)
    im.save(outfile)
    im.close()

def resize_images(infile, height, width):
    im = Image.open(infile)
    im2 = im.resize((width, height))
    random_name = random_string(5) + '.jpg'
    im2.save(random_name)

    im.close()
    os.remove(infile)
    os.rename(random_name, infile)
