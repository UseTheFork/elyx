from abc import abstractmethod
from typing import Any, Callable, Optional, TypeVar, Union

from elyx.contracts.container.container_interface import ContainerInterface

T = TypeVar("T")


class Container(ContainerInterface):
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
        env: str | list[str] | None = None,
    ) -> None:
        """
        Register a binding with the container.

        Args:
            abstract: Abstract type identifier or closure.
            concrete: Concrete implementation or closure.
            shared: Whether the binding should be shared (singleton).
            env: The environment(s) for which the binding is active.
        """
        pass

    @abstractmethod
    def bind_if(
        self,
        abstract,
        concrete=None,
        shared: bool = False,
    ) -> None:
        """
        Register a binding with the container if it hasn't already been registered.

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
    def singleton_if(
        self,
        abstract,
        concrete=None,
    ) -> None:
        """
        Register a shared binding in the container if it hasn't already been registered.

        Args:
            abstract: Abstract type identifier or closure.
            concrete: Concrete implementation or closure.
        """
        pass

    @abstractmethod
    def instance(self, abstract, instance: T) -> T:
        """
        Register an existing instance as shared in the container.

        Args:
            abstract: Abstract type identifier.
            instance: The instance to register.

        Returns:
            The registered instance.
        """
        pass

    @abstractmethod
    def flush(self) -> None:
        """
        Flush the container of all bindings and resolved instances.
        """
        pass

    @abstractmethod
    def forget_instance(self, abstract) -> None:
        """
        Remove a resolved instance from the instance cache.

        Args:
            abstract: The abstract type to forget.
        """
        pass

    @abstractmethod
    def forget_instances(self) -> None:
        """Clear all of the instances from the container."""
        pass

    @abstractmethod
    def forget_scoped_instances(self) -> None:
        """Clear all of the scoped instances from the container."""
        pass

    @abstractmethod
    def make(self, abstract, **kwargs) -> T | Any:
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
    def make_with(self, abstract, **kwargs) -> T | Any:
        """
        Resolve the given type from the container with parameters.

        Args:
            abstract: Abstract type identifier or class.
            **kwargs: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
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

    @abstractmethod
    def is_shared(self, abstract) -> bool:
        """
        Determine if a given type is shared (singleton).

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        pass

    @abstractmethod
    def is_scoped(self, abstract) -> bool:
        """
        Determine if a given type is scoped.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        pass

    @abstractmethod
    def factory(self, abstract) -> Callable:
        """
        Resolve the given type from the container as a factory.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            A callable that will resolve the abstract type.
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

    @abstractmethod
    def resolve_environment_using(self, callback: Optional[Callable]) -> None:
        """
        Set the callback which determines the current container environment.

        Args:
            callback: The callback to resolve the environment.
        """
        pass

    @abstractmethod
    def current_environment_is(self, environments: Union[str, list[str]]) -> bool:
        """
        Determine the environment for the container.

        Args:
            environments: The environment(s) to check against.

        Returns:
            True if the current environment matches, False otherwise.
        """
        pass
