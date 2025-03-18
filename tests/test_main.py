"""Tests for the __main__ module."""

from unittest.mock import patch

import pytest

from mini_chat.__main__ import main, process_command, show_config
from mini_chat.models import Conversation, Message


@patch("mini_chat.__main__.load_config")
@patch("mini_chat.__main__.get_api_key")
def test_main_api_key_missing(mock_get_api_key, mock_load_config, capsys):
    """Test main function when API key is missing."""
    # Mock API key to be missing
    mock_get_api_key.return_value = None

    # Should exit with error
    with pytest.raises(SystemExit) as e:
        main()

    # Check it exited with error code 1
    assert e.value.code == 1

    # Check error message contains API key info
    captured = capsys.readouterr()
    assert "No API key found" in captured.out


@patch("mini_chat.__main__.console")
def test_show_config(mock_console):
    """Test displaying the configuration."""
    config = {"model": "test-model", "temperature": 0.7}

    show_config(config)

    # Verify console.print was called
    assert mock_console.print.call_count >= 1


def test_process_command_help():
    """Test processing the help command."""
    conversation = Conversation(messages=[])
    config = {"model": "test-model"}

    with patch("mini_chat.__main__.show_help") as mock_show_help:
        running, new_config = process_command("/help", conversation, config)

        # Help command should be processed
        mock_show_help.assert_called_once()

        # Chatbot should keep running after showing help
        assert running is True

        # Config should be unchanged
        assert new_config == config


def test_process_command_exit():
    """Test processing the exit command."""
    conversation = Conversation(messages=[])
    config = {"model": "test-model"}

    running, new_config = process_command("/exit", conversation, config)

    # Chatbot should stop running
    assert running is False

    # Config should be unchanged
    assert new_config == config


@patch("mini_chat.__main__.console")
def test_process_command_clear(mock_console):
    """Test processing the clear command."""
    # Create a conversation with messages
    messages = [
        Message(role="system", content="System prompt"),
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there"),
    ]
    conversation = Conversation(messages=messages)
    config = {"model": "test-model"}

    running, new_config = process_command("/clear", conversation, config)

    # Conversation should be cleared (except system message)
    assert len(conversation.messages) == 1
    assert conversation.messages[0].role == "system"

    # Console should show a message
    mock_console.print.assert_called_with("[bold yellow]Conversation cleared.[/bold yellow]")

    # Chatbot should keep running
    assert running is True

    # Config should be unchanged
    assert new_config == config
