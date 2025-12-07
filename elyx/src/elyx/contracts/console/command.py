from abc import ABC, abstractmethod

from elyx.contracts.console.application import Application
from elyx.contracts.container.container import Container


class Command(ABC):
    @classmethod
    @abstractmethod
    def get_command_name(cls) -> str:
        """Extract command name from signature without instantiation."""
        pass

    @abstractmethod
    def get_elyx(self) -> Container:
        """Get the Elyx console application instance."""
        pass

    @abstractmethod
    def set_elyx(self, elyx: Container) -> None:
        """Set the Elyx application instance."""
        pass

    @abstractmethod
    def get_application(self) -> Application:
        """Get the application container instance."""
        pass

    @abstractmethod
    def set_application(self, application: Application) -> None:
        """Set the application container instance."""
        pass
