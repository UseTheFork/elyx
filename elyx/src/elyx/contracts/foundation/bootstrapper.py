from __future__ import annotations

from abc import ABC, abstractmethod

from elyx.contracts.foundation.application import Application


class Bootstrapper(ABC):
    """Base class for application bootstrappers."""

    def __init__(self, **kwargs):
        """Initialize the bootstrapper."""
        pass

    @abstractmethod
    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap the application.

        Args:
            app: The application instance.
        """
        pass
