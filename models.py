"""Data models for the terminal chatbot."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    """Represents a chat message."""
    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: datetime = datetime.now()

@dataclass
class Conversation:
    """Represents a conversation with message history."""
    messages: List[Message]
    title: Optional[str] = None
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
    
    def to_api_format(self) -> List[Dict[str, str]]:
        """Convert conversation to format expected by API."""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
    
    def clear(self) -> None:
        """Clear all messages except system messages."""
        self.messages = [msg for msg in self.messages if msg.role == "system"] 