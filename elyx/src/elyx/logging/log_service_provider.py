from elyx.logging import LogManager
from elyx.support import ServiceProvider


class LogServiceProvider(ServiceProvider):
    def register(self) -> None:
        """Register the log manager as a singleton."""
        self.app.singleton("log", lambda: LogManager(self.app))
