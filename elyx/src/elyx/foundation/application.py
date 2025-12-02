import inspect
from pathlib import Path
from typing import Optional, TypeVar

from dependency_injector import providers

from elyx.container import Container
from elyx.foundation.console.kernel import ConsoleKernel

T = TypeVar("T")


class Application(Container):
    _has_been_bootstrapped: bool = False
    _booted: bool = False
    _booted_callbacks: list = []

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
        self.base_path = base_path
        # Register self as singleton instance using dependency-injector
        abstract_str = self._normalize_abstract(Application)
        setattr(self, abstract_str, providers.Object(self))

    async def handle_command(self, input: list[str]) -> None:
        kernel = await self.make(ConsoleKernel)
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
