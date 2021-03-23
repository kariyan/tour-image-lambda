import logging
from urllib import parse

import boto3
import botocore

s3 = boto3.resource('s3')
logger = logging.getLogger()
client = boto3.client('s3')

PATH = 'vendor'
LIVE_BUCKET = 'tourimg.live'
DEV_BUCKET = 'tourimg.dev'
LIVE_DISTRIBUTION_ID = '***'
DEV_DISTRIBUTION_ID = '***'


class S3ImageService:
    def __init__(self, distribution_id, key):
        self.key = key

        if distribution_id == LIVE_DISTRIBUTION_ID:
            self.bucket = LIVE_BUCKET
        else:
            self.bucket = DEV_BUCKET

        logger.info("using S3 bucket name is : {}, key : {}".format(self.bucket, key))

    @classmethod
    def from_url(cls, distribution_id, origin_url, encoded_url):
        key = '{}/{}/{}'.format(PATH, parse.urlparse(origin_url).netloc, encoded_url)
        return cls(distribution_id, key)

    def upload(self, image_path):
        logger.info('upload image to S3, key : {}'.format(self.key))
        client.upload_file(image_path, self.bucket, self.key)

    def download(self, image_path):
        logger.info('download image from S3')
        client.download_file(self.bucket, self.key, image_path)

    def is_image_exists(self):
        try:
            s3.Object(self.bucket, self.key).load()

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False

            else:
                # Something else has gone wrong.
                raise
        else:
            logger.info('found an image at S3')
            return True
