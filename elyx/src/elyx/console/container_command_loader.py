from elyx.console.command import Command
from elyx.contracts.container.container import Container
from elyx.contracts.container.container_interface import ContainerInterface


class ContainerCommandLoader(ContainerInterface):
    def __init__(self, container: Container, command_map: list):
        """Initialize the container command loader."""
        self.container = container
        self.command_map = command_map

    def has(self, name: str) -> bool:
        """
        Check if a command exists in the command map.

        Args:
            name: The command name to check.

        Returns:
            bool: True if command exists, False otherwise.
        """
        return name in self.command_map

    async def get(self, name: str) -> Command:
        """
        Resolve a command from the container.

        Args:
            name: The command name to resolve.

        Returns:
            Command: The resolved command instance.

        Raises:
            KeyError: If the command does not exist.
        """
        if not self.has(name):
            raise KeyError(f'Command "{name}" does not exist.')

        return await self.container.get(self.command_map[name])

    def get_names(self) -> list[str]:
        """
        Get all command names from the command map.

        Returns:
            list[str]: List of command names.
        """
        return list(self.command_map.keys())
