
from abc import ABC, abstractmethod


class Logger(ABC):
    """Logger contract defining standard logging interface."""

    @abstractmethod
    def emergency(self, message: str, context: dict | None = None) -> None:
        """Log an emergency message."""
        pass

    @abstractmethod
    def alert(self, message: str, context: dict | None = None) -> None:
        """Log an alert message."""
        pass

    @abstractmethod
    def critical(self, message: str, context: dict | None = None) -> None:
        """Log a critical message."""
        pass

    @abstractmethod
    def error(self, message: str, context: dict | None = None) -> None:
        """Log an error message."""
        pass

    @abstractmethod
    def warning(self, message: str, context: dict | None = None) -> None:
        """Log a warning message."""
        pass

    @abstractmethod
    def notice(self, message: str, context: dict | None = None) -> None:
        """Log a notice message."""
        pass

    @abstractmethod
    def info(self, message: str, context: dict | None = None) -> None:
        """Log an info message."""
        pass

    @abstractmethod
    def debug(self, message: str, context: dict | None = None) -> None:
        """Log a debug message."""
        pass
