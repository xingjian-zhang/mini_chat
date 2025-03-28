# mini-chat 🐜

A minimal terminal-based chatbot using Rich for UI and direct HTTP requests for API communication.

![image](assets/image.png)

## Features

- 🎨 Rich terminal UI with syntax highlighting
- ✨ Markdown support and streaming responses
- ⚙️ Profile and configuration management
- 🪶 Extremely lightweight

## Installation

```bash
# Development setup
git clone https://github.com/xingjian-zhang/mini_chat.git
cd mini_chat
uv venv && uv pip install -e ".[dev]"
```

Set your API key using OpenAI's standard environment variable:
```bash
export OPENAI_API_KEY=your_key_here
```

## Configure Profiles

The chatbot supports multiple configuration profiles, allowing you to save different settings for different use cases. Profiles are stored as YAML files in the `~/.config/mini-chat/profiles/` directory.

Profiles are managed by directly editing the YAML files:
- Each profile is stored as a separate `<profile_name>.yaml` file
- The active profile is specified in `~/.config/mini-chat/active_profile.txt`
- The default profile is used if none is specified

You can switch between profiles within the application using:
```
/profile use <profile_name>
```

## Usage

Run with `mini-chat` or `mc`

### Basic Commands

- Type normally to chat with the AI
- `/help` - Show help
- `/clear` - Clear conversation
- `/exit` - Exit
- `/system <msg>` - Add system instructions
- `/config` - View/change settings
- `/profile use <name>` - Switch between profiles

## Project Structure

```
mini_chat/
├── __init__.py      # Package initialization
├── __main__.py      # Application entry point
├── api.py           # API communication layer
├── cli.py           # Command-line interface handling
├── config.py        # Configuration management
├── models.py        # Data models
├── ui.py            # User interface components
└── utils.py         # Utility functions
```

## Development

```bash
# Lint and format
ruff check . --fix
ruff format .

# Run tests
pytest
```

See architecture.md for project structure details.

## Roadmap

- [ ] Support for additional LLM providers beyond OpenAI
- [ ] Conversation history management and persistence
- [ ] File attachment and context upload capabilities
- [ ] Custom themes and UI configurations
- [ ] MCP
