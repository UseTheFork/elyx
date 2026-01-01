import importlib.util
import inspect
from pathlib import Path
from typing import TYPE_CHECKING

from elyx.contracts.foundation import Bootstrapper
from elyx.support import ServiceProvider

if TYPE_CHECKING:
    from elyx.foundation import Application


class RegisterProviders(Bootstrapper):
    _bootstrap_provider_path: Path | None = None
    _merge: list[type] = []

    @staticmethod
    def merge(providers: list[type], bootstrap_provider_path: Path | None = None) -> None:
        """
        Merge the given providers into the provider configuration before registration.

        Args:
            providers: List of provider classes to merge.
            bootstrap_provider_path: Optional path to bootstrap providers file.
        """
        RegisterProviders._bootstrap_provider_path = bootstrap_provider_path
        # Merge providers, removing duplicates and None values
        merged = RegisterProviders._merge + providers
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for provider in merged:
            if provider is not None and provider not in seen:
                seen.add(provider)
                unique.append(provider)
        RegisterProviders._merge = unique

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

    def bootstrap(self, app: Application) -> None:
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
            provider = app.make(provider_class, app=app)

            # Call the register method if it exists
            if hasattr(provider, "register") and callable(provider.register):
                provider.register()
