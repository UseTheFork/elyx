import inspect
import re
from typing import Any, Callable, TypeVar

from elyx.container.container import Container
from elyx.contracts.container.container import Container as ContainerContract
from elyx.contracts.events.dispatcher import Dispatcher as DispatcherContract
from elyx.support import Arr
from elyx.support.str import Str

T = TypeVar("T")


class Dispatcher(DispatcherContract):
    def __init__(self, container: ContainerContract | None = None):
        if container is None:
            container = Container()
        self.container = container

        # The registered event listeners: {event_name: [listener1, listener2, ...]}
        self.listeners = {}

        # The wildcard listeners: [(pattern, listener), ...]
        self.wildcards = []

        # Event deferring state
        self.deferring_events = False
        self.deferred_events = []
        self.events_to_defer = None

    def listen(
        self,
        events,
        listener=None,
    ) -> None:
        """
        Register an event listener with the dispatcher.

        Args:
            events: Event name(s), class type(s), or closure.
            listener: Listener callable or class name.
        """
        # Case 1: listen(callback) - wildcard listener
        if callable(events) and not isinstance(events, type) and listener is None:
            self.wildcards.append(("*", events))
            return

        # Case 2: listen("event.name", callback) or listen(["event1", "event2"], callback)
        # or listen(EventClass, callback)
        # Normalize events to list
        if isinstance(events, str):
            event_list = [events]
        elif isinstance(events, type):
            # Normalize class type to string using container's method
            event_list = [Str.class_to_string(events)]
        elif isinstance(events, list):
            # Normalize each item in the list
            event_list = []
            for event in events:
                if isinstance(event, type):
                    event_list.append(Str.class_to_string(event))
                else:
                    event_list.append(event)
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

    def _resolve_subscriber(self, subscriber: object | str) -> object:
        """
        Resolve the subscriber instance.

        Args:
            subscriber: Subscriber instance or class name.

        Returns:
            Resolved subscriber instance.
        """
        if isinstance(subscriber, str):
            return self.container.make(subscriber)
        return subscriber

    def push(self, event: str, payload: list[Any] | None = None) -> None:
        """
        Register an event and payload to be fired later.

        Args:
            event: Event name.
            payload: Event payload.
        """

        async def dispatch_pushed(pushed_event, pushed_payload):
            # Unpack the payload if it's a list, otherwise pass as-is
            if isinstance(payload, list):
                await self.dispatch(event, *payload)
            else:
                await self.dispatch(event, payload)

        self.listen(f"{event}_pushed", dispatch_pushed)

    async def subscribe(self, subscriber) -> None:
        """
        Register an event subscriber with the dispatcher.

        Args:
            subscriber: Subscriber instance or class name.
        """

        subscriber = self._resolve_subscriber(subscriber)
        events = subscriber.subscribe(self)

        if isinstance(events, dict):
            for event, listeners in events.items():
                for listener in Arr.wrap(listeners):
                    if isinstance(listener, str) and hasattr(subscriber, listener):
                        self.listen(event, getattr(subscriber, listener))
                        continue
                    self.listen(event, listener)

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

        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", event_name))

    def _parse_class_callable(self, listener: str) -> tuple[str, str]:
        """
        Parse the class listener into class and method.

        Args:
            listener: Listener string in format 'Class:method'.

        Returns:
            Tuple of (class_name, method_name).
        """
        return Str.parse_callback(listener, "handle")

    def _create_class_callable(self, listener: str | list) -> Callable:
        """
        Create a callable from a class-based listener.

        Args:
            listener: Listener string or array [class-string, string].

        Returns:
            Callable that will invoke the listener method.
        """
        if isinstance(listener, list):
            class_name, method = listener
        elif isinstance(listener, type):
            # Convert class type to string representation
            class_name = Str.class_to_string(listener)
            method = "handle"
        else:
            class_name, method = self._parse_class_callable(listener)

        # Check if method exists, otherwise use __call__
        listener_instance = self.container.make(class_name)
        if not hasattr(listener_instance, method):
            method = "__call__"

        return getattr(listener_instance, method)

    def _create_class_listener(self, listener, wildcard: bool = False) -> Callable:
        """
        Create a class based listener using the IoC container.

        Args:
            listener: Listener string or array [class-string, string].
            wildcard: Whether this is a wildcard listener.

        Returns:
            Closure that will invoke the listener.
        """

        def wrapper(event, payload):
            if wildcard:
                callable_obj = self._create_class_callable(listener)
                return callable_obj(event, payload)
            callable_obj = self._create_class_callable(listener)
            return callable_obj(*payload) if isinstance(payload, list) else callable_obj(payload)

        return wrapper

    def make_listener(self, listener: Callable | str | list, wildcard: bool = False) -> Callable:
        """
        Register an event listener with the dispatcher.

        Args:
            listener: Closure, string, or array [class-string, string].
            wildcard: Whether this is a wildcard listener.

        Returns:
            Closure that will invoke the listener.
        """
        if isinstance(listener, str):
            return self._create_class_listener(listener, wildcard)

        if isinstance(listener, list) and len(listener) > 0 and isinstance(listener[0], str):
            return self._create_class_listener(listener, wildcard)

        if isinstance(listener, type):
            return self._create_class_listener(listener, wildcard)

        def wrapper(event, payload):
            if wildcard:
                return listener(event, payload)
            # For direct callables, they expect (event, payload)
            # This wrapper is only for direct callables, not class-based ones
            return listener(event, payload)

        return wrapper

    def _prepare_listeners(self, event_name: str) -> list:
        """
        Prepare the listeners for a given event.

        Args:
            event_name: The event name.

        Returns:
            List of listeners.
        """
        if event_name in self.listeners:
            return [self.make_listener(listener) for listener in self.listeners[event_name]]
        return []

    def _get_wildcard_listeners(self, event_name: str) -> list:
        """
        Get the wildcard listeners for the event.

        Args:
            event_name: The event name.

        Returns:
            List of wildcard listeners that match.
        """
        wildcard_listeners = []
        for pattern, listener in self.wildcards:
            if self._matches_wildcard(event_name, pattern):
                wildcard_listeners.append(listener)
        return wildcard_listeners

    def get_listeners(self, event_name: str) -> list:
        """
        Get all of the listeners for a given event name.

        Args:
            event_name: The event name.

        Returns:
            List of listeners.
        """
        listeners = []
        listeners.extend(self._prepare_listeners(event_name))

        # TODO: Add wildcard cache support
        # listeners.extend(self.wildcards_cache.get(event_name, self._get_wildcard_listeners(event_name)))
        listeners.extend(self._get_wildcard_listeners(event_name))

        # TODO: Add interface listeners support
        # if class_exists(event_name):
        #     return self._add_interface_listeners(event_name, listeners)

        return listeners

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
            result = await listener(event, payload)
        else:
            result = listener(event, payload)

        # If the result is a coroutine, await it
        if inspect.iscoroutine(result):
            result = await result

        return result

    def _should_defer_event(self, event: str) -> bool:
        """
        Determine if the given event should be deferred.

        Args:
            event: Event name.

        Returns:
            True if event should be deferred, False otherwise.
        """
        deferring_events = getattr(self, "deferring_events", False)
        events_to_defer = getattr(self, "events_to_defer", None)

        return deferring_events and (events_to_defer is None or event in events_to_defer)

    async def _invoke_listeners(
        self, event: str | object, payload: Any, listeners: list, halt: bool = False
    ) -> list[Any] | None:
        """
        Invoke a set of listeners.

        Args:
            event: Event name or object.
            payload: Event payload.
            listeners: List of listeners to invoke.
            halt: Whether to halt on first non-null response.

        Returns:
            Array of responses or None if halted.
        """
        responses = []

        for listener in listeners:
            response = await self._invoke_listener(listener, event, payload)

            # If halting and we got a non-null response, return it immediately
            if halt and response is not None:
                return response

            # If listener returns False, stop propagation
            if response is False:
                responses.append(response)
                break

            responses.append(response)

        return None if halt else responses

    async def dispatch(self, event, payload: Any = None, halt: bool = False) -> list[Any] | None:
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
        if isinstance(event, str):
            event_name = event
        elif isinstance(event, type):
            # It's a class type
            event_name = Str.class_to_string(event)
        else:
            # It's an instance, get its class
            event_name = Str.class_to_string(type(event))

        # Check if we should defer this event
        if self._should_defer_event(event_name):
            self.deferred_events.append((event, payload, halt))
            return None if halt else []

        # Get all listeners for this event
        listeners = self.get_listeners(event_name)

        return await self._invoke_listeners(event, payload, listeners, halt)

    async def defer(self, callback, events: list[str | type[T]] | None = None):
        """
        Execute the given callback while deferring events, then dispatch all deferred events.

        Args:
            callback: Callable to execute while deferring events.
            events: Optional list of event names or types to defer (None means defer all).

        Returns:
            Result of the callback.
        """

        was_deferring = getattr(self, "deferring_events", False)
        previous_deferred_events = getattr(self, "deferred_events", [])
        previous_events_to_defer = getattr(self, "events_to_defer", None)

        self.deferring_events = True
        self.deferred_events = []
        # Normalize event types to strings
        if events is not None:
            self.events_to_defer = [
                Str.class_to_string(event) if isinstance(event, type) else event for event in events
            ]
        else:
            self.events_to_defer = None

        try:
            result = await callback() if inspect.iscoroutinefunction(callback) else callback()

            self.deferring_events = False

            for args in self.deferred_events:
                await self.dispatch(*args)

            return result
        finally:
            self.deferring_events = was_deferring
            self.deferred_events = previous_deferred_events
            self.events_to_defer = previous_events_to_defer
