import os
from PIL import Image
import pathlib
import numpy as np
from keras.models import model_from_json


from app.utils.shared import covert_images_jpg, resize_images

def verify(filenames):
    first_file = filenames[0]
    second_file = filenames[1]

    first_file_jpg = os.path.join(pathlib.Path(first_file).parent, pathlib.Path(first_file).stem + '.jpg')
    second_file_jpg = os.path.join(pathlib.Path(second_file).parent, pathlib.Path(second_file).stem + '.jpg')

    covert_images_jpg(first_file, first_file_jpg)
    covert_images_jpg(second_file, second_file_jpg)
    resize_images(first_file_jpg, 112, 92)
    resize_images(second_file_jpg, 112, 92)

    json_file = open('./model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("./model.h5") 

    im1 = np.asarray(Image.open(first_file_jpg))
    im1 = im1[..., np.newaxis]
    im2 = np.asarray(Image.open(second_file_jpg))
    im2 = im2[..., np.newaxis]

    return loaded_model.predict([[im1], [im2]])[0][0] < 0.5

