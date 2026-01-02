import os
import sys
from pathlib import Path
from typing import Any, Callable, Optional, Self, TypeVar

from elyx.config import Repository
from elyx.container import Container
from elyx.contracts.config import Repository as RepositoryContract
from elyx.contracts.container import Container as ContainerContract, ContainerInterface
from elyx.contracts.events import Dispatcher as DispatcherContract
from elyx.contracts.support import ServiceProvider
from elyx.events import Dispatcher, EventServiceProvider
from elyx.foundation import ConsoleCommandServiceProvider, ConsoleKernel, LoadEnvironmentVariables
from elyx.logging import LogServiceProvider
from elyx.support import Macroable, Str

T = TypeVar("T")


class Application(Container, Macroable):
    def _register_base_bindings(self):
        """Register the basic bindings into the container."""
        self.instance("app", self)
        self.instance(Application, self)
        self.instance(Container, self)

    def _register_base_service_providers(self):
        """Register all of the base service providers."""

        self.register(EventServiceProvider)
        self.register(LogServiceProvider)
        self.register(ConsoleCommandServiceProvider)

    def _register_core_container_aliases(self):
        """Register the core class aliases in the container."""
        aliases = {
            "app": [Application, Container, ContainerContract, ContainerInterface],
            "config": [Repository, RepositoryContract],
            "events": [Dispatcher, DispatcherContract],
        }

        for key, alias_list in aliases.items():
            for alias in alias_list:
                self.alias(key, alias)

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the application container."""
        super().__init__()

        # Initialize instance variables
        self._has_been_bootstrapped = False
        self._booted = False
        self._deferred_services = {}
        self._booting_callbacks = []
        self._booted_callbacks = []
        self._terminating_callbacks = []
        self._environment_path = None
        self._environment_file = ".env"
        self._is_running_in_console = None

        if base_path:
            self.set_base_path(base_path)

        # register the application for use with all helper methods.
        import elyx.support.helpers as helpers

        helpers._app = self

        self._service_providers = {}
        self._register_base_bindings()
        self._register_base_service_providers()
        self._register_core_container_aliases()

    @staticmethod
    def configure(base_path: Optional[Path] = None):
        """
        Create and configure a new Application instance.

        Args:
            base_path: Optional base path for the application.

        Returns:
            Application instance.
        """
        from elyx.foundation.configuration.application_builder import ApplicationBuilder

        return ApplicationBuilder(Application(base_path=base_path)).with_kernels().with_commands().with_providers()

    async def handle_command(self, input: list[str]) -> int:
        dispatcher = self.make(Dispatcher)
        kernel = self.make(ConsoleKernel, app=self, events=dispatcher)
        status = await kernel.handle(input)
        kernel.terminate()

        return status

    def bootstrap_with(self, bootstrappers: list) -> None:
        self._has_been_bootstrapped = True

        for bootstrapper in bootstrappers:
            instance = self.make(bootstrapper)
            instance.bootstrap(self)

    def booting(self, callback: Callable) -> None:
        """
        Register a new boot listener.

        Args:
            callback: Callback to execute during boot.

        Returns:
            None
        """
        self._booting_callbacks.append(callback)

    def booted(self, callback):
        """
        Register a new "booted" listener.

        Args:
            callback: Callable to execute when application is booted.

        Returns:
            None
        """
        self._booted_callbacks.append(callback)

        if self.is_booted():
            callback(self)

    def is_booted(self) -> bool:
        """
        Determine if the application has been booted.

        Returns:
            bool
        """
        return self._booted

    def boot(self) -> None:
        """
        Boot the application's service providers.

        Returns:
            None
        """
        if self.is_booted():
            return

        # Fire booting callbacks
        for callback in self._booting_callbacks:
            callback(self)

        # Fire booted callbacks
        for callback in self._booted_callbacks:
            callback(self)

        self._booted = True

    def join_paths(self, base_path: str | Path, path: str = "") -> Path:
        """
        Join the given paths together.

        Args:
            base_path: The base path.
            path: The path to join (optional).

        Returns:
            The joined path as a Path object.
        """

        base = Path(base_path)
        if path:
            return base / path
        return base

    def path(self, path: str = "") -> Path:
        """
        Get the path to the application "app" directory.

        Args:
            path: Optional path to append to the app directory.

        Returns:
            The full path to the app directory or subdirectory.
        """
        app_path = getattr(self, "_app_path", None)
        base = app_path if app_path else self.join_paths(self.base_path(), "app")
        return self.join_paths(base, path)

    def before_bootstrapping(self, bootstrapper, callback: Callable) -> None:
        """
        Register a callback to run before a bootstrapper.

        Args:
            bootstrapper: The bootstrapper class.
            callback: Callback to execute before bootstrapping.
        """
        bootstrapper_name = self._normalize_abstract(bootstrapper)
        self["events"].listen(f"bootstrapping: {bootstrapper_name}", callback)

    def after_loading_environment(self, callback: Callable) -> None:
        """
        Register a callback to run after loading the environment.

        Args:
            callback: Callback to execute after bootstrapping.
        """
        self.after_bootstrapping(LoadEnvironmentVariables, callback)

    def after_bootstrapping(self, bootstrapper, callback: Callable) -> None:
        """
        Register a callback to run after a bootstrapper.

        Args:
            bootstrapper: The bootstrapper class.
            callback: Callback to execute after bootstrapping.
        """
        bootstrapper_name = self._normalize_abstract(bootstrapper)
        self["events"].listen(f"bootstrapped: {bootstrapper_name}", callback)

    def has_been_bootstrapped(self) -> bool:
        """
        Determine if the application has been bootstrapped before.

        Returns:
            True if bootstrapped, False otherwise.
        """
        return self._has_been_bootstrapped

    def has_debug_mode_enabled(self) -> bool:
        """
        Determine if the application is running with debug mode enabled.

        Returns:
            True if debug mode, False otherwise.
        """
        return bool(self["config"].get("app.debug"))

    def set_base_path(self, base_path: Path):
        """Set the base path for the application."""
        self._base_path = base_path

        self.bind_paths_in_container()

        return self

    def bind_paths_in_container(self):
        """Set the base path for the application."""
        self.instance("path", self.path())
        self.instance("path.base", self.base_path())
        self.instance("path.config", self.config_path())
        self.instance("path.database", self.database_path())
        self.instance("path.public", self.public_path())
        self.instance("path.resource", self.resource_path())
        self.instance("path.storage", self.storage_path())

        return self

    def base_path(self, path: str = "") -> Path:
        """
        Get the base path of the application installation.

        Args:
            path: Optional path to append to the base path.

        Returns:
            The full base path or base path with appended subdirectory.
        """
        return self.join_paths(self._base_path, path)

    def config_path(self, path: str = "") -> Path:
        """
        Get the path to the application configuration files.

        Args:
            path: Optional path to append to the config directory.

        Returns:
            The full path to the config directory or subdirectory.
        """
        config_path = getattr(self, "_config_path", None)
        base = config_path if config_path else self.base_path("config")
        return self.join_paths(base, path)

    def use_config_path(self, path: str | Path) -> Self:
        """
        Set the configuration directory.

        Args:
            path: The configuration directory path.

        Returns:
            Self for method chaining.
        """
        self._config_path = Path(path)
        self.instance("path.config", self._config_path)
        return self

    def database_path(self, path: str = "") -> Path:
        """
        Get the path to the database directory.

        Args:
            path: Optional path to append to the database directory.

        Returns:
            The full path to the database directory or subdirectory.
        """
        database_path = getattr(self, "_database_path", None)
        base = database_path if database_path else self.base_path("database")
        return self.join_paths(base, path)

    def public_path(self, path: str = "") -> Path:
        """
        Get the path to the public directory.

        Args:
            path: Optional path to append to the public directory.

        Returns:
            The full path to the public directory or subdirectory.
        """
        public_path = getattr(self, "_public_path", None)
        base = public_path if public_path else self.base_path("public")
        return self.join_paths(base, path)

    def resource_path(self, path: str = "") -> Path:
        """
        Get the path to the resources directory.

        Args:
            path: Optional path to append to the resources directory.

        Returns:
            The full path to the resources directory or subdirectory.
        """
        resource_path = getattr(self, "_resource_path", None)
        base = resource_path if resource_path else self.base_path("resources")
        return self.join_paths(base, path)

    def storage_path(self, path: str = "") -> Path:
        """
        Get the path to the storage directory.

        Args:
            path: Optional path to append to the storage directory.

        Returns:
            The full path to the storage directory or subdirectory.
        """
        storage_path = getattr(self, "_storage_path", None)
        base = storage_path if storage_path else self.base_path("storage")
        return self.join_paths(base, path)

    def environment_path(self) -> Path:
        """
        Get the path to the environment file directory.

        Returns:
            The full path to the environment file directory.
        """
        environment_path = getattr(self, "_environment_path", None)
        return Path(environment_path) if environment_path else self.base_path()

    def environment_file(self) -> Path:
        """
        Get the environment file the application is using.

        Returns:
            The environment file name.
        """
        environment_file = getattr(self, "_environment_file", None)
        return Path(environment_file) if environment_file else Path(".env")

    def environment_file_path(self) -> Path:
        """
        Get the fully qualified path to the environment file.

        Returns:
            The full path to the environment file.
        """
        return self.join_paths(self.environment_path(), self.environment_file())

    def environment(self, *environments) -> str | bool:
        """
        Get or check the current application environment.

        Args:
            *environments: Optional environment names to check against.

        Returns:
            Environment name if no args provided, bool if checking specific environments.
        """

        if len(environments) > 0:
            patterns = environments[0] if isinstance(environments[0], list) else list(environments)
            return Str.is_pattern(patterns, self["env"])

        return self["env"]

    def is_local(self) -> bool:
        """
        Determine if the application is in the local environment.

        Returns:
            True if in local environment, False otherwise.
        """
        return self["env"] == "local"

    def is_production(self) -> bool:
        """
        Determine if the application is in the production environment.

        Returns:
            True if in production environment, False otherwise.
        """
        return self["env"] == "production"

    def running_unit_tests(self) -> bool:
        """
        Determine if the application is running unit tests.

        Returns:
            True if running unit tests, False otherwise.
        """
        return self.bound("env") and self["env"] == "testing"

    def detect_environment(self, callback: Callable) -> str:
        """
        Detect the application's current environment.

        Args:
            callback: Closure that returns the environment name.

        Returns:
            Environment name.
        """
        from elyx.foundation.environment_detector import EnvironmentDetector

        args = sys.argv if self.running_in_console() else None

        env = EnvironmentDetector().detect(callback, args)
        self.instance("env", env)
        return env

    def running_in_console(self) -> bool:
        """
        Determine if the application is running in the console.

        Returns:
            True if running in console, False otherwise.
        """
        if self._is_running_in_console is None:
            # Check environment variable first, then check if running in CLI
            env_value = os.getenv("APP_RUNNING_IN_CONSOLE")
            if env_value is not None:
                self._is_running_in_console = env_value.lower() in ("true", "1", "yes")
            else:
                # Check if running in CLI mode (similar to PHP's CLI SAPI check)
                self._is_running_in_console = not hasattr(sys, "ps1") and sys.stdin.isatty()

        return bool(self._is_running_in_console)

    def _mark_as_registered(self, provider: ServiceProvider) -> None:
        """
        Mark the given provider as registered.

        Args:
            provider: Service provider instance.
        """
        name = self._normalize_abstract(provider)
        self._service_providers[name] = provider

    def _boot_provider(self, provider: ServiceProvider) -> None:
        """
        Boot the given service provider.

        Args:
            provider: Service provider instance to boot.
        """
        if hasattr(provider, "boot") and callable(provider.boot):
            self.call(provider.boot)

    def register(self, provider, force: bool = False) -> ServiceProvider:
        """
        Register a service provider with the application.

        """

        registered = self.get_provider(provider)
        if registered and not force:
            return registered

        if isinstance(provider, str):
            provider = self.resolve_provider(provider)

        if isinstance(provider, type):
            provider = self.resolve_provider(provider)

        if hasattr(provider, "register") and callable(provider.register):
            provider.register()

        if hasattr(provider, "bindings"):
            for key, value in provider.bindings.items():
                self.bind(key, value)

        if hasattr(provider, "singletons"):
            for key, value in provider.singletons.items():
                if isinstance(key, int):
                    key = value
                self.singleton(key, value)

        self._mark_as_registered(provider)

        if self.is_booted():
            self._boot_provider(provider)

        return provider

    def get_provider(self, provider):
        """
        Get the registered service provider instance if it exists.

        Args:
            provider: Service provider instance or class name.

        Returns:
            Service provider instance or None if not found.
        """
        name = self._normalize_abstract(provider)
        return self._service_providers.get(name)

    def resolve_provider(self, provider):
        """
        Resolve a service provider instance from the class name.

        Args:
            provider: Service provider class or class name.

        Returns:
            Service provider instance.
        """
        return provider(self)

    def terminating(self, callback: Callable | str) -> Self:
        """
        Register a terminating callback with the application.

        Args:
            callback: Callable or string reference to execute on termination.

        Returns:
            Self for method chaining.
        """
        self._terminating_callbacks.append(callback)
        return self

    def terminate(self) -> None:
        """Terminate the application."""
        for callback in self._terminating_callbacks:
            self.call(callback)

    def get_deferred_services(self) -> dict:
        """
        Get the application's deferred services.

        Returns:
            Dictionary of deferred services.
        """
        return self._deferred_services

    def set_deferred_services(self, services: dict) -> None:
        """
        Set the application's deferred services.

        Args:
            services: Dictionary of deferred services.
        """
        self._deferred_services = services

    def is_deferred_service(self, service: str) -> bool:
        """
        Determine if the given service is a deferred service.

        Args:
            service: Service name to check.

        Returns:
            True if service is deferred, False otherwise.
        """
        return service in self._deferred_services

    def add_deferred_services(self, services: dict) -> None:
        """
        Add an array of services to the application's deferred services.

        Args:
            services: Dictionary of services to add.
        """
        self._deferred_services.update(services)

    def remove_deferred_services(self, services: list[str]) -> None:
        """
        Remove an array of services from the application's deferred services.

        Args:
            services: List of service names to remove.
        """
        for service in services:
            self._deferred_services.pop(service, None)

    def flush(self) -> None:
        """
        Flush the container of all bindings and resolved instances.
        """
        super().flush()

        self._deferred_services = {}
        self._booting_callbacks = []
        self._booted_callbacks = []
        self._terminating_callbacks = []

    def load_deferred_providers(self) -> None:
        """Load and boot all of the remaining deferred providers."""
        for service in list(self._deferred_services.keys()):
            self.load_deferred_provider(service)

        self._deferred_services = {}

    def load_deferred_provider(self, service: str) -> None:
        """
        Load the provider for a deferred service.

        Args:
            service: Service name to load.
        """
        if not self.is_deferred_service(service):
            return

        provider = self._deferred_services[service]

        if self.get_provider(provider) is None:
            self.register_deferred_provider(provider, service)

    def register_deferred_provider(self, provider: str | type, service: str | None = None) -> None:
        """
        Register a deferred provider and service.

        Args:
            provider: Provider class or class name.
            service: Optional service name.
        """
        if service:
            self._deferred_services.pop(service, None)

        instance = self.register(provider)

        if not self.is_booted():
            self.booting(lambda app: self._boot_provider(instance))

    def _load_deferred_provider_if_needed(self, abstract: str) -> None:
        """
        Load the deferred provider if the given type is a deferred service and the instance has not been loaded.

        Args:
            abstract: The abstract type to check.
        """
        if self.is_deferred_service(abstract) and abstract not in self._instances:
            self.load_deferred_provider(abstract)

    def make(self, abstract, **kwargs) -> T | Any:
        """
        Resolve the given type from the container.

        Args:
            abstract: Abstract type identifier or class.
            **kwargs: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
        """
        abstract_str = self._normalize_abstract(abstract)
        abstract_str = self.get_alias(abstract_str)
        self._load_deferred_provider_if_needed(abstract_str)

        return super().make(abstract, **kwargs)

    def resolve(self, abstract, raise_events=True, **kwargs) -> T | Any:
        """
        Resolve the given type from the container.

        Args:
            abstract: Abstract type identifier or class.
            **kwargs: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
        """
        abstract_str = self._normalize_abstract(abstract)
        abstract_str = self.get_alias(abstract_str)
        self._load_deferred_provider_if_needed(abstract_str)

        return super().resolve(abstract, raise_events, **kwargs)

    def bound(self, abstract) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return self.is_deferred_service(abstract_str) or super().bound(abstract)
