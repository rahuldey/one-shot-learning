import os
from enum import Enum


class Environments(Enum):
    DEVELOPMENT = 0
    PRODUCTION = 1


class BaseConfig():
    S3_IMAGE_BUCKET = 'imageverificationbucket'
    S3_MODEL_BUCKET = 'imageverificationbucketmodel'
    S3_URL = None
    DEBUG = None
    DATASET = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'datasets', 'att_faces')
    DATASET_JPG = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'datasets_jpg', 'att_faces')


class DevelopmentConfig(BaseConfig):
    S3_URL = 'http://localhost:9000'
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class ImageConfig(BaseConfig):
    HEIGHT = 112
    WIDTH = 92
    CHANNELS = 1
    AUGMENTED_NUM = 100


class ModelConfig(BaseConfig):
    TRAIN_SET_SIZE = 1500
    TEST_SET_SIZE = 500
    DATA_MODEL_DIR = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'model_data')
