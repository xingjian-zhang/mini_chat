"""Configuration management for the terminal chatbot."""

import os
from typing import Any

# Default configuration
DEFAULT_CONFIG: dict[str, Any] = {
    "api_base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo",
    "max_tokens": 1000,
    "temperature": 0.7,
    "stream": True,
    "history_size": 10,
}


def load_config() -> dict[str, Any]:
    """Load configuration from environment variables or use defaults."""
    config = DEFAULT_CONFIG.copy()

    # Override with environment variables if present
    if os.environ.get("API_BASE_URL"):
        config["api_base_url"] = os.environ.get("API_BASE_URL")
    if os.environ.get("API_MODEL"):
        config["model"] = os.environ.get("API_MODEL")
    if os.environ.get("API_MAX_TOKENS"):
        config["max_tokens"] = int(os.environ.get("API_MAX_TOKENS", "1000"))
    if os.environ.get("API_TEMPERATURE"):
        config["temperature"] = float(os.environ.get("API_TEMPERATURE", "0.7"))

    # API key is required - check OPENAI_API_KEY first, then fall back to API_KEY
    config["api_key"] = get_api_key() or ""

    return config


def get_api_key() -> str | None:
    """Get API key from environment variables."""
    # First check for OPENAI_API_KEY, then fall back to API_KEY
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")
