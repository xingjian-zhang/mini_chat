"""Tests for the __main__ module."""

from unittest.mock import MagicMock, patch

import pytest

from mini_chat.__main__ import main
from mini_chat.cli import process_command, show_config
from mini_chat.models import Conversation, Message


@patch("mini_chat.__main__.setup_signal_handler")
@patch("mini_chat.__main__.load_config")
@patch("mini_chat.__main__.Conversation")
@patch("mini_chat.__main__.display_conversation")
@patch("mini_chat.__main__.get_user_input")
def test_main_structure(
    mock_get_input, mock_display, mock_conversation_class, mock_load_config, mock_setup_signal
):
    """Test main function initialization."""
    # Set up KeyboardInterrupt to exit main loop
    mock_get_input.side_effect = KeyboardInterrupt()

    # Mock conversation instance
    mock_conversation = MagicMock()
    mock_conversation_class.return_value = mock_conversation

    # Mock config
    mock_load_config.return_value = {"system_prompt": "Test system prompt", "api_key": "test_key"}

    # Run main and verify it exits properly
    with pytest.raises(SystemExit):
        main()

    # Verify key functions were called
    mock_setup_signal.assert_called_once()
    mock_load_config.assert_called_once()
    mock_conversation.add_message.assert_called_with("system", "Test system prompt")


@patch("mini_chat.cli.console")
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

    with patch("mini_chat.ui.console"), patch("mini_chat.cli.show_help") as mock_show_help:
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

    with patch("mini_chat.cli.console") as _:
        running, new_config = process_command("/exit", conversation, config)

        # Chatbot should stop running
        assert running is False

        # Config should be unchanged
        assert new_config == config


@patch("mini_chat.cli.console")
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
