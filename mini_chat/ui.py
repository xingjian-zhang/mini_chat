"""UI components for the terminal chatbot."""

import sys
from collections.abc import Callable, Generator
from contextlib import contextmanager

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from mini_chat.models import Conversation, Message

console = Console()


def create_message_display(message: Message) -> Text | Markdown:
    """Create formatted text for message display."""
    if message.role == "assistant":
        # Use Markdown for assistant messages
        content = Markdown(message.content)
    else:
        # Use plain text with styling for user
        content = Text(message.content)
        if message.role == "user":
            content.stylize("blue")

    return content


def display_conversation(conversation: Conversation) -> None:
    """Display the entire conversation."""
    console.clear()
    console.print("[bold]Terminal Chatbot[/bold]", justify="center")

    for message in conversation.messages:
        if message.role != "system":  # Don't show system messages
            # Use consistent capitalization (User/Assistant)
            display_role = "Assistant" if message.role == "assistant" else "User"
            role_text = Text(f"{display_role}: ", style="bold")
            if message.role == "assistant":
                role_text.stylize("green")
            else:
                role_text.stylize("blue")

            console.print(role_text)
            console.print(create_message_display(message))
            console.print("")  # Empty line between messages

    console.print("Type your message below. Use /help for commands.", style="dim")


def get_user_input() -> str:
    """Get input from the user."""
    try:
        # Create a consistent prompt that matches conversation display
        role_text = Text("User: ", style="bold blue")
        console.print(role_text)
        return console.input()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Chatbot terminated by user.[/bold yellow]")
        sys.exit(0)


@contextmanager
def create_loading_display(message: str = "Thinking") -> Generator[Progress, None, None]:
    """Create a loading spinner display with context manager support."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold green]{task.description}[/bold green]"),
        transient=True,
    )
    _ = progress.add_task(message, total=None)

    try:
        yield progress
    finally:
        progress.stop()


def handle_streaming_response(conversation: Conversation, live: Live) -> Callable[[str], None]:
    """Create a handler for streaming response that updates the given Live display.

    Args:
        conversation: The conversation containing the messages
        live: The Live display to update

    Returns:
        A callback function that updates the display with new content
    """
    # Get the last message (the assistant's response)
    message = conversation.messages[-1]
    content = create_message_display(message)

    # Initially update the live display with the content
    live.update(content)

    # Return a function that updates the content
    def update_content(new_content: str) -> None:
        # Update the actual message object's content
        conversation.messages[-1].content += new_content
        # Update the display with the new content
        live.update(create_message_display(conversation.messages[-1]))

    return update_content


def show_help() -> None:
    """Display help information."""
    table = Table(title="Available Commands")
    table.add_column("Command", style="bold blue")
    table.add_column("Description", style="green")

    # Basic commands
    table.add_row("/help", "Show this help message")
    table.add_row("/clear", "Clear the conversation history")
    table.add_row("/exit", "Exit the chatbot")

    # System prompt commands
    table.add_row("/system <text>", "Set the system message")
    table.add_row("/system", "Show current system message")

    # Configuration commands
    table.add_row("/config key=value", "Set a configuration value")
    table.add_row("/config", "Show all configuration values")
    table.add_row("/save", "Save current configuration")
    table.add_row("/reset config", "Reset configuration to defaults")

    # Profile management commands
    table.add_row("/profile", "Show current profile and list all profiles")
    table.add_row("/profile use <n>", "Switch to a different profile")
    table.add_row("/profile list", "List all available profiles")
    table.add_row("/profile create <n>", "Create a new profile with default settings")
    table.add_row(
        "/profile create <n> --from-current", "Create a new profile from current settings"
    )
    table.add_row("/profile clone <src> <dest>", "Clone an existing profile to a new one")
    table.add_row("/profile delete <n>", "Delete a profile")

    console.print(table)
