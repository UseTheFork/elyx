from abc import ABC, abstractmethod

from elyx.foundation.application import Application


class ServiceProvider(ABC):
    """Base class for service providers."""

    def __init__(self, app: Application):
        self.app = app

    @abstractmethod
    def register(self) -> None:
        """
        Register services in the container.
        """
        pass

    def boot(self) -> None:
        """
        Bootstrap services (called after all providers are registered).
        """
        pass
