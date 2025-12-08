
from abc import ABC, abstractmethod
from typing import Any, Callable


class Dispatcher(ABC):
    """Event dispatcher contract."""

    @abstractmethod
    async def listen(self, events: str | list[str] | Callable, listener: str | Callable | None = None) -> None:
        """
        Register an event listener with the dispatcher.

        Args:
            events: Event name(s) or closure.
            listener: Listener callable or class name.
        """
        pass

    @abstractmethod
    def has_listeners(self, event_name: str) -> bool:
        """
        Determine if a given event has listeners.

        Args:
            event_name: The event name.

        Returns:
            True if event has listeners, False otherwise.
        """
        pass

    @abstractmethod
    async def subscribe(self, subscriber: object | str) -> None:
        """
        Register an event subscriber with the dispatcher.

        Args:
            subscriber: Subscriber instance or class name.
        """
        pass

    @abstractmethod
    async def until(self, event: str | object, payload: Any = None) -> Any:
        """
        Dispatch an event until the first non-null response is returned.

        Args:
            event: Event name or object.
            payload: Event payload.

        Returns:
            First non-null response from listeners.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def push(self, event: str, payload: list[Any] | None = None) -> None:
        """
        Register an event and payload to be fired later.

        Args:
            event: Event name.
            payload: Event payload.
        """
        pass

    @abstractmethod
    async def flush(self, event: str) -> None:
        """
        Flush a set of pushed events.

        Args:
            event: Event name.
        """
        pass

    @abstractmethod
    def forget(self, event: str) -> None:
        """
        Remove a set of listeners from the dispatcher.

        Args:
            event: Event name.
        """
        pass

    @abstractmethod
    def forget_pushed(self) -> None:
        """Forget all of the queued listeners."""
        pass
