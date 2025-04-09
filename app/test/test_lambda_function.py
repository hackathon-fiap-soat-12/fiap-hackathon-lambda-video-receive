import os
from unittest.mock import patch

import pytest

from src.lambda_function import lambda_handler


def test_invalid_event_raises_key_error_exception(fixture_invalid_event, fixture_mock_context):
    with pytest.raises(KeyError):
        lambda_handler(fixture_invalid_event, fixture_mock_context)


@patch('src.lambda_function.logger')
def test_event_not_from_video_files_folder(mock_logger, fixture_event_not_from_video_file, fixture_mock_context):
    response = lambda_handler(fixture_event_not_from_video_file, fixture_mock_context)

    mock_logger.info.assert_any_call("Processing file", extra={"bucket": "fake_bucket", "key": "fake_key"})
    mock_logger.warning.assert_any_call("File not in videos folder", extra={"key": "fake_key"})

    assert response['statusCode'] == 200
    assert response['body'] == '"File not in videos folder"'


@patch('src.lambda_function.logger')
def test_sqs_queue_url_not_defined(mock_logger, fixture_event_from_video_file, fixture_mock_context):
    response = lambda_handler(fixture_event_from_video_file, fixture_mock_context)

    mock_logger.info.assert_any_call("Processing file", extra={"bucket": "fake_bucket", "key": "videos/fake_key"})
    mock_logger.error.assert_any_call("SQS Queue environment variable not set")

    assert response['statusCode'] == 500
    assert response['body'] == '"SQS Queue environment variable not set"'


@patch('src.lambda_function.logger')
@patch('src.lambda_function.sqs')
@patch.dict(os.environ, {'SQS_QUEUE_URL': 'https://sqs-url'})
def test_raises_exception_when_sqs_send_message_fails(
        mock_sqs, mock_logger, fixture_event_from_video_file, fixture_mock_context
):
    mock_sqs.send_message.side_effect = Exception("fake exception message")

    with pytest.raises(Exception):
        lambda_handler(fixture_event_from_video_file, fixture_mock_context)

    mock_logger.info.assert_any_call("Processing file", extra={"bucket": "fake_bucket", "key": "videos/fake_key"})


@patch('src.lambda_function.logger')
@patch('src.lambda_function.sqs')
@patch.dict(os.environ, {'SQS_QUEUE_URL': 'https://sqs-url'})
def test_send_message_successfully(mock_sqs, mock_logger, fixture_event_from_video_file, fixture_mock_context):
    mock_sqs.send_message.return_value = {"MessageId": "FakeValue"}

    response = lambda_handler(fixture_event_from_video_file, fixture_mock_context)

    mock_logger.info.assert_any_call("Processing file", extra={"bucket": "fake_bucket", "key": "videos/fake_key"})
    mock_logger.info.assert_any_call("Message sent to SQS", extra={"message_id": "FakeValue"})

    assert response['statusCode'] == 200
    assert response['body'] == '"Message sent to SQS"'
