from elyx.logging.log_manager import LogManager
from elyx.support.service_provider import ServiceProvider


class LogServiceProvider(ServiceProvider):
    def register(self) -> None:
        """Register the log manager as a singleton."""
        self.app.singleton("log", lambda: LogManager(self.app))
