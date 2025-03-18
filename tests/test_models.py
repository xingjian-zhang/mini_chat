"""Tests for the models module."""

from datetime import datetime

from mini_chat.models import Conversation, Message


def test_message_creation():
    """Test creating a Message instance."""
    message = Message(role="user", content="Hello")
    assert message.role == "user"
    assert message.content == "Hello"
    assert isinstance(message.timestamp, datetime)


def test_conversation_creation():
    """Test creating a Conversation instance."""
    messages = [
        Message(role="system", content="System prompt"),
        Message(role="user", content="Hello"),
    ]
    conversation = Conversation(messages=messages)
    assert len(conversation.messages) == 2
    assert conversation.title is None


def test_add_message():
    """Test adding a message to a conversation."""
    conversation = Conversation(messages=[])
    conversation.add_message("user", "Hello")

    assert len(conversation.messages) == 1
    assert conversation.messages[0].role == "user"
    assert conversation.messages[0].content == "Hello"


def test_to_api_format():
    """Test converting a conversation to API format."""
    messages = [
        Message(role="system", content="System prompt"),
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there"),
    ]
    conversation = Conversation(messages=messages)

    api_format = conversation.to_api_format()
    assert len(api_format) == 3

    assert api_format[0]["role"] == "system"
    assert api_format[0]["content"] == "System prompt"

    assert api_format[1]["role"] == "user"
    assert api_format[1]["content"] == "Hello"

    assert api_format[2]["role"] == "assistant"
    assert api_format[2]["content"] == "Hi there"


def test_clear_messages():
    """Test clearing messages from a conversation."""
    messages = [
        Message(role="system", content="System prompt"),
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there"),
    ]
    conversation = Conversation(messages=messages)

    conversation.clear()

    # System messages should be kept
    assert len(conversation.messages) == 1
    assert conversation.messages[0].role == "system"
    assert conversation.messages[0].content == "System prompt"
