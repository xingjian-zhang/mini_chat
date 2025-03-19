"""Command-line interface for the terminal chatbot."""

from typing import Any

from rich.console import Console
from rich.table import Table

from mini_chat.config import (
    DEFAULT_CONFIG,
    get_active_profile,
    list_available_profiles,
    load_config,
    save_config,
    set_active_profile,
    update_config,
)
from mini_chat.models import Conversation, Message
from mini_chat.ui import show_help
from mini_chat.utils import pause_after

console = Console()


@pause_after
def show_config(config: dict[str, Any]) -> None:
    """Display the current configuration."""
    active_profile = get_active_profile()

    table = Table(title=f"Configuration: [bold]{active_profile}[/bold] profile")
    table.add_column("Setting", style="bold blue")
    table.add_column("Value", style="green")

    # Sort keys for consistent display
    for key in sorted(config.keys()):
        if key != "api_key":  # Don't show API key
            value = str(config[key])
            # Truncate long values (e.g., system prompt)
            if len(value) > 50:
                value = value[:47] + "..."
            table.add_row(key, value)

    console.print(table)


@pause_after
def show_system_message(conversation: Conversation) -> None:
    """Display the current system message."""
    system_msgs = [msg for msg in conversation.messages if msg.role == "system"]
    if system_msgs:
        console.print("[bold]Current system message:[/bold]")
        console.print(system_msgs[0].content)
    else:
        console.print("[bold yellow]No system message set.[/bold yellow]")


def handle_system_command(
    args: str, conversation: Conversation, config: dict[str, Any]
) -> dict[str, Any]:
    """Handle the /system command."""
    if not args:
        # Show current system prompt if no args
        show_system_message(conversation)
        return config
    else:
        # Add system message to conversation and save to config
        conversation.add_message("system", args)
        updated_config = update_config("system_prompt", args)
        console.print("[bold yellow]System message updated and saved.[/bold yellow]")
        return updated_config


def handle_config_command(
    args: str, conversation: Conversation, config: dict[str, Any]
) -> dict[str, Any]:
    """Handle the /config command."""
    if not args:
        # Show all config
        show_config(config)
        return config
    else:
        # Process setting a config value
        try:
            key, value = args.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Convert value to appropriate type based on default
            if key in DEFAULT_CONFIG:
                default_value = DEFAULT_CONFIG[key]
                if isinstance(default_value, bool):
                    value = value.lower() in ("true", "yes", "1", "y")
                elif isinstance(default_value, int):
                    value = int(value)
                elif isinstance(default_value, float):
                    value = float(value)

            # Update the config and get the updated version
            updated_config = update_config(key, value)
            console.print(f"[bold green]Updated {key} to {value}[/bold green]")

            # Special handling for system_prompt
            if key == "system_prompt":
                # Update the system message in the conversation
                for i, msg in enumerate(conversation.messages):
                    if msg.role == "system":
                        conversation.messages[i] = Message(role="system", content=value)
                        break
                else:
                    conversation.add_message("system", value)

            return updated_config
        except ValueError:
            console.print(
                "[bold red]Invalid configuration format. Use: /config key=value[/bold red]"
            )
            return config


def handle_reset_command(args: str, config: dict[str, Any]) -> dict[str, Any]:
    """Handle the /reset command."""
    if args == "config":
        # Reset to default config
        updated_config = DEFAULT_CONFIG.copy()
        updated_config["api_key"] = config["api_key"]  # Keep API key
        save_config(updated_config)
        with pause_after():
            console.print("[bold yellow]Configuration reset to defaults.[/bold yellow]")
        return updated_config
    else:
        with pause_after():
            console.print("[bold red]Unknown reset target. Use: /reset config[/bold red]")
        return config


def handle_profile_command(
    args: str, conversation: Conversation, config: dict[str, Any]
) -> dict[str, Any]:
    """Handle the /profile command."""
    if not args:
        # Show current profile using context manager
        with pause_after():
            console.print(f"[bold]Current profile:[/bold] {get_active_profile()}")
            console.print(
                "[italic]Profiles can be managed manually by editing files in "
                "~/.config/mini-chat/profiles/[/italic]"
            )
        return config
    else:
        # Profile switching commands
        profile_args = args.split()
        subcmd = profile_args[0] if profile_args else ""

        if subcmd == "use" and len(profile_args) > 1:
            # Switch to a different profile
            profile_name = profile_args[1]
            profiles = list_available_profiles()

            if profile_name not in profiles:
                with pause_after():
                    console.print(f"[bold red]Profile '{profile_name}' does not exist.[/bold red]")
                    console.print(f"[italic]Available profiles: {', '.join(profiles)}[/italic]")
                return config

            # Set as active profile
            set_active_profile(profile_name)
            updated_config = load_config()

            # Start a new session with the new system prompt
            conversation.messages.clear()
            conversation.add_message("system", updated_config["system_prompt"])

            console.print(f"[bold green]Switched to profile: {profile_name}[/bold green]")
            return updated_config
        else:
            console.print(
                "[bold red]Unknown profile command. Use: /profile use <profile_name>[/bold red]"
            )
            return config


def process_command(
    command: str, conversation: Conversation, config: dict[str, Any]
) -> tuple[bool, dict[str, Any]]:
    """
    Process special commands.

    Returns:
        Tuple of (continue_running, updated_config)
        - continue_running: True if the app should continue running, False to exit
        - updated_config: The updated configuration (may be the same as input if no changes)
    """
    # Split command and arguments
    parts = command.split(" ", 1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    # Start with the current config
    updated_config = config.copy()

    if cmd == "/exit":
        console.print("[bold yellow]mini-chat exiting...[/bold yellow]")
        return False, updated_config
    elif cmd == "/help":
        show_help()
    elif cmd == "/clear":
        conversation.clear()
        console.print("[bold yellow]Conversation cleared.[/bold yellow]")
    elif cmd == "/system":
        updated_config = handle_system_command(args, conversation, config)
    elif cmd == "/config":
        updated_config = handle_config_command(args, conversation, config)
    elif cmd == "/save":
        save_config(updated_config)
        console.print("[bold green]Configuration saved.[/bold green]")
    elif cmd == "/reset":
        updated_config = handle_reset_command(args, config)
    elif cmd == "/profile":
        updated_config = handle_profile_command(args, conversation, config)
    else:
        console.print(f"[bold red]Unknown command: {cmd}[/bold red]")
        console.print("Type /help for a list of commands.")

    return True, updated_config
