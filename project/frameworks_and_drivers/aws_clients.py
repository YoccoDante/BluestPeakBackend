import boto3
from env import REGION

class S3Client:
    _instance = None

    @staticmethod
    def get_instance():
        if S3Client._instance is None:
            S3Client()
        return S3Client._instance

    def __init__(self):
        if S3Client._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.client = boto3.client(
                "s3",
                region_name=REGION
            )
            self.s3 = boto3.resource(
                "s3",
                region_name=REGION
            )
            S3Client._instance = self

class SnsClient:
    _instance = None

    @staticmethod
    def get_instance():
        if SnsClient._instance is None:
            SnsClient()
        return SnsClient._instance

    def __init__(self):
        if SnsClient._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.client = boto3.client(
                "sns",
                region_name=REGION
            )
            SnsClient._instance = self