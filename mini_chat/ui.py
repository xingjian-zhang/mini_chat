"""UI components for the terminal chatbot."""

from collections.abc import Callable

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.text import Text

from mini_chat.models import Conversation, Message

console = Console()


def create_message_panel(message: Message) -> Panel:
    """Create a panel to display a message."""
    style = "green" if message.role == "assistant" else "blue"

    # Use Markdown for assistant messages, plain text for user
    content = Markdown(message.content) if message.role == "assistant" else Text(message.content)

    return Panel(
        content, title=f"[bold]{message.role.capitalize()}[/bold]", border_style=style, expand=False
    )


def display_conversation(conversation: Conversation) -> None:
    """Display the entire conversation."""
    console.clear()
    console.print("[bold]Terminal Chatbot[/bold]", justify="center")

    for message in conversation.messages:
        if message.role != "system":  # Don't show system messages
            console.print(create_message_panel(message))

    console.print("Type your message below. Use /help for commands.")


def get_user_input() -> str:
    """Get input from the user."""
    return Prompt.ask("[bold blue]You[/bold blue]")


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
    panel = create_message_panel(message)

    # Initially update the live display with the panel
    live.update(panel)

    # Return a function that updates the content
    def update_content(new_content: str) -> None:
        message.content += new_content
        live.update(create_message_panel(message))

    return update_content


def show_help() -> None:
    """Display help information."""
    help_text = """
    [bold]Terminal Chatbot Commands:[/bold]

    /help    - Display this help message
    /clear   - Clear the conversation
    /exit    - Exit the chatbot
    /system  - Add a system message (instructions)

    Just type normally to chat with the AI assistant.
    """
    console.print(Panel(help_text, title="Help", border_style="yellow"))
