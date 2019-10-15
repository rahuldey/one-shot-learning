import os
import config
import pathlib
from PIL import Image
import numpy as np
import pickle
from keras.preprocessing.image import ImageDataGenerator
from aws_utils import walk_over_all_images, download_data
from shared import covert_images_jpg, resize_images


def download_from_s3():
    data_dir = config.BaseConfig().DATASET_JPG
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    image_list = walk_over_all_images(config.BaseConfig().S3_IMAGE_BUCKET)
    for key in image_list:
        if '.pgm' not in key:
            continue
        input_file = os.path.join(data_dir, '/'.join(key.split('/')[1:]))
        parent = pathlib.Path(input_file).parent
        name = pathlib.Path(input_file).stem

        if not os.path.exists(parent):
            os.makedirs(parent)

        covert_images_jpg(download_data(
            config.BaseConfig().S3_IMAGE_BUCKET, key), os.path.join(parent, name + '.jpg'))


def resize_s3_images():
    conf = config.ImageConfig()
    for root, dirs, files in os.walk(conf.DATASET_JPG, topdown=False):
        for file in files:
            if '.jpg' not in file:
                continue

            input_file = os.path.join(root, file)
            parent = pathlib.Path(input_file).parent
            name = pathlib.Path(input_file).stem

    for root, dirs, files in os.walk(conf.DATASET_JPG, topdown=False):
        img_size = (conf.WIDTH, conf.HEIGHT)
        resize_images(input_file, conf.WIDTH, conf.HEIGHT)


def create_augmented_images():
    conf = config.ImageConfig()
    imgen = ImageDataGenerator(
        rotation_range=30,
        horizontal_flip=0.5)

    for root, dirs, files in os.walk(conf.DATASET_JPG, topdown=False):
        for file in files:
            if '.jpg' not in file:
                continue

            input_file = os.path.join(root, file)
            parent = pathlib.Path(input_file).parent
            name = pathlib.Path(input_file).stem

            im_arr = np.asarray(Image.open(input_file))

            for i in range(conf.AUGMENTED_NUM):
                im_arr_augmented = imgen.random_transform(
                    im_arr[..., np.newaxis])[:, :, 0]
                Image.fromarray(im_arr_augmented).save(os.path.join(
                    parent, name + '-augmented-{}'.format(i) + '.jpg'))


def create_pairs(set_type):
    conf = config.ModelConfig()

    if set_type not in ['Training', 'Testing']:
        raise ValueError('Incorrect value for set_type: {}'.format(set_type))

    set_size = conf.TRAIN_SET_SIZE if set_type == 'Training' else conf.TEST_SET_SIZE

    file_path = os.path.join(conf.DATASET_JPG, set_type)
    dirnames = [os.path.join(file_path, dirname)
                for dirname in os.listdir(file_path)]
    filenames = []
    for dirname in dirnames:
        filenames.append([os.path.join(dirname, filename)
                          for filename in os.listdir(dirname)])

    num_classes = len(filenames)

    pairs = []
    labels = []
    for i, dirname in enumerate(filenames):
        for _ in range(set_size):

            # selecting two images of the same category
            im_path_1 = filenames[i][np.random.choice(len(filenames[i]), 1)[0]]
            im_path_2 = filenames[i][np.random.choice(len(filenames[i]), 1)[0]]

            im_1 = np.asarray(Image.open(im_path_1))
            im_1 = im_1[..., np.newaxis]

            im_2 = np.asarray(Image.open(im_path_2))
            im_2 = im_2[..., np.newaxis]

            # selecting one image of a different class
            inc = np.random.choice(num_classes, 1)[0]
            ix = (i + inc) % num_classes
            im_path_3 = filenames[ix][np.random.choice(
                len(filenames[ix]), 1)[0]]

            im_3 = np.asarray(Image.open(im_path_3))
            im_3 = im_3[..., np.newaxis]

            pairs += [[im_1, im_2]]
            pairs += [[im_1, im_3]]
            labels += [1, 0]

    output_dir = os.path.join(conf.DATA_MODEL_DIR, '{}.pkl'.format(set_type))
    if not os.path.exists(conf.DATA_MODEL_DIR):
        os.makedirs(conf.DATA_MODEL_DIR)
    pickle.dump((np.array(pairs), np.array(labels)), open(output_dir, "wb"))


create_pairs('Training')
create_pairs('Testing')
