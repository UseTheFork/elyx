from typing import Callable

from elyx.contracts.foundation.application import Application
from elyx.contracts.support.service_provider import ServiceProvider as ServiceProviderContract


class ServiceProvider(ServiceProviderContract):
    """Base class for service providers."""

    booting_callbacks: list[Callable] = []
    booted_callbacks: list[Callable] = []

    def __init__(self, app: Application, **kwargs):
        self.app = app
        self.booting_callbacks = []
        self.booted_callbacks = []

    def booting(self, callback: Callable) -> None:
        """
        Register a booting callback to be run before the "boot" method is called.

        Args:
            callback: Callback to execute before boot.
        """
        self.booting_callbacks.append(callback)

    def booted(self, callback: Callable) -> None:
        """
        Register a booted callback to be run after the "boot" method is called.

        Args:
            callback: Callback to execute after boot.
        """
        self.booted_callbacks.append(callback)

    async def call_booting_callbacks(self) -> None:
        """Call the registered booting callbacks."""
        index = 0
        while index < len(self.booting_callbacks):
            await self.app.call(self.booting_callbacks[index])
            index += 1

    async def call_booted_callbacks(self) -> None:
        """Call the registered booted callbacks."""
        index = 0
        while index < len(self.booted_callbacks):
            await self.app.call(self.booted_callbacks[index])
            index += 1
