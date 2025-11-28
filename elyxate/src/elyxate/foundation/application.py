import os
from collections.abc import Callable
from typing import Any

from elyxate.container import Container
from elyxate.foundation.configuration.application_builder import ApplicationBuilder


class Application:
    """
    The main application class for managing the application lifecycle.
    """

    def __init__(self, base_path: str | None = None):
        """
        Create a new application instance.

        Args:
            base_path: The base path of the application.
        """
        super().__init__()

        # Indicates if the application has "booted".
        self._booted: bool = False

        # The array of booting callbacks.
        self._booting_callbacks: list[Callable] = []

        # The array of booted callbacks.
        self._booted_callbacks: list[Callable] = []

        # The array of terminating callbacks.
        self._terminating_callbacks: list[Callable] = []

        # All of the registered service providers.
        self._service_providers: dict[str, Any] = {}

        # The names of the loaded service providers.
        self._loaded_providers: dict[str, bool] = {}

        # The deferred services and their providers.
        self._deferred_services: dict[str, str] = {}

        # The custom bootstrap path defined by the developer.
        self._bootstrap_path: str | None = None

        # The custom application path defined by the developer.
        self._app_path: str | None = None

        # The custom configuration path defined by the developer.
        self._config_path: str | None = None

        # The custom database path defined by the developer.
        self._database_path: str | None = None

        # The custom language file path defined by the developer.
        self._lang_path: str | None = None

        # The custom public / web path defined by the developer.
        self._public_path: str | None = None

        # The custom storage path defined by the developer.
        self._storage_path: str | None = None

        # The custom environment path defined by the developer.
        self._environment_path: str | None = None

        # The environment file to load during bootstrapping.
        self._environment_file: str = ".env"

        # Indicates if the application is running in the console.
        self._is_running_in_console: bool | None = None

        if base_path:
            self.set_base_path(base_path)

        self._register_base_bindings()
        self._register_base_service_providers()
        self._register_core_container_aliases()

    def _register_base_bindings(self) -> None:
        """
        Register the basic bindings into the container.
        """
        Application.set_instance(self)

        self.instance("app", self)
        self.instance(Container, self)

    def _register_base_service_providers(self) -> None:
        """
        Register the base service providers.
        """
        # Keep this empty for now
        pass

    def _register_core_container_aliases(self) -> None:
        """
        Register the core container aliases.
        """
        # Keep this empty for now
        pass

    def register(self, provider: Any | str, force: bool = False) -> Any:
        """
        Register a service provider with the application.

        Args:
            provider: Service provider instance or class name.
            force: Force registration even if already registered.

        Returns:
            The registered service provider.
        """
        registered = self.get_provider(provider)
        if registered and not force:
            return registered

        # If the given "provider" is a string, we will resolve it, passing in the
        # application instance automatically for the developer. This is simply
        # a more convenient way of specifying your service provider classes.
        if isinstance(provider, str):
            provider = self.resolve_provider(provider)

        provider.register()

        # If there are bindings / singletons set as properties on the provider we
        # will spin through them and register them with the application, which
        # serves as a convenience layer while registering a lot of bindings.
        if hasattr(provider, "bindings"):
            for key, value in provider.bindings.items():
                self.bind(key, value)

        if hasattr(provider, "singletons"):
            for key, value in provider.singletons.items():
                if isinstance(key, int):
                    key = value

                self.singleton(key, value)

        self._mark_as_registered(provider)

        # If the application has already booted, we will call this boot method on
        # the provider class so it has an opportunity to do its boot logic and
        # will be ready for any usage by this developer's application logic.
        if self.is_booted():
            self._boot_provider(provider)

        return provider

    def get_provider(self, provider: Any | str) -> Any | None:
        """
        Get the registered service provider instance if it exists.

        Args:
            provider: Service provider instance or class name.

        Returns:
            The service provider instance or None.
        """
        name = provider if isinstance(provider, str) else provider.__class__.__name__

        return self._service_providers.get(name)

    def get_providers(self, provider: Any | str) -> list[Any]:
        """
        Get the registered service provider instances if any exist.

        Args:
            provider: Service provider instance or class name.

        Returns:
            List of matching service provider instances.
        """
        name = provider if isinstance(provider, str) else provider.__class__.__name__

        return [value for value in self._service_providers.values() if isinstance(value, type(provider))]

    def resolve_provider(self, provider: str) -> Any:
        """
        Resolve a service provider instance from the class name.

        Args:
            provider: Service provider class name.

        Returns:
            Service provider instance.
        """
        # This would need proper module resolution in practice
        provider_class = provider  # Placeholder for actual class resolution
        return provider_class(self)

    def make(self, abstract: str | type, parameters: dict[str, Any] | None = None):
        """
        Resolve the given type from the container.

        Args:
            abstract: Abstract type identifier or class.
            parameters: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
        """
        abstract_str = self._normalize_abstract(abstract)
        self._load_deferred_provider_if_needed(self._get_alias(abstract_str))

        return super().make(abstract, parameters)

    def _resolve(
        self,
        abstract: str | type,
        parameters: dict[str, Any] | None = None,
        raise_events: bool = True,
    ):
        """
        Resolve the given type from the container.

        Args:
            abstract: Abstract type identifier or class.
            parameters: Parameters to pass to the constructor.
            raise_events: Whether to raise resolution events.

        Returns:
            Resolved instance.
        """
        abstract_str = self._normalize_abstract(abstract)
        self._load_deferred_provider_if_needed(self._get_alias(abstract_str))

        return super()._resolve(abstract, parameters, raise_events)

    def _load_deferred_provider_if_needed(self, abstract: str) -> None:
        """
        Load the deferred provider if the given type is a deferred service and the instance has not been loaded.

        Args:
            abstract: Abstract type identifier.
        """
        if self._is_deferred_service(abstract) and abstract not in self._instances:
            self._load_deferred_provider(abstract)

    def bound(self, abstract: str | type) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return self._is_deferred_service(abstract_str) or super().bound(abstract)

    def is_booted(self) -> bool:
        """
        Determine if the application has booted.

        Returns:
            bool
        """
        return self._booted

    def boot(self) -> None:
        """
        Boot the application's service providers.
        """
        if self.is_booted():
            return

        # Once the application has booted we will also fire some "booted" callbacks
        # for any listeners that need to do work after this initial booting gets
        # finished. This is useful when ordering the boot-up processes we run.
        self._fire_app_callbacks(self._booting_callbacks)

        for provider in self._service_providers.values():
            self._boot_provider(provider)

        self._booted = True

        self._fire_app_callbacks(self._booted_callbacks)

    def _boot_provider(self, provider: Any) -> None:
        """
        Boot the given service provider.

        Args:
            provider: Service provider instance.
        """
        provider.call_booting_callbacks()

        if hasattr(provider, "boot"):
            self.call([provider, "boot"])

        provider.call_booted_callbacks()

    def booting(self, callback: Callable) -> None:
        """
        Register a new boot listener.

        Args:
            callback: Callback to execute during booting.
        """
        self._booting_callbacks.append(callback)

    def booted(self, callback: Callable) -> None:
        """
        Register a new "booted" listener.

        Args:
            callback: Callback to execute after booting.
        """
        self._booted_callbacks.append(callback)

        if self.is_booted():
            callback(self)

    def _fire_app_callbacks(self, callbacks: list[Callable]) -> None:
        """
        Fire the given callbacks.

        Args:
            callbacks: List of callbacks to execute.
        """
        for callback in callbacks:
            callback(self)

    def _mark_as_registered(self, provider: Any) -> None:
        """
        Mark the given provider as registered.

        Args:
            provider: Service provider instance.
        """
        self._service_providers[provider.__class__.__name__] = provider
        self._loaded_providers[provider.__class__.__name__] = True

    def _is_deferred_service(self, abstract: str) -> bool:
        """
        Determine if the given service is a deferred service.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        return abstract in self._deferred_services

    def _load_deferred_provider(self, abstract: str) -> None:
        """
        Load the deferred provider for the given service.

        Args:
            abstract: Abstract type identifier.
        """
        # Placeholder for deferred provider loading logic
        pass

    def set_base_path(self, base_path: str) -> None:
        """
        Set the base path for the application.

        Args:
            base_path: The base path.
        """
        self._base_path = base_path

    @staticmethod
    def set_instance(instance: "Application") -> None:
        """
        Set the globally available instance of the container.

        Args:
            instance: Application instance.
        """
        # Placeholder for setting global instance
        pass

    @staticmethod
    def configure(base_path: str | None = None) -> ApplicationBuilder:
        """
        Begin configuring a new Laravel application instance.

        Args:
            base_path: The base path for the application.

        Returns:
            ApplicationBuilder instance.
        """
        if base_path is None:
            base_path = Application.infer_base_path()

        return ApplicationBuilder(Application(base_path))

    @staticmethod
    def infer_base_path() -> str:
        """
        Infer the base path for the application.

        Returns:
            The inferred base path.
        """
        # Return the current working directory as the base path
        return os.getcwd()
