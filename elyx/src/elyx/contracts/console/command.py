from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from elyx.container import Container
    from elyx.foundation import Application


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
