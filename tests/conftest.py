"""Common pytest fixtures and configuration."""

import os
import pathlib
import tempfile
from unittest.mock import patch

import pytest

from mini_chat.models import Conversation, Message


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(role="user", content="Test message")


@pytest.fixture
def sample_conversation():
    """Create a sample conversation for testing."""
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there! How can I help you today?"),
    ]
    return Conversation(messages=messages)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture(autouse=True)
def mock_environment():
    """Mock environment variables for tests."""
    with patch.dict(os.environ, {"API_KEY": "test_api_key"}, clear=False):
        yield
