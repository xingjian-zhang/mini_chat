# Terminal Chatbot

A simple terminal-based chatbot using the Rich library for UI and direct HTTP requests for API communication.

## Setup

1. Create a virtual environment and install dependencies using `uv`:

```
# Install uv if you don't have it yet
pip install uv

# Create a virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt
```

2. Set your OpenAI API key:

```
export OPENAI_API_KEY=your_openai_api_key_here
```

3. Run the chatbot:

```
# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate     # On Windows

# Run the chatbot
python main.py
```

## Commands

- `/help` - Display help information
- `/clear` - Clear the conversation
- `/exit` - Exit the chatbot
- `/system <message>` - Add a system message (instructions)

Just type normally to chat with the AI assistant. 