from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class ConsoleKernelContract(ABC):
    @abstractmethod
    def bootstrap(self) -> None:
        """
        Bootstrap the application for console commands.
        """
        pass

    @abstractmethod
    def handle(self, input: Any, output: Any | None = None) -> int:
        """
        Handle an incoming console command.

        Args:
            input: Console input interface.
            output: Console output interface (optional).

        Returns:
            Exit status code.
        """
        pass

    @abstractmethod
    def call(self, command: str, parameters: dict[str, Any] | None = None, output_buffer: Any | None = None) -> int:
        """
        Run a console command by name.

        Args:
            command: Command name to run.
            parameters: Parameters to pass to the command.
            output_buffer: Output buffer (optional).

        Returns:
            Exit status code.
        """
        pass

    @abstractmethod
    def queue(self, command: str, parameters: dict[str, Any] | None = None) -> Any:
        """
        Queue a console command by name.

        Args:
            command: Command name to queue.
            parameters: Parameters to pass to the command.

        Returns:
            Pending dispatch object.
        """
        pass

    @abstractmethod
    def all(self) -> list[Any]:
        """
        Get all of the commands registered with the console.

        Returns:
            List of registered commands.
        """
        pass

    @abstractmethod
    def output(self) -> str:
        """
        Get the output for the last run command.

        Returns:
            Command output as string.
        """
        pass

    @abstractmethod
    def terminate(self, input: Any, status: int) -> None:
        """
        Terminate the application.

        Args:
            input: Console input interface.
            status: Exit status code.
        """
        pass
