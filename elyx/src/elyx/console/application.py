
import sys
from typing import Any

from elyx.contracts.console.application_contract import ApplicationContract
from elyx.contracts.container_contract import ContainerContract


class Application(ApplicationContract):
    """Console application for handling command execution."""

    def __init__(self, elyx: ContainerContract):
        """
        Initialize the console application.
        
        Args:
            elyx: The application container instance.
        """
        self.elyx = elyx
        self._commands = {}
        self._output = ""

    def __call__(self, command: str, parameters: dict[str, Any] | None = None, output_buffer: Any | None = None) -> int:
        """
        Run a console command by name.

        Args:
            command: The command name to run.
            parameters: Parameters to pass to the command.
            output_buffer: Optional output buffer for capturing command output.

        Returns:
            Exit status code (0 for success, non-zero for error).
        """
        if parameters is None:
            parameters = {}

        # Check if command exists
        if command not in self._commands:
            self._output = f"Command '{command}' not found."
            return 1

        try:
            # Resolve the command from container
            command_class = self._commands[command]
            command_instance = self.elyx.make(command_class)
            
            # Execute the command
            result = command_instance.handle(**parameters)
            
            # Capture output if buffer provided
            if output_buffer is not None:
                self._output = str(result) if result is not None else ""
            
            return 0
        except Exception as e:
            self._output = f"Error executing command: {str(e)}"
            return 1

    def output(self) -> str:
        """
        Get the output from the last command.

        Returns:
            Command output as a string.
        """
        return self._output

    def register(self, name: str, command: type) -> None:
        """
        Register a command with the application.
        
        Args:
            name: The command name.
            command: The command class.
        """
        self._commands[name] = command

    def run(self) -> int:
        """
        Run the console application with command line arguments.
        
        Returns:
            Exit status code.
        """
        args = sys.argv[1:]
        
        if not args:
            self._print_available_commands()
            return 0
        
        command_name = args[0]
        # Parse remaining args as parameters (simple implementation)
        parameters = {}
        
        return self(command_name, parameters)

    def _print_available_commands(self) -> None:
        """Print available commands."""
        print("Available commands:")
        for name in self._commands.keys():
            print(f"  {name}")
