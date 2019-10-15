import pathlib
import os
import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

import config

# reads configuration file and returns config object


def get_configuration():
    if os.environ['ENVIRON'] == config.Environments.DEVELOPMENT.name:
        return config.DevelopmentConfig()
    elif os.environ['ENVIRON'] == config.Environments.PRODUCTION.name:
        return config.ProductionConfig()
    else:
        raise EnvironmentError('Unknown Environment')

# returns initialised s3 client object


def get_s3_client(conf):
    if conf.S3_URL != None:
        return boto3.client('s3',
                            endpoint_url=conf.S3_URL,
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                            config=Config(signature_version='s3v4'))
    else:
        return boto3.client('s3',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

# creates bucket in s3


def create_bucket(bucket_name):
    conf = get_configuration()
    try:
        s3_client = get_s3_client(conf)
        s3_client.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)

# deletes bucket in s3


def delete_bucket(bucket_name):
    conf = get_configuration()
    s3 = None
    if conf.S3_URL != None:
        s3 = boto3.resource('s3',
                            endpoint_url=conf.S3_URL,
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                            config=Config(signature_version='s3v4'))
    else:
        s3 = boto3.resource('s3',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

    bucket = s3.Bucket(bucket_name)
    for key in bucket.objects.all():
        key.delete()
    bucket.delete()

# uploads data to s3 bucket


def upload_data(bucket_name, file_name, key):
    conf = get_configuration()
    s3_client = get_s3_client(conf)
    try:
        s3_client.upload_file(file_name, bucket_name, key)
    except ClientError as e:
        logging.error(e)
    except Exception as e:
        logging.error(e)

# downloads data from bucket and returns a handle to the file


def download_data(bucket_name, key):
    conf = get_configuration()
    s3_client = get_s3_client(conf)
    f = open('file.pgm', 'wb+')
    try:
        s3_client.download_fileobj(bucket_name, key, f)
    except ClientError as e:
        logging.error(e)
    return f

# downloads the att images dataset


def walk_over_all_images(bucket_name):
    image_list = []
    conf = get_configuration()
    s3_client = get_s3_client(conf)
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
    except ClientError as e:
        logging.error(e)
    result = paginator.paginate(Bucket=bucket_name)
    for page in result:
        if "Contents" in page:
            for key in page["Contents"]:
                image_list.append(key["Key"])
    return image_list

# uploads the att image data to s3 bucket


def upload_att_data(bucket_name):
    conf = get_configuration()
    for root, dirs, files in os.walk(conf.DATASET, topdown=False):
        for file in files:
            if '.pgm' not in file:
                continue
            file_name = os.path.join(root, file)
            key = '/'.join(file_name.split('/')[-4:])
            response = upload_data(bucket_name, file_name, key)
