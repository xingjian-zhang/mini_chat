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
