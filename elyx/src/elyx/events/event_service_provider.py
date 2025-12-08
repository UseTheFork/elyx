from elyx.events.dispatcher import Dispatcher
from elyx.support.service_provider import ServiceProvider


class EventServiceProvider(ServiceProvider):
    def register(self) -> None:
        """Register the event dispatcher as a singleton."""
        self.app.singleton("events", lambda: Dispatcher(self.app))
