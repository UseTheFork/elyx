# example/app/providers/app_service_provider.py
from elyx.support.service_provider import ServiceProvider


class AppServiceProvider(ServiceProvider):
    """Application service provider."""

    def register(self) -> None:
        """Register application services."""
        # Bind services to the container
        pass
