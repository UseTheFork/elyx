from abc import ABC, abstractmethod


class ServiceProvider(ABC):
    """Base contract for service providers."""

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
