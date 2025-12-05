from abc import abstractmethod
from pathlib import Path
from typing import Any, Callable

from elyx.contracts.container.container import Container


class Application(Container):
    @abstractmethod
    def bound(self, abstract) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        pass

    @abstractmethod
    def base_path(self, path: str = "") -> Path:
        """
        Get the base path of the application installation.

        Args:
            path: Optional path to append to the base path.

        Returns:
            The full base path.
        """
        pass

    @abstractmethod
    def bootstrap_path(self, path: str = "") -> Path:
        """
        Get the path to the bootstrap directory.

        Args:
            path: Optional path to append to the bootstrap directory.

        Returns:
            The full path to the bootstrap directory.
        """
        pass

    @abstractmethod
    def config_path(self, path: str = "") -> Path:
        """
        Get the path to the application configuration files.

        Args:
            path: Optional path to append to the config directory.

        Returns:
            The full path to the config directory.
        """
        pass

    @abstractmethod
    def database_path(self, path: str = "") -> Path:
        """
        Get the path to the database directory.

        Args:
            path: Optional path to append to the database directory.

        Returns:
            The full path to the database directory.
        """
        pass

    @abstractmethod
    def public_path(self, path: str = "") -> Path:
        """
        Get the path to the public directory.

        Args:
            path: Optional path to append to the public directory.

        Returns:
            The full path to the public directory.
        """
        pass

    @abstractmethod
    def resource_path(self, path: str = "") -> Path:
        """
        Get the path to the resources directory.

        Args:
            path: Optional path to append to the resources directory.

        Returns:
            The full path to the resources directory.
        """
        pass

    @abstractmethod
    def storage_path(self, path: str = "") -> Path:
        """
        Get the path to the storage directory.

        Args:
            path: Optional path to append to the storage directory.

        Returns:
            The full path to the storage directory.
        """
        pass

    @abstractmethod
    def environment(self, *environments: str) -> str | bool:
        """
        Get or check the current application environment.

        Args:
            *environments: Optional environment names to check against.

        Returns:
            Environment name if no args provided, bool if checking specific environments.
        """
        pass

    @abstractmethod
    def running_in_console(self) -> bool:
        """
        Determine if the application is running in the console.

        Returns:
            True if running in console, False otherwise.
        """
        pass

    @abstractmethod
    def running_unit_tests(self) -> bool:
        """
        Determine if the application is running unit tests.

        Returns:
            True if running unit tests, False otherwise.
        """
        pass

    @abstractmethod
    def has_debug_mode_enabled(self) -> bool:
        """
        Determine if the application is running with debug mode enabled.

        Returns:
            True if debug mode is enabled, False otherwise.
        """
        pass

    @abstractmethod
    def maintenance_mode(self) -> Any:
        """
        Get an instance of the maintenance mode manager implementation.

        Returns:
            Maintenance mode manager instance.
        """
        pass

    @abstractmethod
    def register_configured_providers(self) -> None:
        """Register all of the configured providers."""
        pass

    @abstractmethod
    def register(self, provider: Any | str, force: bool = False) -> Any:
        """
        Register a service provider with the application.

        Args:
            provider: Service provider instance or class name.
            force: Whether to force registration.

        Returns:
            The registered service provider instance.
        """
        pass

    @abstractmethod
    def register_deferred_provider(self, provider: str, service: str | None = None) -> None:
        """
        Register a deferred provider and service.

        Args:
            provider: Provider class name.
            service: Optional service name.
        """
        pass

    @abstractmethod
    def resolve_provider(self, provider: str) -> Any:
        """
        Resolve a service provider instance from the class name.

        Args:
            provider: Provider class name.

        Returns:
            Service provider instance.
        """
        pass

    @abstractmethod
    async def boot(self) -> None:
        """Boot the application's service providers."""
        pass

    @abstractmethod
    def booting(self, callback: Callable) -> None:
        """
        Register a new boot listener.

        Args:
            callback: Callback to execute during boot.
        """
        pass

    @abstractmethod
    async def booted(self, callback: Callable) -> None:
        """
        Register a new "booted" listener.

        Args:
            callback: Callback to execute after boot.
        """
        pass

    @abstractmethod
    async def bootstrap_with(self, bootstrappers: list) -> None:
        """
        Run the given array of bootstrap classes.

        Args:
            bootstrappers: List of bootstrapper classes.
        """
        pass

    # @abstractmethod
    # def get_locale(self) -> str:
    #     """
    #     Get the current application locale.

    #     Returns:
    #         Current locale string.
    #     """
    #     pass

    @abstractmethod
    def get_namespace(self) -> str:
        """
        Get the application namespace.

        Returns:
            Application namespace.

        Raises:
            RuntimeError: If namespace cannot be determined.
        """
        pass

    @abstractmethod
    def get_providers(self, provider: Any | str) -> list[Any]:
        """
        Get the registered service provider instances if any exist.

        Args:
            provider: Service provider instance or class name.

        Returns:
            List of matching provider instances.
        """
        pass

    @abstractmethod
    def has_been_bootstrapped(self) -> bool:
        """
        Determine if the application has been bootstrapped before.

        Returns:
            True if bootstrapped, False otherwise.
        """
        pass

    @abstractmethod
    def load_deferred_providers(self) -> None:
        """Load and boot all of the remaining deferred providers."""
        pass

    # @abstractmethod
    # def set_locale(self, locale: str) -> None:
    #     """
    #     Set the current application locale.

    #     Args:
    #         locale: Locale string to set.
    #     """
    #     pass

    @abstractmethod
    def should_skip_middleware(self) -> bool:
        """
        Determine if middleware has been disabled for the application.

        Returns:
            True if middleware should be skipped, False otherwise.
        """
        pass

    @abstractmethod
    def terminating(self, callback: Callable | str) -> "Application":
        """
        Register a terminating callback with the application.

        Args:
            callback: Callable or string reference to execute on termination.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def terminate(self) -> None:
        """Terminate the application."""
        pass
