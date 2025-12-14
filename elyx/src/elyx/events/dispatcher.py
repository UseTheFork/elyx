import inspect
from typing import Any, Callable

from elyx.container.container import Container
from elyx.contracts.container.container import Container as ContainerContract
from elyx.contracts.events.dispatcher import Dispatcher as DispatcherContract
from elyx.support import Arr


class Dispatcher(DispatcherContract):
    def __init__(self, container: ContainerContract | None = None):
        if container is None:
            container = Container()
        self.container = container

        # The registered event listeners: {event_name: [listener1, listener2, ...]}
        self.listeners = {}

        # The wildcard listeners: [(pattern, listener), ...]
        self.wildcards = []

    async def listen(self, events: str | list[str] | Callable, listener: str | Callable | None = None) -> None:
        """
        Register an event listener with the dispatcher.

        Args:
            events: Event name(s) or closure.
            listener: Listener callable or class name.
        """
        # Case 1: listen(callback) - wildcard listener
        if callable(events) and listener is None:
            self.wildcards.append(("*", events))
            return

        # Case 2: listen("event.name", callback) or listen(["event1", "event2"], callback)
        # Normalize events to list
        if isinstance(events, str):
            event_list = [events]
        elif isinstance(events, list):
            event_list = events
        else:
            return

        for event in event_list:
            if event not in self.listeners:
                self.listeners[event] = []
            self.listeners[event].append(listener)

    def has_listeners(self, event_name: str) -> bool:
        """
        Determine if a given event has listeners.

        Args:
            event_name: The event name.

        Returns:
            True if event has listeners, False otherwise.
        """
        return event_name in self.listeners and len(self.listeners[event_name]) > 0

    async def _resolve_subscriber(self, subscriber: object | str) -> object:
        """
        Resolve the subscriber instance.

        Args:
            subscriber: Subscriber instance or class name.

        Returns:
            Resolved subscriber instance.
        """
        if isinstance(subscriber, str):
            return await self.container.make(subscriber)
        return subscriber

    async def push(self, event: str, payload: list[Any] | None = None) -> None:
        """
        Register an event and payload to be fired later.

        Args:
            event: Event name.
            payload: Event payload.
        """

        async def dispatch_pushed():
            await self.dispatch(event, payload)

        await self.listen(f"{event}_pushed", dispatch_pushed)

    async def subscribe(self, subscriber) -> None:
        """
        Register an event subscriber with the dispatcher.

        Args:
            subscriber: Subscriber instance or class name.
        """

        subscriber = await self._resolve_subscriber(subscriber)
        events = subscriber.subscribe(self)

        if isinstance(events, dict):
            for event, listeners in events.items():
                for listener in Arr.wrap(listeners):
                    if isinstance(listener, str) and hasattr(subscriber, listener):
                        await self.listen(event, getattr(subscriber, listener))
                        continue
                    await self.listen(event, listener)

    async def flush(self, event: str) -> None:
        """
        Flush a set of pushed events.

        Args:
            event: Event name.
        """
        await self.dispatch(f"{event}_pushed")

    def forget(self, event: str) -> None:
        """
        Remove a set of listeners from the dispatcher.

        Args:
            event: Event name.
        """
        if event in self.listeners:
            del self.listeners[event]

    def forget_pushed(self) -> None:
        """Forget all of the queued listeners."""
        # Remove all listeners that end with '_pushed'
        pushed_events = [key for key in self.listeners.keys() if key.endswith("_pushed")]
        for event in pushed_events:
            del self.listeners[event]

    async def until(self, event: str | object, payload: Any = None) -> Any:
        """
        Dispatch an event until the first non-null response is returned.

        Args:
            event: Event name or object.
            payload: Event payload.

        Returns:
            First non-null response from listeners.
        """
        return await self.dispatch(event, payload, halt=True)

    async def dispatch(self, event: str | object, payload: Any = None, halt: bool = False) -> list[Any] | None:
        """
        Dispatch an event and call the listeners.

        Args:
            event: Event name or object.
            payload: Event payload.
            halt: Whether to halt on first non-null response.

        Returns:
            Array of responses or None if halted.
        """
        # Get event name from object if needed
        event_name = event if isinstance(event, str) else event.__class__.__name__

        # Get all listeners for this event
        listeners = self._get_listeners(event_name)

        responses = []

        # Execute listeners sequentially
        for listener in listeners:
            response = await self._invoke_listener(listener, event, payload)

            # If halting and we got a non-null response, return it immediately
            if halt and response is not None:
                return response

            responses.append(response)

        return None if halt else responses

    def _get_listeners(self, event_name: str) -> list:
        """
        Get all listeners for a given event, including wildcards.

        Args:
            event_name: The event name.

        Returns:
            List of listeners.
        """
        listeners = []

        # Add specific listeners
        if event_name in self.listeners:
            listeners.extend(self.listeners[event_name])

        # Add wildcard listeners that match
        for pattern, listener in self.wildcards:
            if self._matches_wildcard(event_name, pattern):
                listeners.append(listener)

        return listeners

    def _matches_wildcard(self, event_name: str, pattern: str) -> bool:
        """
        Check if an event name matches a wildcard pattern.

        Args:
            event_name: The event name.
            pattern: The wildcard pattern (e.g., "order.*" or "*").

        Returns:
            True if matches, False otherwise.
        """
        if pattern == "*":
            return True

        # Convert wildcard pattern to regex
        import re

        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", event_name))

    async def _invoke_listener(self, listener: Callable | str, event: str | object, payload: Any) -> Any:
        """
        Invoke a single event listener.

        Args:
            listener: The listener callable or string.
            event: Event name or object.
            payload: Event payload.

        Returns:
            Response from the listener.
        """
        # Resolve string listeners from container
        if isinstance(listener, str):
            listener = await self.container.make(listener)

        # Call the listener
        if inspect.iscoroutinefunction(listener):
            return await listener(event, payload)
        else:
            return listener(event, payload)
