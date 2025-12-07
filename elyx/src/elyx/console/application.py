from typing import Any

from elyx.console.console import Console
from elyx.console.container_command_loader import ContainerCommandLoader
from elyx.contracts.console.application import Application as ApplicationContract
from elyx.contracts.console.command import Command
from elyx.contracts.container.container import Container


class Application(ApplicationContract):
    """Console application for handling command execution."""

    bootstrappers: list = []

    def __init__(self, elyx: Container):
        """
        Initialize the console application.

        Args:
            elyx: The application container instance.
        """
        self.elyx = elyx
        self._commands = {}
        self._output = ""
        self.console = Console()
        self.command_loader = None

        self.bootstrap()

    def bootstrap(self) -> None:
        """
        Bootstrap the console application.

        Returns:
            None
        """
        for bootstrapper in self.bootstrappers:
            bootstrapper(self)

    async def call(
        self,
        command: str,
        parameters: dict[str, Any] = {},
        output_buffer: Any | None = None,
    ) -> int:
        """
        Run a console command by name.

        Args:
            command: The command name to run.
            parameters: Parameters to pass to the command.
            output_buffer: Optional output buffer for capturing command output.

        Returns:
            Exit status code (0 for success, non-zero for error).
        """

        # Check if command exists
        if command not in self._commands:
            self._output = f"Command '{command}' not found."
            return 1

        # try:
        # Resolve the command from container
        command_class = self._commands[command]
        command_instance = await self.elyx.make(command_class)

        command_instance.set_elyx(self.get_elyx())
        command_instance.set_application(self)

        # command_instance.set
        command_instance.console = self.console

        # Parse arguments if parameters provided as list
        if isinstance(parameters, list):
            command_instance.parse_args(parameters)
            parameters = {}

        # Execute the command
        result = await command_instance.handle(**parameters)

        # Capture output if buffer provided
        if output_buffer is not None:
            self._output = str(result) if result is not None else ""

        return 0
        # except Exception as e:
        #     self._output = f"Error executing command: {e!s}"
        #     return 1

    def output(self) -> str:
        """
        Get the output from the last command.

        Returns:
            Command output as a string.
        """
        return self._output

    def add(self, name: str, command: type) -> None:
        """
        Register a command with the application.

        Args:
            name: The command name.
            command: The command class.
        """
        self.add_command(name, command)

    def add_command(self, name: str, command: type) -> None:
        """
        Register a command with the application.

        Args:
            name: The command name.
            command: The command class.
        """
        self._commands[name] = command

    async def run(self, input: list[str]) -> int:
        """
        Run the console application with command line arguments.

        Returns:
            Exit status code.
        """
        args = input[1:]

        command_name = args[0]
        remaining_args = args[1:]

        return await self.call(command_name, remaining_args)

    def terminate(self) -> None:
        pass

    def resolve(self, command):
        """
        Resolve a command and add it to the application.

        Args:
            command: Command class or instance to resolve.

        Returns:
            Self for method chaining.
        """

        # Instantiate to get the name from signature
        if isinstance(command, type) and issubclass(command, Command):
            # Instantiate to get the name from signature
            command_name = command.get_command_name()
            self.add(command_name, command)
        elif isinstance(command, Command):
            # Already an instance
            command_name = command.name
            self.add(command_name, command.__class__)

        self.add(command_name, command)

    def resolve_commands(self, commands: list) -> ApplicationContract:
        """
        Resolve and register multiple commands with the application.

        Args:
            commands: List of command classes to resolve and register.

        Returns:
            Self for method chaining.
        """
        for command in commands:
            self.resolve(command)

        return self

    def set_command_loader(self, command_map: dict) -> None:
        """
        Set the command loader with a command map.

        Args:
            command_map: Dictionary mapping command names to command classes.
        """
        self.command_loader = ContainerCommandLoader(self.elyx, command_map)

    async def get_command(self, name: str):
        """
        Get a command by name from the command loader.

        Args:
            name: The command name.

        Returns:
            Command instance.
        """
        if self.command_loader and self.command_loader.has(name):
            return await self.command_loader.get(name)
        return None

    def get_elyx(self) -> Container:
        """
        Get the Elyx application instance.

        Returns:
            Elyx Application instance.
        """
        return self.elyx
