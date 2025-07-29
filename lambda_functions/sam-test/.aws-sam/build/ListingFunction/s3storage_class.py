import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
from dotenv import load_dotenv
import os

from lambda_functions.listings.listings_handler import DEFAULT_REGION
from setup import region_name

load_dotenv(dotenv_path='../.env')
S3_BUCKET_NAME= os.environ.get('S3_BUCKET_NAME')
DEFAULT_REGION = os.environ.get('DEFAULT_REGION')


class S3_bucket():
    def __init__(self):
        self.s3_client = None
    def initiate_connection(self):
        self.s3_client = boto3.resource('s3',
                                        region_name= DEFAULT_REGION,
                                        profile='far-developer')
    def upload_object(self, object):
        self.s3_client.upload(object)

    def get_private_link(self,object):
        pass


