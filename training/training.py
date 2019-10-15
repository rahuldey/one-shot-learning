import glob
import os
import pickle

import numpy as np
from PIL import Image

from keras.models import Model, model_from_json
from keras.layers import Dense, Input, Conv2D, MaxPooling2D, Dropout, GlobalAveragePooling2D, MaxPooling2D, concatenate, Activation, Flatten, Lambda, BatchNormalization
from keras.activations import relu
from keras.optimizers import Adam
from keras import backend as K
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session

import config as conf
from aws_utils import upload_data

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
set_session(tf.Session(config=config))


def contrastive_loss(y_true, y_pred):
    margin = 1
    square_pred = K.square(y_pred)
    margin_square = K.square(K.maximum(margin - y_pred, 0))
    return K.mean(y_true * square_pred + (1 - y_true) * margin_square)


def euclidean_distance(vects):
    x, y = vects
    sum_square = K.sum(K.square(x - y), axis=1, keepdims=True)
    return K.sqrt(K.maximum(sum_square, K.epsilon()))


def eucl_dist_output_shape(shapes):
    shape1, shape2 = shapes
    return (shape1[0], 1)


def compute_accuracy(y_true, y_pred):
    pred = y_pred.ravel() < 0.5
    return np.mean(pred == y_true)


def accuracy(y_true, y_pred):
    return K.mean(K.equal(y_true, K.cast(y_pred < 0.5, y_true.dtype)))


def fire_module(name, squeeze, expand):
    def layer(x):
        squeeze_1x1 = Conv2D(squeeze, (1, 1), activation='relu',
                             padding='valid', name=name+'/squeeze1x1')(x)
        squeeze_1x1 = BatchNormalization(
            name=name+'/squeeze1x1_bn')(squeeze_1x1)
        expand_1x1 = Conv2D(expand, (1, 1), activation='relu',
                            padding='valid', name=name+'/expand1x1')(squeeze_1x1)
        expand_3x3 = Conv2D(expand, (3, 3), activation='relu',
                            padding='same', name=name+'/expand3x3')(squeeze_1x1)
        expand_merge = concatenate(
            [expand_1x1, expand_3x3], axis=3, name=name+'/concat')
        return expand_merge
    return layer


def squeeze_module(name):
    def layer(x):
        conv1 = Conv2D(64, (3, 3), activation='relu', strides=2,
                       name=name+'/conv1', padding='valid')(x)
        maxpool1 = MaxPooling2D(pool_size=(
            3, 3), strides=2, name=name+'/pool1')(conv1)
        fire2 = fire_module(squeeze=16, expand=64,
                            name=name+'/fire2')(maxpool1)
        fire3 = fire_module(squeeze=16, expand=64, name=name+'/fire3')(fire2)
        maxpool3 = MaxPooling2D(pool_size=(
            3, 3), strides=2, name=name+'/pool3')(fire3)
        fire4 = fire_module(squeeze=32, expand=128, name=name+'/fire4')(fire3)
        fire5 = fire_module(squeeze=32, expand=128, name=name+'/fire5')(fire4)
        maxpool5 = MaxPooling2D(pool_size=(
            3, 3), strides=2, name=name+'/pool5')(fire5)
        fire6 = fire_module(squeeze=48, expand=192,
                            name=name+'/fire6')(maxpool5)
        fire7 = fire_module(squeeze=48, expand=192, name=name+'/fire7')(fire6)
        fire8 = fire_module(squeeze=64, expand=256, name=name+'/fire8')(fire7)
        fire9 = fire_module(squeeze=64, expand=256, name=name+'/fire9')(fire8)
        dropout9 = Dropout(rate=0.5, name=name+'/dropout9')(fire9)
        conv10 = Conv2D(1000, (1, 1), activation='relu',
                        name=name+'/conv10')(dropout9)
        conv10 = BatchNormalization(name=name+'/conv10_bn')(conv10)
        avgpool10 = GlobalAveragePooling2D(name=name+'/pool10')(conv10)
        return avgpool10
    return layer


def create_base_model(input_shape):
    input_image = Input(shape=input_shape)
    squeeze_layer = squeeze_module(name='squeeze1')(input_image)
    dense_layer = Dense(128, activation='relu', name='dense1')(squeeze_layer)
    dense_layer = Dropout(0.1, name='dropout1')(dense_layer)
    dense_layer = Dense(128, activation='relu', name='dense2')(dense_layer)
    return Model(input_image, dense_layer)


def main():
    conf_model = conf.ModelConfig()
    conf_image = conf.ImageConfig()

    tr_pairs, tr_y = pickle.load(
        open(os.path.join(conf_model.DATA_MODEL_DIR, 'Training.pkl'), 'rb'))
    te_pairs, te_y = pickle.load(
        open(os.path.join(conf_model.DATA_MODEL_DIR, 'Testing.pkl'), "rb"))

    input_shape = (conf_image.HEIGHT, conf_image.WIDTH, conf_image.CHANNELS)
    input_a = Input(shape=input_shape)
    input_b = Input(shape=input_shape)

    base_model = create_base_model(input_shape)

    processed_a = base_model(input_a)
    processed_b = base_model(input_b)

    distance = Lambda(euclidean_distance,
                      output_shape=eucl_dist_output_shape)([processed_a, processed_b])

    model = Model([input_a, input_b], distance)
    adam = Adam()
    model.compile(loss=contrastive_loss, optimizer=adam, metrics=[accuracy])

    model.fit([tr_pairs[:, 0], tr_pairs[:, 1]], tr_y,
              batch_size=16,
              epochs=20,
              validation_data=([te_pairs[:, 0], te_pairs[:, 1]], te_y))

    model_json = model.to_json()
    with open(os.path.join(conf_model.DATA_MODEL_DIR, 'model.json'), "w") as json_file:
        json_file.write(model_json)
    model.save_weights(os.path.join(conf_model.DATA_MODEL_DIR, 'model.h5'))
    upload_data(os.environ['S3_MODEL_BUCKET'], os.path.join(
        conf_model.DATA_MODEL_DIR, 'model.json'), 'model.json')
    upload_data(os.environ['S3_MODEL_BUCKET'], os.path.join(
        conf_model.DATA_MODEL_DIR, 'model.json'), 'model.h5')


main()
