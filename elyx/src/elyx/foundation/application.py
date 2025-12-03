import inspect
from pathlib import Path
from typing import Optional, TypeVar

from elyx.container.container import Container
from elyx.foundation.console.kernel import ConsoleKernel

T = TypeVar("T")


class Application(Container):
    _has_been_bootstrapped: bool = False
    _booted: bool = False
    _booted_callbacks: list = []

    _environment_path = None
    _environment_file = ".env"

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

        return ApplicationBuilder(Application(base_path=base_path)).with_kernels()

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the application container."""
        super().__init__()
        if base_path:
            self.set_base_path(base_path)

        self._register_base_bindings()
        self._register_base_service_providers()

    def _register_base_bindings(self):
        """Register the basic bindings into the container."""
        self.instance("app", self)
        self.instance(Application, self)
        self.instance(Container, self)

    def _register_base_service_providers(self):
        """Register all of the base service providers."""
        # TODO: This
        pass

    def _register_core_container_aliases(self):
        """Register the core class aliases in the container."""
        # aliases = {
        #     'config':
        # }
        # TODO: This
        pass

    async def handle_command(self, input: list[str]) -> None:
        kernel = await self.make(ConsoleKernel, app=self)
        status = await kernel.handle(input)
        # kernel.terminate()

    def has_been_bootstrapped(self) -> bool:
        return self._has_been_bootstrapped

    async def bootstrap_with(self, bootstrappers: list) -> None:
        self._has_been_bootstrapped = True

        for bootstrapper in bootstrappers:
            instance = await self.make(bootstrapper)
            result = instance.bootstrap(self)
            if inspect.iscoroutine(result):
                await result

    async def booted(self, callback):
        """
        Register a new "booted" listener.

        Args:
            callback: Callable to execute when application is booted.

        Returns:
            None
        """
        self._booted_callbacks.append(callback)

        if self.is_booted():
            result = callback(self)
            if inspect.iscoroutine(result):
                await result

    def is_booted(self) -> bool:
        """
        Determine if the application has been booted.

        Returns:
            bool
        """
        return self._booted

    async def boot(self) -> None:
        """
        Boot the application's service providers.

        Returns:
            None
        """
        if self.is_booted():
            return

        # Fire booted callbacks
        for callback in self._booted_callbacks:
            result = callback(self)
            if inspect.iscoroutine(result):
                await result

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

    def environment_path(self) -> str:
        """
        Get the path to the environment file directory.

        Returns:
            The full path to the environment file directory.
        """
        environment_path = getattr(self, "_environment_path", None)
        return environment_path if environment_path else str(self.base_path)

    def environment_file(self) -> str:
        """
        Get the environment file the application is using.

        Returns:
            The environment file name.
        """
        environment_file = getattr(self, "_environment_file", None)
        return environment_file if environment_file else ".env"

    def environment_file_path(self) -> str:
        """
        Get the fully qualified path to the environment file.

        Returns:
            The full path to the environment file.
        """
        return self.join_paths(self.environment_path(), self.environment_file())
