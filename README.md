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

Other optional configuration variables:
- `API_BASE_URL`: The base URL for the API (default: `https://api.openai.com/v1`)
- `API_MODEL`: The model to use (default: `gpt-3.5-turbo`)
- `API_MAX_TOKENS`: Maximum tokens in the response (default: `1000`)
- `API_TEMPERATURE`: Temperature setting (default: `0.7`)

## Usage

Run the chatbot:

```bash
# If installed as a package
mini-chat

# Or from the repository
python -m mini_chat
```

### Commands

- `/help` - Display help information
- `/clear` - Clear the conversation
- `/exit` - Exit the chatbot
- `/system <message>` - Add a system message (instructions)

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
