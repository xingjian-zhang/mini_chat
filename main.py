"""Main entry point for the terminal chatbot."""
import os
import sys
from typing import List, Dict, Any

from rich.console import Console
from rich.live import Live

from models import Conversation, Message
from ui import (display_conversation, get_user_input, handle_streaming_response, 
               create_loading_display, show_help)
from api import send_message, APIError
from config import load_config, get_api_key

console = Console()

def process_command(command: str, conversation: Conversation) -> bool:
    """
    Process special commands.

    Returns:
        True if the app should continue running, False to exit
    """
    if command == "/exit":
        console.print("[bold yellow]Goodbye![/bold yellow]")
        return False
    elif command == "/help":
        show_help()
    elif command == "/clear":
        conversation.clear()
        console.print("[bold yellow]Conversation cleared.[/bold yellow]")
    elif command.startswith("/system "):
        system_message = command[8:].strip()
        conversation.add_message("system", system_message)
        console.print("[bold yellow]System message added.[/bold yellow]")
    else:
        return True  # Not a special command
    
    return True  # Continue running

def main() -> None:
    """Run the main chat loop."""
    # Initialize
    config = load_config()
    
    # Check for API key
    if not get_api_key():
        console.print("[bold red]Error: No API key found in environment variables.[/bold red]")
        console.print("Please set your API key using: export OPENAI_API_KEY=your_api_key_here")
        console.print("Or alternatively: export API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Initialize conversation with a default system message
    conversation = Conversation([
        Message(role="system", content="You are a helpful assistant. Format your responses using Markdown. Use headings, lists, code blocks with syntax highlighting, and other Markdown features to structure your responses effectively.")
    ])
    
    console.clear()
    console.print("[bold]Welcome to Terminal Chatbot[/bold]", justify="center")
    console.print("Type /help for available commands or just start chatting!")
    
    # Main chat loop
    running = True
    while running:
        # Get user input
        user_input = get_user_input()
        
        # Check for commands
        if user_input.startswith("/"):
            running = process_command(user_input, conversation)
            continue
        
        # Add user message to conversation
        conversation.add_message("user", user_input)
        
        # Show conversation with user's message
        display_conversation(conversation)
        
        # Create a loading spinner
        progress = create_loading_display()
        task = progress.add_task("Thinking", total=None)
        
        # Use a single Live display for both loading and streaming
        with Live(progress, refresh_per_second=10) as live:
            try:
                # Add initial empty assistant message
                conversation.add_message("assistant", "")
                
                # Create streaming response handler
                update_content = handle_streaming_response(conversation, live)
                
                # Send message to API with streaming callback
                send_message(conversation, update_content)
                
            except APIError as e:
                console.print(f"[bold red]Error: {str(e)}[/bold red]")
                # Remove the last assistant message if it exists
                if conversation.messages and conversation.messages[-1].role == "assistant":
                    conversation.messages.pop()
                continue
        
        # Refresh display after completion
        display_conversation(conversation)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Chatbot terminated by user.[/bold yellow]")
        sys.exit(0) 