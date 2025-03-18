# Terminal Chatbot

A simple terminal-based chatbot using the Rich library for UI and direct HTTP requests for API communication.

## Features

- Rich terminal UI with colored message panels
- Markdown rendering for assistant responses
- Streaming responses from the AI
- Loading indicators during API calls
- Command system with /help, /clear, /exit, and /system commands
- Proper error handling for API requests
- Configuration management with environment variables
- Modular design with separation of concerns

## Installation

### Development Installation

1. Clone the repository and change into the directory:

```bash
git clone https://github.com/yourusername/mini-chat.git
cd mini-chat
```

2. Create a virtual environment and install the development dependencies:

```bash
# Using uv (recommended)
uv venv
uv pip install -e ".[dev]"

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate     # On Windows
pip install -e ".[dev]"
```

### Regular Installation

```bash
pip install git+https://github.com/yourusername/mini-chat.git
```

## Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

You can also configure settings using the built-in configuration system while the chatbot is running. The chatbot now supports multiple configuration profiles in YAML format.

### Configuration Profiles

The chatbot now supports multiple configuration profiles, allowing you to save different settings for different use cases. Profiles are stored as YAML files in the `~/.mini_chat/profiles/` directory.

You can:
- Create multiple named profiles
- Switch between profiles during a session
- Clone existing profiles
- Delete profiles

All configuration changes are saved per-profile, making it easy to maintain different setups for different tasks.

### Other Configuration Options

These environment variables can override settings in the active profile:
- `API_BASE_URL`: The base URL for the API (default: `https://api.openai.com/v1`)
- `API_MODEL`: The model to use (default: `gpt-3.5-turbo`)
- `API_MAX_TOKENS`: Maximum tokens in the response (default: `1000`)
- `API_TEMPERATURE`: Temperature setting (default: `0.7`)

## Usage

Run the chatbot:

```bash
# Using the full command
mini-chat

# Or using the shorter alias
mc

# Or from the repository
python -m mini_chat
```

### Commands

- `/help` - Display help information
- `/clear` - Clear the conversation
- `/exit` - Exit the chatbot
- `/system <message>` - Add a system message (instructions)
- `/config` - View current configuration
- `/config key=value` - Set a configuration value
- `/save` - Save configuration changes
- `/reset config` - Reset to default configuration

### Profile Management Commands

- `/profile` - Show current profile and list all profiles
- `/profile use <name>` - Switch to a different profile
- `/profile list` - List all available profiles
- `/profile create <name>` - Create a new profile with default settings
- `/profile create <name> --from-current` - Create a new profile from current settings
- `/profile clone <src> <dest>` - Clone an existing profile to a new one
- `/profile delete <name>` - Delete a profile

Just type normally to chat with the AI assistant.

## Development

### Linting and Formatting

Run linting:

```bash
ruff check .
```

Apply automatic fixes:

```bash
ruff check --fix .
```

Format code:

```bash
ruff format .
```

### Pre-commit Hooks

This project uses pre-commit to run checks before each commit. To set up:

```bash
# Install pre-commit
uv pip install pre-commit

# Install the git hooks
pre-commit install
```

Now, ruff checks will run automatically before each commit, ensuring code quality.
