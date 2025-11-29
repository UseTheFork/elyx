from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class ContainerContract(ABC):
    @abstractmethod
    async def get(self, id: str | type[T]):
        """
        Finds an entry of the container by its identifier and returns it.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            Entry.

        Raises:
            NotFoundExceptionInterface: No entry was found for this identifier.
            ContainerExceptionInterface: Error while retrieving the entry.
        """
        pass

    @abstractmethod
    def has(self, id: str | type[T]) -> bool:
        """
        Returns true if the container can return an entry for the given identifier.
        Returns false otherwise.

        `has(id)` returning true does not mean that `get(id)` will not throw an exception.
        It does however mean that `get(id)` will not throw a `NotFoundExceptionInterface`.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            bool
        """
        pass

    @abstractmethod
    def bound(self, abstract: str | type[T]) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        pass

    @abstractmethod
    def alias(self, abstract: str | type[T], alias: str) -> None:
        """
        Alias a type to a different name.

        Args:
            abstract: Abstract type identifier.
            alias: Alias name.

        Raises:
            LogicError: If aliasing fails.
        """
        pass

    @abstractmethod
    def bind(
        self,
        abstract: str | type[T] | Callable,
        concrete: str | type[T] | Callable | None = None,
        shared: bool = False,
    ) -> None:
        """
        Register a binding with the container.

        Args:
            abstract: Abstract type identifier or closure.
            concrete: Concrete implementation or closure.
            shared: Whether the binding should be shared (singleton).
        """
        pass

    @abstractmethod
    def singleton(
        self,
        abstract: str | type[T] | Callable,
        concrete: str | type[T] | Callable | None = None,
    ) -> None:
        """
        Register a shared binding in the container.

        Args:
            abstract: Abstract type identifier or closure.
            concrete: Concrete implementation or closure.
        """
        pass

    @abstractmethod
    def flush(self) -> None:
        """
        Flush the container of all bindings and resolved instances.
        """
        pass

    @abstractmethod
    async def make(self, abstract: str | type[T], parameters: dict[str, Any] | None = None) -> T | Any:
        """
        Resolve the given type from the container.

        Args:
            abstract: Abstract type identifier or class.
            parameters: Parameters to pass to the constructor.

        Returns:
            Resolved instance.

        Raises:
            BindingResolutionException: If binding resolution fails.
        """
        pass

    @abstractmethod
    async def call(
        self,
        callback: Callable | str,
        parameters: dict[str, Any] | None = None,
        default_method: str | None = None,
    ) -> Any:
        """
        Call the given Closure / class@method and inject its dependencies.

        Args:
            callback: Callable or string in format 'Class@method'.
            parameters: Parameters to pass to the callback.
            default_method: Default method name if not specified in callback string.

        Returns:
            Result of the callback.
        """
        pass

    @abstractmethod
    def resolved(self, abstract: str | type[T]) -> bool:
        """
        Determine if the given abstract type has been resolved.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        pass

    # @abstractmethod
    # def before_resolving(self, abstract: str | type[T] | Callable, callback: Callable | None = None) -> None:
    #     """
    #     Register a new before resolving callback.

    #     Args:
    #         abstract: Abstract type identifier or closure.
    #         callback: Callback to execute before resolving.
    #     """
    #     pass

    # @abstractmethod
    # def resolving(self, abstract: str | type[T] | Callable, callback: Callable | None = None) -> None:
    #     """
    #     Register a new resolving callback.

    #     Args:
    #         abstract: Abstract type identifier or closure.
    #         callback: Callback to execute during resolving.
    #     """
    #     pass

    # @abstractmethod
    # def after_resolving(self, abstract: str | type[T] | Callable, callback: Callable | None = None) -> None:
    #     """
    #     Register a new after resolving callback.

    #     Args:
    #         abstract: Abstract type identifier or closure.
    #         callback: Callback to execute after resolving.
    #     """
    #     pass
