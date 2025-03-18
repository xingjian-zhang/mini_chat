"""Tests for the config module."""

import os
import pathlib
import tempfile
from unittest.mock import patch

import pytest
import yaml

from mini_chat.config import (
    DEFAULT_CONFIG,
    ensure_config_dirs,
    get_active_profile,
    get_api_key,
    get_profile_path,
    load_config,
)


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)
        with (
            patch("mini_chat.config.USER_CONFIG_DIR", tmp_path),
            patch("mini_chat.config.CONFIG_PROFILES_DIR", tmp_path / "profiles"),
            patch("mini_chat.config.ACTIVE_PROFILE_FILE", tmp_path / "active_profile.txt"),
        ):
            yield tmp_path


def test_ensure_config_dirs(temp_config_dir):
    """Test that config directories are created."""
    profiles_dir = temp_config_dir / "profiles"

    ensure_config_dirs()

    assert temp_config_dir.exists()
    assert profiles_dir.exists()


def test_get_profile_path():
    """Test getting a profile path."""
    path = get_profile_path("test_profile")
    assert path.name == "test_profile.yaml"
    assert "profiles" in str(path)


def test_get_active_profile(temp_config_dir):
    """Test getting the active profile."""
    # First call should create the file with default profile
    profile = get_active_profile()
    assert profile == "default"

    # File should exist now
    active_profile_file = temp_config_dir / "active_profile.txt"
    assert active_profile_file.exists()

    # Content should be the default profile name
    assert active_profile_file.read_text().strip() == "default"


def test_load_config_default(temp_config_dir):
    """Test loading the default config."""
    config = load_config()
    # Remove the API key for comparison with DEFAULT_CONFIG since it's added in load_config()
    if "api_key" in config:
        del config["api_key"]
    assert config == DEFAULT_CONFIG


def test_load_config_with_profile(temp_config_dir):
    """Test loading a profile config."""
    # Create a test profile config
    profiles_dir = temp_config_dir / "profiles"
    profiles_dir.mkdir(exist_ok=True)

    test_config = DEFAULT_CONFIG.copy()
    test_config["model"] = "test-model"

    with (profiles_dir / "test_profile.yaml").open("w") as f:
        yaml.dump(test_config, f)

    # Load the test profile
    with patch("mini_chat.config.get_active_profile", return_value="test_profile"):
        config = load_config()
        assert config["model"] == "test-model"


@patch.dict(os.environ, {"API_KEY": "test-api-key"}, clear=True)
def test_get_api_key_from_env():
    """Test getting API key from environment variable."""
    api_key = get_api_key()
    assert api_key == "test-api-key"


@patch.dict(os.environ, {}, clear=True)
def test_get_api_key_missing():
    """Test behavior when API key is missing."""
    api_key = get_api_key()
    assert api_key is None
