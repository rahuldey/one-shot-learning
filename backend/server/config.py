import os
from enum import Enum

class BaseConfig():
    S3_MODEL_BUCKET = 'imageverificationbucketmodel'
    DEBUG = False
    S3_URL = None
    UPLOAD_FOLDER = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'uploads')
    MODEL_JSON = 'model.json'
    MODEL_H5 = 'model.h5'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    S3_URL = 'http://localhost:9000/'


class ProductionConfig(BaseConfig):
    DEBUG = False


