from abc import ABC, abstractmethod
from typing import Any


class ApplicationContract(ABC):
    @abstractmethod
    def call(self, command: str, parameters: dict[str, Any] | None = None, output_buffer: Any | None = None) -> int:
        """
        Run an Artisan console command by name.

        Args:
            command: The command name to run.
            parameters: Parameters to pass to the command.
            output_buffer: Optional output buffer for capturing command output.

        Returns:
            Exit status code (0 for success, non-zero for error).
        """
        pass

    @abstractmethod
    def output(self) -> str:
        """
        Get the output from the last command.

        Returns:
            Command output as a string.
        """
        pass
