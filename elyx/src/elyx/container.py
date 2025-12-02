from typing import Any, Callable, TypeVar

from dependency_injector import containers, providers

from elyx.contracts.container.container_contract import ContainerContract

T = TypeVar("T")


class Container(containers.DynamicContainer, ContainerContract):
    """
    Dependency injection container wrapping dependency-injector.
    """

    def bound(self, abstract: str | type[T]) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return hasattr(self, abstract_str)

    def has(self, id: str | type[T]) -> bool:
        """
        Returns true if the container can return an entry for the given identifier.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            bool
        """
        return self.bound(id)

    async def get(self, id: str | type[T]) -> T | Any:
        """
        Finds an entry of the container by its identifier and returns it.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            Entry.
        """
        return await self.make(id)

    def resolved(self, abstract: str | type[T]) -> bool:
        """
        Determine if the given abstract type has been resolved.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        if not hasattr(self, abstract_str):
            return False
        provider = getattr(self, abstract_str)
        return isinstance(provider, providers.Singleton) and provider.is_provided

    async def make(self, abstract: str | type[T], **kwargs) -> T | Any:
        """
        Resolve the given type from the container.

        Args:
            abstract: Abstract type identifier or class.
            **kwargs: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
        """
        abstract_str = self._normalize_abstract(abstract)

        if not hasattr(self, abstract_str):
            # Auto-wire if it's a class
            if isinstance(abstract, type):
                provider = providers.Factory(abstract)
                setattr(self, abstract_str, provider)
            else:
                from elyx.exceptions import EntryNotFoundException

                raise EntryNotFoundException(abstract_str)

        provider = getattr(self, abstract_str)

        if kwargs:
            return provider(**kwargs)
        return provider()

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
        if callable(abstract) and concrete is None:
            concrete = abstract
            abstract = abstract.__name__

        if concrete is None:
            concrete = abstract

        abstract_str = self._normalize_abstract(abstract)

        if shared:
            provider = providers.Singleton(concrete)
        else:
            provider = providers.Factory(concrete)

        setattr(self, abstract_str, provider)

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
        self.bind(abstract, concrete, shared=True)

    def alias(self, abstract: str | type[T], alias: str) -> None:
        """
        Alias a type to a different name.

        Args:
            abstract: Abstract type identifier.
            alias: Alias name.
        """
        abstract_str = self._normalize_abstract(abstract)
        if not hasattr(self, abstract_str):
            raise ValueError(f"Cannot alias unbound abstract: {abstract_str}")

        provider = getattr(self, abstract_str)
        setattr(self, alias, provider)

    def flush(self) -> None:
        """
        Flush the container of all bindings and resolved instances.
        """
        self.reset_singletons()
        # Remove all providers
        for attr_name in list(self.__dict__.keys()):
            if not attr_name.startswith("_"):
                delattr(self, attr_name)

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
        import inspect

        if parameters is None:
            parameters = {}

        # Handle string format 'Class@method'
        if isinstance(callback, str):
            if "@" in callback:
                class_name, method_name = callback.split("@", 1)
            else:
                class_name = callback
                method_name = default_method or "__invoke__"

            instance = await self.make(class_name)
            callback = getattr(instance, method_name)

        # Use dependency-injector's injection
        result = callback(**parameters)
        if inspect.iscoroutine(result):
            return await result
        return result

    def _normalize_abstract(self, abstract: str | type[T]) -> str:
        """
        Normalize abstract type to string representation.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            String representation of the abstract type.
        """
        if isinstance(abstract, type):
            return f"{abstract.__module__}.{abstract.__qualname__}"
        return abstract

    def after_resolving(self, abstract: str | type[T] | Callable, callback: Callable | None = None) -> None:
        """
        Register a new after resolving callback for all types.

        Args:
            abstract: Abstract type identifier or closure.
            callback: Callback to execute after resolving.

        Returns:
            None
        """
        # Note: dependency-injector doesn't have built-in callback support
        # This is a placeholder to maintain API compatibility
        pass
