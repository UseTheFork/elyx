import inspect
from collections.abc import Callable
from typing import Any, Dict, TypeVar

from elyx.contracts.container_contract import ContainerContract
from elyx.exceptions import CircularDependencyException, EntryNotFoundException

T = TypeVar("T")


class Container(ContainerContract):
    """
    Dependency injection container.
    """

    def __init__(self):
        """Initialize the container with empty registries."""
        # An array of the types that have been resolved.
        self._resolved: Dict[str, bool] = {}

        # The container's bindings.
        self._bindings: Dict[str, dict[str, Any]] = {}

        # The container's method bindings.
        self._method_bindings: Dict[str, Callable] = {}

        # The container's shared instances.
        self._instances: Dict[str, Any] = {}

        # The registered type aliases.
        self._aliases: Dict[str, str] = {}

        # The extension closures for services.
        self._before_resolving_callbacks: Dict[str, list[Callable]] = {}
        self._resolving_callbacks: Dict[str, list[Callable]] = {}
        self._after_resolving_callbacks: Dict[str, list[Callable]] = {}
        self._global_before_resolving_callbacks: list[Callable] = []
        self._global_resolving_callbacks: list[Callable] = []
        self._global_after_resolving_callbacks: list[Callable] = []

    def bound(self, abstract: str | type[T]) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return abstract_str in self._bindings or abstract_str in self._instances or self._is_alias(abstract_str)

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

        Raises:
            EntryNotFoundException: No entry was found for this identifier.
            CircularDependencyException: Circular dependency detected.
            ContainerException: Error while retrieving the entry.
        """
        try:
            return await self.make(id)
        except Exception as e:
            if self.has(id) or isinstance(e, CircularDependencyException):
                raise e

            code = e.args[0] if e.args and isinstance(e.args[0], int) else 0
            raise EntryNotFoundException(self._normalize_abstract(id), code, e)

    def resolved(self, abstract: str | type[T]) -> bool:
        """
        Determine if the given abstract type has been resolved.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)

        if self._is_alias(abstract_str):
            abstract_str = self._get_alias(abstract_str)

        return abstract_str in self._resolved or abstract_str in self._instances

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
        abstract_str = self._normalize_abstract(abstract)

        # Resolve alias if present
        if self._is_alias(abstract_str):
            abstract_str = self._get_alias(abstract_str)

        # If we have a shared instance, return it
        if abstract_str in self._instances:
            return self._instances[abstract_str]

        # Fire before resolving callbacks
        await self._fire_before_resolving_callbacks(abstract_str, parameters)

        # Get the concrete implementation
        concrete = self._get_concrete(abstract_str)

        # Build the instance
        if self._is_buildable(concrete):
            instance = await self._build(concrete, parameters)
        else:
            instance = await self.make(concrete, parameters)

        # Fire resolving callbacks
        await self._fire_resolving_callbacks(abstract_str, instance)

        # If this is a shared binding, store the instance
        if self._is_shared(abstract_str):
            self._instances[abstract_str] = instance

        # Mark as resolved
        self._resolved[abstract_str] = True

        # Fire after resolving callbacks
        await self._fire_after_resolving_callbacks(abstract_str, instance)

        return instance

    def _get_concrete(self, abstract: str) -> Any:
        """
        Get the concrete type for a given abstract.

        Args:
            abstract: Abstract type identifier.

        Returns:
            Concrete implementation.
        """
        if abstract not in self._bindings:
            return abstract

        return self._bindings[abstract]["concrete"]

    def _is_buildable(self, concrete: Any) -> bool:
        """
        Determine if the given concrete is buildable.

        Args:
            concrete: Concrete implementation.

        Returns:
            bool
        """
        return callable(concrete) or isinstance(concrete, type)

    def _is_shared(self, abstract: str) -> bool:
        """
        Determine if a given type is shared.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        return abstract in self._bindings and self._bindings[abstract].get("shared", False)

    async def _build(self, concrete: Any, parameters: dict[str, Any] | None = None) -> Any:
        """
        Instantiate a concrete instance of the given type.

        Args:
            concrete: Concrete implementation.
            parameters: Parameters to pass to the constructor.

        Returns:
            Instance of the concrete type.
        """
        if parameters is None:
            parameters = {}

        # If concrete is a callable (factory function), call it
        if callable(concrete) and not isinstance(concrete, type):
            result = concrete(self, **parameters)
            if inspect.iscoroutine(result):
                return await result
            return result

        # If concrete is a class, instantiate it with dependency injection
        if isinstance(concrete, type):
            # Get constructor signature
            sig = inspect.signature(concrete.__init__)
            resolved_params = {}

            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                # Use provided parameter if available
                if param_name in parameters:
                    resolved_params[param_name] = parameters[param_name]
                # Try to resolve from type hint
                elif param.annotation != inspect.Parameter.empty and param.annotation != type(None):
                    try:
                        resolved_params[param_name] = await self.make(param.annotation)
                    except Exception:
                        # If resolution fails and there's a default, use it
                        if param.default != inspect.Parameter.empty:
                            resolved_params[param_name] = param.default
                        # Otherwise, skip this parameter
                # Use default value if available
                elif param.default != inspect.Parameter.empty:
                    resolved_params[param_name] = param.default

            return concrete(**resolved_params)

        return concrete

    async def _fire_before_resolving_callbacks(self, abstract: str, parameters: dict[str, Any] | None) -> None:
        """
        Fire all of the before resolving callbacks.

        Args:
            abstract: Abstract type identifier.
            parameters: Parameters being passed to make.
        """
        await self._fire_callback_array(abstract, parameters, self._global_before_resolving_callbacks)
        await self._fire_callback_array(abstract, parameters, self._before_resolving_callbacks.get(abstract, []))

    async def _fire_resolving_callbacks(self, abstract: str, instance: Any) -> None:
        """
        Fire all of the resolving callbacks.

        Args:
            abstract: Abstract type identifier.
            instance: The resolved instance.
        """
        await self._fire_callback_array(abstract, instance, self._global_resolving_callbacks)
        await self._fire_callback_array(abstract, instance, self._resolving_callbacks.get(abstract, []))

    async def _fire_after_resolving_callbacks(self, abstract: str, instance: Any) -> None:
        """
        Fire all of the after resolving callbacks.

        Args:
            abstract: Abstract type identifier.
            instance: The resolved instance.
        """
        await self._fire_callback_array(abstract, instance, self._global_after_resolving_callbacks)
        await self._fire_callback_array(abstract, instance, self._after_resolving_callbacks.get(abstract, []))

    async def _fire_callback_array(self, abstract: str, object: Any, callbacks: list[Callable]) -> None:
        """
        Fire an array of callbacks with an object.

        Args:
            abstract: Abstract type identifier.
            object: Object to pass to callbacks.
            callbacks: Array of callbacks to fire.
        """
        for callback in callbacks:
            result = callback(object, self)
            if inspect.iscoroutine(result):
                await result

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
        if parameters is None:
            parameters = {}

        # Handle string format 'Class@method'
        if isinstance(callback, str):
            if "@" in callback:
                class_name, method_name = callback.split("@", 1)
            else:
                class_name = callback
                method_name = default_method or "__invoke__"
            
            # Resolve the class instance
            instance = await self.make(class_name)
            callback = getattr(instance, method_name)

        # Get the callback signature
        sig = inspect.signature(callback)
        resolved_params = {}

        for param_name, param in sig.parameters.items():
            # Use provided parameter if available
            if param_name in parameters:
                resolved_params[param_name] = parameters[param_name]
            # Try to resolve from type hint
            elif param.annotation != inspect.Parameter.empty and param.annotation != type(None):
                try:
                    resolved_params[param_name] = await self.make(param.annotation)
                except Exception:
                    # If resolution fails and there's a default, use it
                    if param.default != inspect.Parameter.empty:
                        resolved_params[param_name] = param.default
            # Use default value if available
            elif param.default != inspect.Parameter.empty:
                resolved_params[param_name] = param.default

        # Call the callback with resolved parameters
        result = callback(**resolved_params)
        if inspect.iscoroutine(result):
            return await result
        return result

    def resolved(self, abstract: str | type[T]) -> bool:
        """
        Determine if the given abstract type has been resolved.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)

        if self._is_alias(abstract_str):
            abstract_str = self._get_alias(abstract_str)

        return abstract_str in self._resolved or abstract_str in self._instances

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

