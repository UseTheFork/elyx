import argparse

from elyx.console.argument_parser import ArgumentParser
from elyx.contracts.console.command_contract import CommandContract
from elyx.contracts.container_contract import ContainerContract


class Command(CommandContract):
    """Console application for handling command execution."""

    hidden = False

    @property
    def parser(self):
        parser = ArgumentParser(
            prog=self.name,
            description=self.descripton,
        )
        parser.add_argument("ask_query", nargs=argparse.REMAINDER, help="The user's question or query text")
        return parser

    def get_elyx(self) -> ContainerContract:
        """
        Get the Elyx console application instance.

        Returns:
            ConsoleApplication instance.
        """
        return self.elyx

    def set_elyx(self, elyx: ContainerContract) -> None:
        """
        Set the Elyx application instance.

        Returns:
            ConsoleApplication instance.
        """
        self.elyx = elyx
