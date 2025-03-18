"""UI components for the terminal chatbot."""

import sys
from collections.abc import Callable

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
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


def create_loading_display(message: str = "Thinking") -> Progress:
    """Create a loading spinner display."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold green]{task.description}[/bold green]"),
        transient=True,
    )


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
        message.content += new_content
        live.update(create_message_display(message))

    return update_content


def show_help() -> None:
    """Display help information."""
    console.print("[bold]Terminal Chatbot Commands:[/bold]")
    console.print("")
    console.print("  /help    - Display this help message")
    console.print("  /clear   - Clear the conversation")
    console.print("  /exit    - Exit the chatbot")
    console.print("  /system  - Add a system message (instructions)")
    console.print("")
    console.print("Just type normally to chat with the AI assistant.")
