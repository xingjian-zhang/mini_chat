"""Configuration management for the terminal chatbot."""

import logging
import os
import pathlib
from typing import Any

import yaml  # type: ignore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mini_chat.config")

# Default configuration
DEFAULT_CONFIG: dict[str, Any] = {
    # API settings
    "api_base_url": "https://api.openai.com/v1",
    "model": "gpt-4o-mini",
    "max_tokens": 1000,
    "temperature": 0.7,
    "stream": True,
    "system_prompt": "You are a helpful assistant.",
}

# Config file location
USER_CONFIG_DIR = pathlib.Path.home() / ".config" / "mini-chat"
CONFIG_PROFILES_DIR = USER_CONFIG_DIR / "profiles"
ACTIVE_PROFILE_FILE = USER_CONFIG_DIR / "active_profile.txt"
DEFAULT_PROFILE_NAME = "default"


def ensure_config_dirs() -> None:
    """Ensure the config directories exist."""
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def get_profile_path(profile_name: str) -> pathlib.Path:
    """Get the path to a profile config file."""
    return CONFIG_PROFILES_DIR / f"{profile_name}.yaml"


def get_active_profile() -> str:
    """Get the name of the active profile."""
    if not ACTIVE_PROFILE_FILE.exists():
        # Create with default profile if it doesn't exist
        with ACTIVE_PROFILE_FILE.open("w") as f:
            f.write(DEFAULT_PROFILE_NAME)
        return DEFAULT_PROFILE_NAME

    with ACTIVE_PROFILE_FILE.open() as f:
        profile = f.read().strip()
        return profile if profile else DEFAULT_PROFILE_NAME


def set_active_profile(profile_name: str) -> None:
    """Set the active profile."""
    ensure_config_dirs()
    with ACTIVE_PROFILE_FILE.open("w") as f:
        f.write(profile_name)


def list_available_profiles() -> list[str]:
    """List all available configuration profiles."""
    ensure_config_dirs()
    profiles = []
    for file in CONFIG_PROFILES_DIR.glob("*.yaml"):
        profiles.append(file.stem)

    # Ensure default profile is always available
    if DEFAULT_PROFILE_NAME not in profiles:
        profiles.append(DEFAULT_PROFILE_NAME)

    return sorted(profiles)


def save_config(config: dict[str, Any], profile_name: str | None = None) -> None:
    """Save the configuration to a file."""
    ensure_config_dirs()

    # Use active profile if none specified
    if profile_name is None:
        profile_name = get_active_profile()

    # Don't save API key to config file for security
    save_config = config.copy()
    if "api_key" in save_config:
        del save_config["api_key"]

    # Get the path for this profile
    config_path = get_profile_path(profile_name)

    logger.debug(f"Saving config to {config_path}: {save_config}")
    with config_path.open("w") as f:
        yaml.dump(save_config, f, default_flow_style=False, sort_keys=False)


def clone_profile(source_profile: str, target_profile: str) -> dict[str, Any]:
    """Clone a profile to a new name."""
    config = load_config(source_profile)
    save_config(config, target_profile)
    return config


def load_profile_config(profile_name: str) -> dict[str, Any]:
    """Load a specific profile configuration file."""
    config_path = get_profile_path(profile_name)

    if not config_path.exists():
        logger.debug(f"Profile {profile_name} does not exist, creating with defaults")
        # Create new profile with defaults if it doesn't exist
        save_config(DEFAULT_CONFIG.copy(), profile_name)
        return DEFAULT_CONFIG.copy()

    try:
        with config_path.open() as f:
            user_config = yaml.safe_load(f) or {}
            logger.debug(f"Loaded profile {profile_name}: {user_config}")
            return user_config
    except (OSError, yaml.YAMLError) as e:
        # If the file exists but is invalid, return empty dict
        logger.warning(f"Failed to load profile {profile_name}: {e}")
        return {}


def load_config(profile_name: str | None = None) -> dict[str, Any]:
    """Load configuration from active profile, environment variables, and defaults."""
    # Determine which profile to load
    if profile_name is None:
        profile_name = get_active_profile()

    # Start with defaults
    config = DEFAULT_CONFIG.copy()
    logger.debug(f"Starting with default config: {config}")

    # Override with profile config
    user_config = load_profile_config(profile_name)
    config.update(user_config)
    logger.debug(f"After profile {profile_name} config: {config}")

    # Override with environment variables if present
    if os.environ.get("API_BASE_URL"):
        config["api_base_url"] = os.environ.get("API_BASE_URL")
    if os.environ.get("API_MODEL"):
        config["model"] = os.environ.get("API_MODEL")
    if os.environ.get("API_MAX_TOKENS"):
        config["max_tokens"] = int(os.environ.get("API_MAX_TOKENS", "1000"))
    if os.environ.get("API_TEMPERATURE"):
        config["temperature"] = float(os.environ.get("API_TEMPERATURE", "0.7"))
    if os.environ.get("SYSTEM_PROMPT"):
        config["system_prompt"] = os.environ.get("SYSTEM_PROMPT")

    logger.debug(f"After env vars: {config}")

    # API key is required - check OPENAI_API_KEY first, then fall back to API_KEY
    config["api_key"] = get_api_key() or ""

    return config


def get_api_key() -> str | None:
    """Get API key from environment variables."""
    # First check for OPENAI_API_KEY, then fall back to API_KEY
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY")


def update_config(key: str, value: Any, profile_name: str | None = None) -> dict[str, Any]:
    """Update a config value and save to file."""
    if profile_name is None:
        profile_name = get_active_profile()

    config = load_config(profile_name)
    logger.debug(f"Updating config key '{key}' to '{value}' in profile '{profile_name}'")
    config[key] = value
    save_config(config, profile_name)
    return config


def delete_profile(profile_name: str) -> bool:
    """Delete a profile configuration file."""
    if profile_name == DEFAULT_PROFILE_NAME:
        logger.warning("Cannot delete the default profile")
        return False

    config_path = get_profile_path(profile_name)
    if config_path.exists():
        config_path.unlink()
        logger.debug(f"Deleted profile {profile_name}")

        # If this was the active profile, switch to default
        if get_active_profile() == profile_name:
            set_active_profile(DEFAULT_PROFILE_NAME)

        return True

    return False
