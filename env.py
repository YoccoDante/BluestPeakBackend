import json
import boto3
from botocore.exceptions import ClientError


def get_mongo_secret():

    secret_name = "mongo_uri"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response['SecretString'])
    print("MongoDB connection string retrieved successfully")
    return secret['MONGO_URI']

MONGO_URI = get_mongo_secret()
BUCKET_NAME = "bluestpeakbucket"
REGION = "us-east-2"
IPN_SECRET_WORD = 'secret_word'
CLIENT_ARN = 'arn:aws:sns:us-east-2:737439452320:payment'