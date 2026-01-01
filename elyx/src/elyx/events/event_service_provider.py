from elyx.events import Dispatcher
from elyx.support import ServiceProvider


class EventServiceProvider(ServiceProvider):
    def boot(self) -> None:
        pass

    def register(self) -> None:
        """Register the event dispatcher as a singleton."""
        self.app.singleton("events", lambda: Dispatcher(self.app))
