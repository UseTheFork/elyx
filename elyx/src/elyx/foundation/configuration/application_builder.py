from typing import Optional

from dependency_injector import providers

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
        # Register ConsoleKernel with explicit dependency injection
        abstract_str = self._application._normalize_abstract(ConsoleKernel)
        app_abstract_str = self._application._normalize_abstract(Application)

        setattr(
            self._application,
            abstract_str,
            providers.Singleton(ConsoleKernel, app=getattr(self._application, app_abstract_str)),
        )

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
        async def register_commands_callback(kernel, app):
            def register_on_boot():
                kernel.add_commands(commands)

            await self._application.booted(register_on_boot)

        self._application.after_resolving(ConsoleKernel, register_commands_callback)

        return self

    def create(self) -> Application:
        """
        Get the application instance.

        Returns:
            Application instance.
        """

        return self._application
