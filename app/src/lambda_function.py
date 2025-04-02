import os

import boto3
import json
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit

logger = Logger(service=os.getenv('OTEL_SERVICE_NAME', 'default_service_name'))

sqs = boto3.client('sqs')


@logger.inject_lambda_context
def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    logger.info("Processing file", extra={"bucket": bucket, "key": key})

    if key.startswith('videoFiles/'):
        try:
            queue_url = os.environ['SQS_QUEUE_URL']
        except KeyError:
            logger.error("SQS Queue environment variable not set")
            return {
                'statusCode': 500,
                'body': json.dumps('SQS Queue environment variable not set')
            }

        message = {'bucket': bucket, 'key': key}
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
        logger.warning("File not in videoFiles folder", extra={"key": key})
        return {
            'statusCode': 200,
            'body': json.dumps('File not in videoFiles folder')
        }