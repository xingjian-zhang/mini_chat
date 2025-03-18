"""Data models for the terminal chatbot."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Represents a chat message."""

    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    """Represents a conversation with message history."""

    messages: list[Message]
    title: str | None = None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))

    def to_api_format(self) -> list[dict[str, str]]:
        """Convert conversation to format expected by API."""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages except system messages."""
        self.messages = [msg for msg in self.messages if msg.role == "system"]
