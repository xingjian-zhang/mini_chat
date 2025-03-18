"""Main entry point for the terminal chatbot."""

import signal
import sys
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text

from mini_chat.api import APIError, send_message
from mini_chat.config import (
    DEFAULT_CONFIG,
    DEFAULT_PROFILE_NAME,
    clone_profile,
    delete_profile,
    get_active_profile,
    get_api_key,
    list_available_profiles,
    load_config,
    save_config,
    set_active_profile,
    update_config,
)
from mini_chat.models import Conversation, Message
from mini_chat.ui import (
    create_loading_display,
    display_conversation,
    get_user_input,
    handle_streaming_response,
    show_help,
)

console = Console()


# Set up signal handler for clean exit with Ctrl+C
def signal_handler(sig, frame):
    """Handle keyboard interrupt signal."""
    console.print("\n[bold yellow]Chatbot terminated by user.[/bold yellow]")
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)


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


def show_profiles() -> None:
    """Display available configuration profiles."""
    active_profile = get_active_profile()
    profiles = list_available_profiles()

    table = Table(title="Configuration Profiles")
    table.add_column("Profile", style="bold blue")
    table.add_column("Status", style="green")

    for profile in profiles:
        status = "[bold green]ACTIVE[/bold green]" if profile == active_profile else ""
        table.add_row(profile, status)

    console.print(table)


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
        console.print("[bold yellow]Goodbye![/bold yellow]")
        return False, updated_config
    elif cmd == "/help":
        show_help()
    elif cmd == "/clear":
        conversation.clear()
        console.print("[bold yellow]Conversation cleared.[/bold yellow]")
    elif cmd == "/system":
        if not args:
            # Show current system prompt if no args
            system_msgs = [msg for msg in conversation.messages if msg.role == "system"]
            if system_msgs:
                console.print("[bold]Current system message:[/bold]")
                console.print(system_msgs[0].content)
            else:
                console.print("[bold yellow]No system message set.[/bold yellow]")
        else:
            # Add system message to conversation and save to config
            conversation.add_message("system", args)
            updated_config = update_config("system_prompt", args)
            console.print("[bold yellow]System message updated and saved.[/bold yellow]")
    elif cmd == "/config":
        if not args:
            # Show all config
            show_config(config)
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
            except ValueError:
                console.print(
                    "[bold red]Invalid configuration format. Use: /config key=value[/bold red]"
                )
    elif cmd == "/save":
        save_config(updated_config)
        console.print("[bold green]Configuration saved.[/bold green]")
    elif cmd == "/reset":
        if args == "config":
            # Reset to default config
            updated_config = DEFAULT_CONFIG.copy()
            updated_config["api_key"] = config["api_key"]  # Keep API key
            save_config(updated_config)
            console.print("[bold yellow]Configuration reset to defaults.[/bold yellow]")
        else:
            console.print("[bold red]Unknown reset target. Use: /reset config[/bold red]")
    elif cmd == "/profile":
        if not args:
            # Show current profile and list available profiles
            console.print(f"[bold]Current profile:[/bold] {get_active_profile()}")
            show_profiles()
        else:
            # Profile management commands
            profile_args = args.split()
            subcmd = profile_args[0] if profile_args else ""

            if subcmd == "use" and len(profile_args) > 1:
                # Switch to a different profile
                profile_name = profile_args[1]

                # If profile doesn't exist, create it
                if profile_name not in list_available_profiles():
                    msg = "[yellow]Profile '{}' does not exist. Creating new profile.[/yellow]"
                    console.print(msg.format(profile_name))

                # Set as active profile
                set_active_profile(profile_name)
                updated_config = load_config()

                # Update the conversation with the new system prompt
                for i, msg in enumerate(conversation.messages):
                    if msg.role == "system":
                        conversation.messages[i] = Message(
                            role="system", content=updated_config["system_prompt"]
                        )
                        break
                else:
                    conversation.add_message("system", updated_config["system_prompt"])

                console.print(f"[bold green]Switched to profile: {profile_name}[/bold green]")

            elif subcmd == "list":
                # List all available profiles
                show_profiles()

            elif subcmd == "create" and len(profile_args) > 1:
                # Create a new profile
                profile_name = profile_args[1]

                # Use current config as template if specified
                if len(profile_args) > 2 and profile_args[2] == "--from-current":
                    save_config(config, profile_name)
                else:
                    # Start with defaults
                    save_config(DEFAULT_CONFIG.copy(), profile_name)

                console.print(f"[bold green]Created new profile: {profile_name}[/bold green]")

            elif subcmd == "delete" and len(profile_args) > 1:
                # Delete a profile
                profile_name = profile_args[1]

                if profile_name == DEFAULT_PROFILE_NAME:
                    console.print("[bold red]Cannot delete the default profile.[/bold red]")
                else:
                    if delete_profile(profile_name):
                        console.print(f"[bold green]Deleted profile: {profile_name}[/bold green]")

                        # If this was the active profile, reload config
                        if get_active_profile() == DEFAULT_PROFILE_NAME:
                            updated_config = load_config()
                    else:
                        console.print(
                            f"[bold red]Profile '{profile_name}' does not exist.[/bold red]"
                        )

            elif subcmd == "clone" and len(profile_args) > 2:
                # Clone a profile
                source_profile = profile_args[1]
                target_profile = profile_args[2]

                try:
                    clone_profile(source_profile, target_profile)
                    msg = "[bold green]Cloned profile '{}' to '{}'[/bold green]"
                    console.print(msg.format(source_profile, target_profile))
                except Exception as e:
                    console.print(f"[bold red]Failed to clone profile: {e}[/bold red]")

            else:
                console.print("[bold red]Unknown profile command. Available commands:[/bold red]")
                console.print("  /profile use <name> - Switch to profile")
                console.print("  /profile list - List all profiles")
                console.print("  /profile create <name> [--from-current] - Create new profile")
                console.print("  /profile clone <source> <target> - Clone a profile")
                console.print("  /profile delete <name> - Delete a profile")
    else:
        return True, updated_config  # Not a special command

    return True, updated_config  # Continue running


def main() -> None:
    """Run the main chat loop."""
    # Load configuration
    config = load_config()

    # Check for API key
    if not get_api_key():
        console.print("[bold red]Error: No API key found in environment variables.[/bold red]")
        console.print("Please set your API key using: export OPENAI_API_KEY=your_api_key_here")
        console.print("Or alternatively: export API_KEY=your_api_key_here")
        sys.exit(1)

    # Initialize conversation with system message from config
    conversation = Conversation([Message(role="system", content=config["system_prompt"])])

    console.clear()
    console.print("[bold]Welcome to Terminal Chatbot[/bold]", justify="center")
    active_profile = get_active_profile()
    profile_text = Text(f"Active Profile: {active_profile}", style="bold blue")
    console.print(profile_text)
    console.print("Type /help for available commands or just start chatting!")

    # Main chat loop
    running = True
    while running:
        # Get user input
        user_input = get_user_input()

        # Check for commands
        if user_input.startswith("/"):
            running, config = process_command(user_input, conversation, config)
            continue

        # Add user message to conversation
        conversation.add_message("user", user_input)

        # Show conversation with user's message
        display_conversation(conversation)

        # Create a loading spinner
        progress = create_loading_display()
        progress.add_task("Thinking", total=None)

        # Use a single Live display for both loading and streaming
        try:
            with Live(progress, refresh_per_second=10) as live:
                try:
                    # Add initial empty assistant message
                    conversation.add_message("assistant", "")

                    # Create streaming response handler
                    update_content = handle_streaming_response(conversation, live)

                    # Send message to API with streaming callback
                    send_message(conversation, update_content)

                except APIError as e:
                    console.print(f"[bold red]Error: {e!s}[/bold red]")
                    # Remove the last assistant message if it exists
                    if conversation.messages and conversation.messages[-1].role == "assistant":
                        conversation.messages.pop()
                    continue
                except KeyboardInterrupt:
                    raise  # Re-raise to be caught by the outer try/except
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Chatbot terminated by user.[/bold yellow]")
            sys.exit(0)

        # Refresh display after completion
        display_conversation(conversation)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Chatbot terminated by user.[/bold yellow]")
        sys.exit(0)
