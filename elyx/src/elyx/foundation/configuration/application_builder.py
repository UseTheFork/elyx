from pathlib import Path
from typing import Optional

from dependency_injector import providers

from elyx.foundation.application import Application
from elyx.foundation.bootstrap.register_providers import RegisterProviders
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

        # Use self._application directly, not getattr
        provider = providers.Singleton(ConsoleKernel, app=self._application)
        setattr(self._application._bindings, abstract_str, provider)

        return self

    def with_providers(
        self, providers: list[type] | None = None, with_bootstrap_providers: bool = True
    ) -> "ApplicationBuilder":
        """
        Register service providers with the application.

        Args:
            providers: List of provider classes to register.
            with_bootstrap_providers: Whether to include bootstrap providers.

        Returns:
            ApplicationBuilder instance for chaining.
        """

        if providers is None:
            providers = []

        bootstrap_provider_path = None
        if with_bootstrap_providers:
            # Get bootstrap providers path if it exists
            bootstrap_path = self._application.path("bootstrap/providers.py")
            if bootstrap_path.exists():
                bootstrap_provider_path = bootstrap_path

        RegisterProviders.merge(providers, bootstrap_provider_path)

        return self

    def with_commands(self, commands: Optional[list[type]] = None) -> "ApplicationBuilder":
        """
        Register commands with the application.

        Args:
            commands: List of command classes.

        Returns:
            ApplicationBuilder instance for chaining.
        """

        # Auto-discover commands from app/Console/Commands if no commands provided
        if not commands:
            console_commands_path = Path(self._application.path("console/commands"))
            if console_commands_path.exists():
                commands = [console_commands_path]

        # Register callback to run after console kernel is resolved
        def register_commands_callback(kernel, app):
            def register_on_boot(app):
                # Check if commands are paths or classes
                for command in commands:
                    if isinstance(command, Path):
                        kernel.add_command_paths([command])
                    else:
                        kernel.add_commands([command])

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
