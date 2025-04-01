from unittest.mock import Mock

import pytest


@pytest.fixture()
def fixture_invalid_event() -> dict:
    return {
        "fake_key": "fake_value"
    }


@pytest.fixture()
def fixture_event_not_from_video_file() -> dict:
    return {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': 'fake_bucket'
                    },
                    'object': {
                        'key': 'fake_key'
                    }
                },
            }
        ]
    }


@pytest.fixture()
def fixture_event_from_video_file() -> dict:
    return {
        'Records': [
            {
                's3': {
                    'bucket': {
                        'name': 'fake_bucket'
                    },
                    'object': {
                        'key': 'videoFiles/fake_key'
                    }
                },
            }
        ]
    }


@pytest.fixture()
def fixture_mock_context():
    return Mock()
