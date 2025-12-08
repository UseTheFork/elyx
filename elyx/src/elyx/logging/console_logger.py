
from rich.console import Console

from elyx.contracts.logging.logger import Logger


class ConsoleLogger(Logger):
    """Logger that outputs to the console using Rich."""

    def __init__(self, config: dict):
        """
        Initialize the console logger.

        Args:
            config: Logger configuration dictionary.
        """
        self.config = config
        self.console = Console(stderr=True)
        self.level = config.get("level", "debug")

    def emergency(self, message: str, context: dict | None = None) -> None:
        """Log an emergency message."""
        self.console.print(f"[bold red]EMERGENCY[/bold red]: {message}")

    def alert(self, message: str, context: dict | None = None) -> None:
        """Log an alert message."""
        self.console.print(f"[bold red]ALERT[/bold red]: {message}")

    def critical(self, message: str, context: dict | None = None) -> None:
        """Log a critical message."""
        self.console.print(f"[red]CRITICAL[/red]: {message}")

    def error(self, message: str, context: dict | None = None) -> None:
        """Log an error message."""
        self.console.print(f"[red]ERROR[/red]: {message}")

    def warning(self, message: str, context: dict | None = None) -> None:
        """Log a warning message."""
        self.console.print(f"[yellow]WARNING[/yellow]: {message}")

    def notice(self, message: str, context: dict | None = None) -> None:
        """Log a notice message."""
        self.console.print(f"[cyan]NOTICE[/cyan]: {message}")

    def info(self, message: str, context: dict | None = None) -> None:
        """Log an info message."""
        self.console.print(f"[blue]INFO[/blue]: {message}")

    def debug(self, message: str, context: dict | None = None) -> None:
        """Log a debug message."""
        self.console.print(f"[dim]DEBUG[/dim]: {message}")
