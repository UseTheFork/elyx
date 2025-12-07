from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from elyx.contracts.foundation.application import Application
from elyx.contracts.foundation.bootstrapper import Bootstrapper
from elyx.support.service_provider import ServiceProvider


class RegisterProviders(Bootstrapper):
    async def bootstrap(self, app: Application) -> None:
        """
        Register all service providers with the application.

        Args:
            app: The application instance.
        """
        # Get providers from application configuration
        providers = self._get_providers(app)

        # Register each provider
        for provider_class in providers:
            # Check that provider extends ServiceProvider
            if not (inspect.isclass(provider_class) and issubclass(provider_class, ServiceProvider)):
                raise TypeError(
                    f"Provider {provider_class.__name__ if inspect.isclass(provider_class) else provider_class} "
                    f"must extend ServiceProvider"
                )

            # Instantiate the provider
            provider = await app.make(provider_class, app=app)

            # Call the register method if it exists
            if hasattr(provider, "register") and callable(provider.register):
                result = provider.register()
                if inspect.iscoroutine(result):
                    await result

    def _get_providers(self, app: Application) -> list[type]:
        """
        Get the list of provider classes to register.

        Args:
            app: The application instance.

        Returns:
            List of provider classes.
        """
        providers = []

        # Check if app has a providers attribute
        if hasattr(app, "providers"):
            providers.extend(app.providers)

        # Optionally discover providers from bootstrap/providers.py
        if app.base_path:
            providers_file = app.path("bootstrap/providers.py")
            if providers_file.exists():
                discovered = self._load_providers_from_file(providers_file)
                providers.extend(discovered)

        return providers

    def _load_providers_from_file(self, file: Path) -> list[type]:
        """
        Load provider classes from a Python file.

        Args:
            file: Path to the providers file.

        Returns:
            List of provider classes found in the file.
        """
        spec = importlib.util.spec_from_file_location("bootstrap.providers", file)
        if spec is None or spec.loader is None:
            return []

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for a 'providers' list in the module
        if hasattr(module, "providers"):
            return module.providers

        return []
