resource "aws_security_group" "lambda-sg" {
  name        = "fiap-hackathon-lambda-video-receive-sg"
  description = "FIAP Hackathon - Lambda Video Receive Security Group"
  vpc_id      = data.aws_vpc.selected_vpc.id
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = data.aws_ip_ranges.api_gateway.cidr_blocks
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lambda_function" "video_receive_lambda" {
  function_name = "fiap-hackathon-lambda-video-receive"
  description   = "FIAP Hackathon - Lambda Video Receive Security Group"
  role          = data.aws_iam_role.lab_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"
  filename      = "../bin/bootstrap.zip"

  vpc_config {
    subnet_ids = [
      for subnet in data.aws_subnet.selected_subnets : subnet.id
    ]
    security_group_ids = [
      aws_security_group.lambda-sg.id
    ]
  }

  layers = [
    "arn:aws:lambda:${var.aws_region}:184161586896:layer:opentelemetry-python-0_12_0:1",
    # "arn:aws:lambda:${var.aws_region}:184161586896:layer:opentelemetry-collector-amd64-0_13_0:1"
  ]

  environment {
    variables = {
      "SQS_QUEUE_URL"                      = data.aws_sqs_queue.video-create-queue.url
      "OPENTELEMETRY_COLLECTOR_CONFIG_URI" = "/var/task/collector.yaml"
      "OTEL_SERVICE_NAME"                  = "video-receive-lambda"
      "OTEL_EXPORTER_OTLP_ENDPOINT"        = "http://${data.aws_lb.nlb.dns_name}/alloy"
      "OTEL_EXPORTER_OTLP_PROTOCOL"        = "http/protobuf"
      "OTEL_LOGS_EXPORTER"                 = "otlp"
      "OTEL_TRACES_EXPORTER"               = "otlp"
      "OTEL_METRICS_EXPORTER"              = "none"
      "OTEL_LOG_LEVEL"                     = "INFO"
      "OTEL_PROPAGATORS"                   = "tracecontext"
      "AWS_LAMBDA_EXEC_WRAPPER"            = "/opt/otel-instrument"
    }
  }
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.video_receive_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = data.aws_s3_bucket.video_file_store_bucket.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = data.aws_s3_bucket.video_file_store_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.video_receive_lambda.arn
    filter_prefix       = "videos/"
    events = [
      "s3:ObjectCreated:*"
    ]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}