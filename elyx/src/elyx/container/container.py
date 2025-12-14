from typing import Any, Callable, TypeVar, get_type_hints

from dependency_injector import containers, providers
from elyx.contracts.container.container import Container as ContainerContract
from elyx.exceptions import EntryNotFoundException

T = TypeVar("T")


class Container(ContainerContract):
    """
    Dependency injection container wrapping dependency-injector.
    """

    _instance = None

    def __init__(self):
        super().__init__()
        # Use a DynamicContainer instance for storing bindings
        self._bindings = containers.DynamicContainer()
        self._instances = {}
        self._aliases = {}
        self._shared = {}
        self._global_before_resolving_callbacks = []
        self._before_resolving_callbacks = {}
        self._global_after_resolving_callbacks = []
        self._after_resolving_callbacks = {}

    @classmethod
    def set_instance(cls, container):
        """
        Set the globally available instance of the container.

        Args:
            container: Container instance to set as singleton.

        Returns:
            The container instance.
        """
        cls._instance = container
        return container

    @classmethod
    def get_instance(cls):
        """
        Get the globally available instance of the container.

        Returns:
            Container instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def bound(self, abstract) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return hasattr(self._bindings, abstract_str) or abstract_str in self._instances or abstract_str in self._aliases

    def has(self, id: str) -> bool:
        """
        Returns true if the container can return an entry for the given identifier.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            bool
        """
        return self.bound(id)

    async def get(self, id: str) -> T | Any:
        """
        Finds an entry of the container by its identifier and returns it.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            Entry.

        Raises:
            EntryNotFoundException: If the entry is not found.
        """
        from elyx.container.exceptions import EntryNotFoundException

        try:
            return await self.make(id)
        except Exception as e:
            if self.has(id):
                raise

            raise EntryNotFoundException(id) from e

    def resolved(self, abstract) -> bool:
        """
        Determine if the given abstract type has been resolved.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)

        if self.is_alias(abstract_str):
            abstract_str = self.get_alias(abstract_str)

        return abstract_str in self._resolved or abstract_str in self._instances

    def make(self, abstract, **kwargs) -> T | Any:
        """
        Resolve the given type from the container.

        Args:
            abstract: Abstract type identifier or class.
            **kwargs: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
        """
        return self.resolve(abstract, **kwargs)

    def resolve(self, abstract, raise_events=True, **kwargs) -> T | Any:
        """
        Resolve the given type from the container.

        Args:
            abstract: Abstract type identifier or class.
            **kwargs: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
        """

        original_abstract = abstract

        abstract_str = self._normalize_abstract(abstract)
        abstract = self.get_alias(abstract_str)

        if raise_events:
            self._fire_before_resolving_callbacks(abstract_str, **kwargs)

        if not hasattr(self._bindings, abstract_str):
            # Auto-wire if it's a class
            if isinstance(original_abstract, type):
                provider = providers.Factory(original_abstract)
                setattr(self._bindings, abstract_str, provider)
            else:
                raise EntryNotFoundException(abstract_str)

        provider = getattr(self._bindings, abstract_str)

        if kwargs:
            instance = provider(**kwargs)
        else:
            instance = provider()

        # Fire after resolving callbacks
        if raise_events:
            self._fire_after_resolving_callbacks(abstract_str, instance)

        return instance

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
        if callable(abstract) and concrete is None:
            concrete = abstract
            # Try to extract return type hint as abstract
            try:
                hints = get_type_hints(abstract)
                if "return" in hints:
                    return_type = hints["return"]
                    # Handle Union types (e.g., Type1 | Type2)
                    if hasattr(return_type, "__origin__"):
                        # For Union types, use the first type
                        if hasattr(return_type, "__args__"):
                            abstract = return_type.__args__[0]
                        else:
                            abstract = return_type
                    else:
                        abstract = return_type
                else:
                    abstract = abstract.__name__
            except Exception:
                abstract = abstract.__name__

        if concrete is None:
            concrete = abstract

        abstract_str = self._normalize_abstract(abstract)

        if shared:
            provider = providers.Singleton(concrete)
            self._shared[abstract_str] = True
        else:
            provider = providers.Factory(concrete)
            self._shared[abstract_str] = False

        setattr(self._bindings, abstract_str, provider)

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
        if not self.bound(abstract):
            self.bind(abstract, concrete, shared)

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
        self.bind(abstract, concrete, shared=True)

    def is_shared(self, abstract) -> bool:
        """
        Determine if a given type is shared (singleton).

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return self._shared.get(abstract_str, False)

    def instance(self, abstract, instance: T) -> T:
        """
        Register an existing instance as shared in the container.

        Args:
            abstract: Abstract type identifier.
            instance: The instance to register.

        Returns:
            The registered instance.
        """
        abstract_str = self._normalize_abstract(abstract)

        # is_bound = self.bound(abstract_str)

        # Remove any existing alias
        if abstract_str in self._aliases:
            del self._aliases[abstract_str]

        # Store the instance
        self._instances[abstract_str] = instance

        # Create a singleton provider that returns this instance
        provider = providers.Singleton(lambda: instance)
        setattr(self._bindings, abstract_str, provider)

        # TODO: Implement rebound callbacks if needed
        # if is_bound:
        #     self.rebound(abstract_str)

        return instance

    def alias(self, abstract, alias) -> None:
        """
        Alias a type to a different name.

        Args:
            abstract: Abstract type identifier.
            alias: Alias name.
        """
        abstract_str = self._normalize_abstract(abstract)
        if not hasattr(self._bindings, abstract_str):
            raise ValueError(f"Cannot alias unbound abstract: {abstract_str}")

        provider = getattr(self._bindings, abstract_str)
        setattr(self._bindings, alias, provider)

    def is_alias(self, name: str) -> bool:
        """
        Determine if a given string is an alias.

        Args:
            name: Name to check.

        Returns:
            bool
        """
        return name in self._aliases

    def get_alias(self, abstract) -> str:
        """
        Get the alias for an abstract if available.

        Args:
            abstract: Abstract type identifier.

        Returns:
            The resolved alias or the original abstract if no alias exists.
        """
        if abstract in self._aliases:
            return self.get_alias(self._aliases[abstract])
        return abstract

    def flush(self) -> None:
        """
        Flush the container of all bindings and resolved instances.
        """
        self._bindings.reset_singletons()
        # TODO: should we fix this? should we not use dependency_injector it may be overkill here.
        # Remove all providers from _bindings
        # for attr_name in list(self._bindings.__dict__.keys()):
        #     if not attr_name.startswith("_"):
        #         delattr(self._bindings, attr_name)

    def call(
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

        if parameters is None:
            parameters = {}

        # Handle string format 'Class@method'
        if isinstance(callback, str):
            if "@" in callback:
                class_name, method_name = callback.split("@", 1)
            else:
                class_name = callback
                method_name = default_method or "__invoke__"

            instance = self.make(class_name)
            callback = getattr(instance, method_name)

        # Use dependency-injector's injection
        result = callback(**parameters)
        # if inspect.iscoroutine(result):
        #     return result
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

    def after_resolving(self, abstract, callback: Callable | None = None) -> None:
        """
        Register a new after resolving callback for all types.

        Args:
            abstract: Abstract type identifier or closure.
            callback: Callback to execute after resolving.

        Returns:
            None
        """
        # If abstract is a callable and no callback provided, it's a global callback
        if callable(abstract) and callback is None:
            self._global_after_resolving_callbacks.append(abstract)
        else:
            # Normalize abstract to string and resolve aliases
            if isinstance(abstract, str) or isinstance(abstract, type):
                abstract_str = self._normalize_abstract(abstract)
                abstract_str = self.get_alias(abstract_str)
            else:
                abstract_str = self._normalize_abstract(abstract)

            # Store callback for specific abstract type
            if abstract_str not in self._after_resolving_callbacks:
                self._after_resolving_callbacks[abstract_str] = []
            self._after_resolving_callbacks[abstract_str].append(callback)

    def _fire_callback_array(self, callbacks: list, *args) -> None:
        """
        Fire an array of callbacks with the given arguments.

        Args:
            callbacks: List of callbacks to execute.
            *args: Arguments to pass to each callback.

        Returns:
            None
        """
        for callback in callbacks:
            callback(*args)

    def _fire_after_resolving_callbacks(self, abstract: str, instance: Any) -> None:
        """
        Fire all after resolving callbacks for the given abstract type.

        Args:
            abstract: Abstract type identifier.
            instance: The resolved instance.

        Returns:
            None
        """
        self._fire_callback_array(self._global_after_resolving_callbacks, instance, self)

        if abstract in self._after_resolving_callbacks:
            self._fire_callback_array(self._after_resolving_callbacks[abstract], instance, self)

    def _fire_before_resolving_callbacks(self, abstract: str, **kwargs) -> None:
        """
        Fire all of the before resolving callbacks.

        Args:
            abstract: Abstract type identifier.
            **kwargs: Parameters being passed to the constructor.

        Returns:
            None
        """
        self._fire_callback_array(self._global_before_resolving_callbacks, abstract, kwargs, self)

        if abstract in self._before_resolving_callbacks:
            self._fire_callback_array(self._before_resolving_callbacks[abstract], abstract, kwargs, self)

    async def factory(self, abstract):
        """
        Resolve the given type from the container as a factory.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            Resolved instance.
        """
        return await self.make(abstract)

    async def make_with(self, abstract, **kwargs):
        """
        Resolve the given type from the container with parameters.

        Args:
            abstract: Abstract type identifier or class.
            **kwargs: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
        """
        return await self.make(abstract, **kwargs)

    def wrap(self, callback: Callable, parameters: dict[str, Any] | None = None) -> Callable:
        """
        Wrap the given closure such that its dependencies will be injected when executed.

        Args:
            callback: Callable to wrap.
            parameters: Parameters to pass to the callback.

        Returns:
            Wrapped callable that will inject dependencies when called.
        """
        if parameters is None:
            parameters = {}
        return lambda: self.call(callback, parameters)
