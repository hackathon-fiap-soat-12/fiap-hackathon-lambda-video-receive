# import os

# import boto3
# import json
# from aws_lambda_powertools import Logger

# logger = Logger(service=os.getenv('OTEL_SERVICE_NAME', 'default_service_name'))

# sqs = boto3.client('sqs')


# @logger.inject_lambda_context
# def lambda_handler(event, context):
#     bucket = event['Records'][0]['s3']['bucket']['name']
#     key = event['Records'][0]['s3']['object']['key']

#     logger.info("Processing file", extra={"bucket": bucket, "key": key})

#     if key.startswith('videos/'):
#         try:
#             queue_url = os.environ['SQS_QUEUE_URL']
#         except KeyError:
#             logger.error("SQS Queue environment variable not set")
#             return {
#                 'statusCode': 500,
#                 'body': json.dumps('SQS Queue environment variable not set')
#             }

#         message = {'bucket': bucket, 'key': key}
#         response = sqs.send_message(
#             QueueUrl=queue_url,
#             MessageBody=json.dumps(message)
#         )

#         logger.info("Message sent to SQS", extra={"message_id": response['MessageId']})

#         return {
#             'statusCode': 200,
#             'body': json.dumps('Message sent to SQS')
#         }
#     else:
#         logger.warning("File not in videos folder", extra={"key": key})
#         return {
#             'statusCode': 200,
#             'body': json.dumps('File not in videos folder')
#         }


import os
import boto3
import json
from aws_lambda_powertools import Logger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import inject

# Initialize the Powertools Logger
logger = Logger(service=os.getenv('OTEL_SERVICE_NAME', 'default_service_name'))

# Initialize the SQS client
sqs = boto3.client('sqs')

# Set up OpenTelemetry Tracer Provider
endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318')
traces_endpoint = f'{endpoint}/v1/traces'
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(OTLPSpanExporter(endpoint=traces_endpoint))
)
tracer = trace.get_tracer(__name__)

@logger.inject_lambda_context
def lambda_handler(event, context):
    # Start a root span for the Lambda handler
    with tracer.start_as_current_span("lambda_handler") as span:
        # Extract bucket and key from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        # Log with trace ID and span ID
        span_context = span.get_span_context()
        logger.info("Processing file", extra={
            "bucket": bucket,
            "key": key,
            "trace_id": format(span_context.trace_id, '032x'),  # Convert to hex
            "span_id": format(span_context.span_id, '016x')      # Convert to hex
        })

        if key.startswith('videos/'):
            try:
                queue_url = os.environ['SQS_QUEUE_URL']
            except KeyError:
                logger.error("SQS Queue environment variable not set", extra={
                    "trace_id": format(span_context.trace_id, '032x'),
                    "span_id": format(span_context.span_id, '016x')
                })
                return {
                    'statusCode': 500,
                    'body': json.dumps('SQS Queue environment variable not set')
                }

            message = {'bucket': bucket, 'key': key}

            # Propagate trace context to SQS
            carrier = {}
            inject(carrier)
            message_attributes = {
                'traceparent': {
                    'DataType': 'String',
                    'StringValue': carrier['traceparent']
                }
            }
            if 'tracestate' in carrier:
                message_attributes['tracestate'] = {
                    'DataType': 'String',
                    'StringValue': carrier['tracestate']
                }

            # Start a child span for SQS send_message
            with tracer.start_as_current_span("sqs.send_message") as sqs_span:
                response = sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(message),
                    MessageAttributes=message_attributes
                )
                sqs_span.set_attribute("message_id", response['MessageId'])

            logger.info("Message sent to SQS", extra={
                "message_id": response['MessageId'],
                "trace_id": format(span_context.trace_id, '032x'),
                "span_id": format(span_context.span_id, '016x')
            })

            return {
                'statusCode': 200,
                'body': json.dumps('Message sent to SQS')
            }
        else:
            logger.warning("File not in videos folder", extra={
                "key": key,
                "trace_id": format(span_context.trace_id, '032x'),
                "span_id": format(span_context.span_id, '016x')
            })
            return {
                'statusCode': 200,
                'body': json.dumps('File not in videos folder')
            }