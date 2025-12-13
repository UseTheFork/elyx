from elyx.foundation.console.about_command import AboutCommand
from elyx.support.service_provider import ServiceProvider


class ConsoleCommandServiceProvider(ServiceProvider):
    _commands = {
        "about": AboutCommand,
    }

    def register(self) -> None:
        """Register the log manager as a singleton."""
        self._register_commands()

    def _register_commands(self) -> None:
        """Register all console commands."""
        self.register_commands(self._commands)

    def register_commands(self, commands: dict[str, type]) -> None:
        """
        Register multiple commands with optional custom registration methods.

        Args:
            commands: Dictionary mapping command names to command classes.
        """
        for command_name, command_class in commands.items():
            method_name = f"register_{command_name}_command"

            if hasattr(self, method_name):
                getattr(self, method_name)()

        self.commands(list(commands.values()))

    def register_about_command(self) -> None:
        """Register the about command."""
        self.app.singleton(AboutCommand)
