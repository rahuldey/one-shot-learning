import os
import time

import config
from aws_utils import create_bucket, upload_att_data, delete_bucket


# delete_bucket(config.BaseConfig().S3_IMAGE_BUCKET)

# create s3 bucket
create_bucket(config.BaseConfig().S3_IMAGE_BUCKET)
create_bucket(config.BaseConfig().S3_MODEL_BUCKET)

# # upload att data to s3 bucket
upload_att_data(config.BaseConfig().S3_IMAGE_BUCKET)


# source ./set-env.sh DEVELOPMENT testkey testsecret
