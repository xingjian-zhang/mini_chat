# Mini-Chat Application Architecture

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

## Component Responsibilities

### `__main__.py`
- Main entry point for the application
- Application loop management
- High-level orchestration

### `api.py`
- Handles communication with the AI API
- Manages streaming and non-streaming requests
- Error handling for API communication

### `cli.py`
- Processes command-line commands
- Command handler functions
- Command-specific UI displays

### `config.py`
- Configuration loading/saving
- Profile management
- Environment variable handling

### `models.py`
- Data structures for the application
- Conversation and Message models

### `ui.py`
- UI component rendering
- User input handling
- Message display formatting

### `utils.py`
- Common utility functions
- Signal handling
- Progress display helpers

## Data Flow

1. User enters input in the terminal
2. The `__main__.py` processes the input
   - If it's a command, `cli.py` handles it
   - If it's a message, it's added to the conversation
3. For messages:
   - The conversation is sent to the API via `api.py`
   - The response is streamed back and displayed using `ui.py`
4. The application loop continues until exit

## Configuration Management

- Configuration is stored in YAML files in `~/.config/mini-chat/profiles/`
- Multiple profiles can be created and switched between
- API keys are sourced from environment variables, not stored in files

## User Interface

- Built with the Rich library for enhanced terminal UI
- Supports markdown rendering for assistant responses
- Uses spinners and progress indicators for loading states
- Live updating of streaming responses
