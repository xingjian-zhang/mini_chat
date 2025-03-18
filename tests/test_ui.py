"""Tests for the ui module."""

from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress
from rich.text import Text

from mini_chat.models import Conversation, Message
from mini_chat.ui import create_loading_display, create_message_display, handle_streaming_response


@pytest.fixture
def mock_console():
    """Create a mock console."""
    return MagicMock(spec=Console)


@pytest.fixture
def mock_conversation():
    """Create a test conversation."""
    messages = [
        Message(role="system", content="System prompt"),
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there"),
    ]
    return Conversation(messages=messages)


def test_create_message_display_user():
    """Test creating display for user message."""
    message = Message(role="user", content="Hello")
    result = create_message_display(message)

    assert isinstance(result, Text)
    assert result.plain == "Hello"

    # Check if blue styling is applied (checking the spans instead of style property)
    assert any("blue" in str(span.style) for span in result.spans)


def test_create_message_display_assistant():
    """Test creating display for assistant message."""
    message = Message(role="assistant", content="# Hello\n\nHow are you?")
    result = create_message_display(message)

    assert isinstance(result, Markdown)
    assert "# Hello" in result.markup


@patch("mini_chat.ui.console")
def test_display_conversation(mock_console, mock_conversation):
    """Test displaying a conversation."""
    from mini_chat.ui import display_conversation

    display_conversation(mock_conversation)

    # Check console clear was called
    mock_console.clear.assert_called_once()

    # Should print the title
    mock_console.print.assert_any_call("[bold]Terminal Chatbot[/bold]", justify="center")

    # Should have printed user and assistant messages (2 calls per message)
    # Plus title and footer message = 5 calls minimum
    assert mock_console.print.call_count >= 5

    # System message should not be displayed
    for call in mock_console.print.call_args_list:
        args = call[0]
        if len(args) > 0 and isinstance(args[0], Text):
            assert "System" not in args[0].plain


@patch("rich.live.Live")
def test_handle_streaming_response(mock_live_class, mock_conversation):
    """Test the streaming response handler."""
    mock_live = MagicMock()
    mock_live_class.return_value = mock_live

    # Call function to get the content update callback
    callback = handle_streaming_response(mock_conversation, mock_live)

    # Add an initial assistant message
    mock_conversation.add_message("assistant", "")

    # Test the callback with content updates
    callback("Hello")
    callback(" world")

    # Check that the message was updated
    assert mock_conversation.messages[-1].content == "Hello world"

    # Live.update should have been called for each content update
    assert mock_live.update.call_count >= 2


def test_create_loading_display():
    """Test the loading display context manager."""
    with patch("mini_chat.ui.Progress") as mock_progress_class:
        mock_progress = MagicMock(spec=Progress)
        mock_progress_class.return_value = mock_progress

        # Test context manager behavior
        with create_loading_display("Testing") as progress:
            assert progress == mock_progress
            assert mock_progress.add_task.called
            assert mock_progress.add_task.call_args[0][0] == "Testing"

        # Verify progress.stop was called when context manager exits
        assert mock_progress.stop.called
