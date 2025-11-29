from typing import Optional

from elyx.foundation.application import Application
from elyx.foundation.console.kernel import ConsoleKernel


class ApplicationBuilder:
    def __init__(self, application: Application):
        """Create a new application builder instance."""
        self._application = application

    def with_kernels(self) -> "ApplicationBuilder":
        """
        Register the console kernel as a singleton.

        Returns:
            ApplicationBuilder instance for chaining.
        """
        self._application.singleton(ConsoleKernel, ConsoleKernel)

        return self

    def with_commands(self, commands: Optional[list[type]] = None) -> "ApplicationBuilder":
        """
        Register commands with the application.

        Args:
            commands: List of command classes.

        Returns:
            ApplicationBuilder instance for chaining.
        """
        if commands is None:
            commands = []

        # Register callback to run after console kernel is resolved
        async def register_commands_callback(kernel):
            def register_on_boot():
                kernel.add_commands(commands)

            self._application.booted(register_on_boot)

        self._application.after_resolving(ConsoleKernel, register_commands_callback)

        return self

    def create(self) -> Application:
        """
        Get the application instance.

        Returns:
            Application instance.
        """

        return self._application
