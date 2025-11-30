from elyx.console.command import Command


class TestCommand(Command):
    """A simple test command to verify the setup is working."""

    @property
    def name(self) -> str:
        return "test"

    @property
    def description(self) -> str:
        return "Test command to verify setup"

    def handle(self):
        """Execute the test command."""
        print("Test command executed successfully!")
        print("Setup is working as expected.")
        return 0
