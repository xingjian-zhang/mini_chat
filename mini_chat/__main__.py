"""Main entry point for the terminal chatbot."""

import sys

from rich.console import Console
from rich.live import Live

from mini_chat.api import APIError, send_message
from mini_chat.cli import process_command
from mini_chat.config import load_config
from mini_chat.models import Conversation
from mini_chat.ui import (
    create_loading_display,
    display_conversation,
    get_user_input,
    handle_streaming_response,
)
from mini_chat.utils import setup_signal_handler

console = Console()


def main() -> None:
    """Run the terminal chatbot."""
    # Set up signal handler
    setup_signal_handler()

    # Initialize config and conversation
    config = load_config()
    conversation = Conversation(messages=[])

    # Add system message from config
    system_prompt = config.get("system_prompt", "You are a helpful assistant.")
    conversation.add_message("system", system_prompt)

    # Main interaction loop
    continue_running = True
    while continue_running:
        # Display conversation
        display_conversation(conversation)

        # Get user input
        user_input = get_user_input()

        # Handle commands
        if user_input.startswith("/"):
            continue_running, config = process_command(user_input, conversation, config)
            continue

        # Add user message
        conversation.add_message("user", user_input)

        # Add empty assistant message (will be filled in with the response)
        conversation.add_message("assistant", "")

        # Create a Live display for the assistant's response with loading spinner
        with Live(console=console, refresh_per_second=10) as live, create_loading_display() as _:
            try:
                # Send message with streaming updates
                content_callback = handle_streaming_response(conversation, live)
                send_message(conversation, content_callback)
            except APIError as e:
                # Show error and revert assistant message on failure
                conversation.messages.pop()  # Remove assistant message
                console.print(f"[bold red]API Error: {e}[/bold red]")
                input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]mini-chat terminated by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
        sys.exit(1)
