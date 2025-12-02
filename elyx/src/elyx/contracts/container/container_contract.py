from abc import abstractmethod
from typing import Any, TypeVar

from elyx.contracts.container.container_interface_contract import ContainerInterfaceContract

T = TypeVar("T")


class ContainerContract(ContainerInterfaceContract):
    @abstractmethod
    def bound(self, abstract) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        pass

    @abstractmethod
    def alias(self, abstract, alias) -> None:
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
        abstract,
        concrete=None,
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
        abstract,
        concrete=None,
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
    async def make(self, abstract, parameters: dict[str, Any] | None = None) -> T | Any:
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
        callback,
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
    def resolved(self, abstract) -> bool:
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
