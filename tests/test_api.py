"""Tests for the api module."""

from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException

from mini_chat.api import APIError, _send_request, send_message
from mini_chat.models import Conversation, Message


@pytest.fixture
def mock_conversation():
    """Create a test conversation."""
    messages = [
        Message(role="system", content="System prompt"),
        Message(role="user", content="Hello"),
    ]
    return Conversation(messages=messages)


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    return {
        "api_base_url": "https://test-api.example.com/v1",
        "model": "test-model",
        "max_tokens": 500,
        "temperature": 0.5,
    }


@patch("mini_chat.api.load_config")
@patch("mini_chat.api.get_api_key")
@patch("mini_chat.api._send_request")
def test_send_message_non_streaming(
    mock_send_request, mock_get_api_key, mock_load_config, mock_conversation, mock_config
):
    """Test sending a message without streaming."""
    # Configure mocks
    mock_load_config.return_value = mock_config
    mock_get_api_key.return_value = "test-api-key"
    mock_send_request.return_value = "Test response"

    # Call function
    response = send_message(mock_conversation)

    # Verify results
    assert response == "Test response"

    # Verify API was called with correct parameters
    mock_send_request.assert_called_once()

    # Check headers and data
    args = mock_send_request.call_args[0]
    headers = args[0]
    data = args[1]

    assert headers["Authorization"] == "Bearer test-api-key"
    assert data["model"] == "test-model"
    assert data["stream"] is False
    assert len(data["messages"]) == 2


@patch("mini_chat.api.load_config")
@patch("mini_chat.api.get_api_key")
@patch("mini_chat.api._stream_response")
def test_send_message_streaming(
    mock_stream_response, mock_get_api_key, mock_load_config, mock_conversation, mock_config
):
    """Test sending a message with streaming."""
    # Configure mocks
    mock_load_config.return_value = mock_config
    mock_get_api_key.return_value = "test-api-key"
    mock_stream_response.return_value = "Streamed response"

    # Callback for streaming
    on_content = MagicMock()

    # Call function
    response = send_message(mock_conversation, on_content)

    # Verify results
    assert response == "Streamed response"

    # Verify streaming API was called with correct parameters
    mock_stream_response.assert_called_once()

    # Check that callback was passed
    args = mock_stream_response.call_args[0]
    assert args[3] == on_content


@patch("mini_chat.api.get_api_key")
def test_send_message_missing_api_key(mock_get_api_key, mock_conversation):
    """Test sending a message with missing API key."""
    # Configure mocks
    mock_get_api_key.return_value = None

    # Expect APIError when API key is missing
    with pytest.raises(APIError, match="API key not found"):
        send_message(mock_conversation)


@patch("requests.post")
def test_send_request_success(mock_post):
    """Test successful API request."""
    # Configure mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
    mock_post.return_value = mock_response

    # Test parameters
    headers = {"Authorization": "Bearer test-key"}
    data = {"model": "test-model"}
    base_url = "https://test-api.example.com/v1"

    # Call function
    response = _send_request(headers, data, base_url)

    # Verify results
    assert response == "Test response"

    # Verify API was called correctly
    mock_post.assert_called_once_with(
        "https://test-api.example.com/v1/chat/completions", headers=headers, json=data, timeout=30
    )


@patch("requests.post")
def test_send_request_error(mock_post):
    """Test API request with error."""
    # Configure mock response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_post.return_value = mock_response

    # Test parameters
    headers = {"Authorization": "Bearer test-key"}
    data = {"model": "test-model"}
    base_url = "https://test-api.example.com/v1"

    # Expect APIError due to non-200 status code
    with pytest.raises(APIError, match="API returned error 401"):
        _send_request(headers, data, base_url)


@patch("requests.post")
def test_send_request_network_error(mock_post):
    """Test API request with network error."""
    # Configure mock to raise exception
    mock_post.side_effect = RequestException("Network error")

    # Test parameters
    headers = {"Authorization": "Bearer test-key"}
    data = {"model": "test-model"}
    base_url = "https://test-api.example.com/v1"

    # Expect APIError due to network error
    with pytest.raises(APIError, match="API request failed"):
        _send_request(headers, data, base_url)
