"""Utility functions for the terminal chatbot."""

import signal
import sys
from typing import Any

from rich.console import Console
from rich.progress import Progress

console = Console()


def setup_signal_handler() -> None:
    """Set up signal handler for clean exit with Ctrl+C."""

    def signal_handler(sig: int, frame: Any) -> None:
        """Handle keyboard interrupt signal."""
        console.print("\n[bold yellow]mini-chat terminated by user.[/bold yellow]")
        sys.exit(0)

    # Only register in non-test environments
    # pytest and unittest use KeyboardInterrupt for control flow
    if "pytest" not in sys.modules:
        # Register the signal handler
        signal.signal(signal.SIGINT, signal_handler)


def create_progress_bar(desc: str) -> Progress:
    """Create a progress bar with the given description."""
    progress = Progress()
    _ = progress.add_task(desc, total=None)
    return progress


class PauseAfter:
    """Context manager and decorator that pauses execution and waits for user input.

    Can be used either as a decorator:

    @pause_after
    def my_function():
        # Function code here
        print("This function will pause after execution")

    Or as a context manager:

    with pause_after():
        # Block of code here
        print("This block will pause after execution")
    """

    def __init__(self, func=None):
        """Initialize as either a decorator or context manager."""
        self.func = func

    def __call__(self, *args, **kwargs):
        """Called when used as a decorator."""
        if self.func is None:
            # Being called with a function argument
            self.func = args[0]
            return self

        # Execute the wrapped function
        result = self.func(*args, **kwargs)
        self._pause()
        return result

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and pause."""
        self._pause()
        # Don't suppress exceptions
        return False

    def _pause(self):
        """Common pause functionality."""
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()


# For backward compatibility and to maintain the decorator syntax
pause_after = PauseAfter
