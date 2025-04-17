import os

import boto3
import json
from aws_lambda_powertools import Logger
from urllib.parse import unquote_plus

logger = Logger(service=os.getenv('OTEL_SERVICE_NAME', 'default_service_name'))

sqs = boto3.client('sqs', region_name='us-east-1')
s3 = boto3.client('s3', region_name="us-east-1")


@logger.inject_lambda_context
def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    raw_key = event['Records'][0]['s3']['object']['key']
    key = unquote_plus(raw_key)

    logger.info("Processing file", extra={"bucket": bucket, "key": key})

    if key.startswith('videos/'):
        try:
            queue_url = os.environ['SQS_QUEUE_URL']
        except KeyError:
            logger.error("SQS Queue environment variable not set")
            return {
                'statusCode': 500,
                'body': json.dumps('SQS Queue environment variable not set')
            }

        try:
            print(f"bucket: {str(bucket)}")
            print(f"key: {str(key)}")

            object_head_data = s3.head_object(Bucket=bucket, Key=key)
            object_metadata = object_head_data.get('Metadata')
            file_id = object_metadata['id']
        except KeyError:
            logger.error('S3 Object without x-amz-meta-id Metadata')
            return {
                'statusCode': 500,
                'body': json.dumps('S3 Object without x-amz-meta-id Metadata')
            }

        message = {'id': file_id}

        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )

        logger.info("Message sent to SQS", extra={"message_id": response['MessageId']})

        return {
            'statusCode': 200,
            'body': json.dumps('Message sent to SQS')
        }
    else:
        logger.warning("File not in videos folder", extra={"key": key})
        return {
            'statusCode': 200,
            'body': json.dumps('File not in videos folder')
        }
