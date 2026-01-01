import inspect
import types
from typing import Any, Callable, TypeVar, Union, get_args, get_origin

from elyx.contracts.container import Container as ContainerContract
from elyx.exceptions import EntryNotFoundException
from elyx.support import Str

T = TypeVar("T")


class Container(ContainerContract):
    """
    Dependency injection container.
    """

    _instance = None

    def __init__(self):
        super().__init__()
        self._bindings = {}
        self._instances = {}
        self._aliases = {}
        self._resolved = {}
        self._scoped_instances = {}
        self._global_before_resolving_callbacks = []
        self._before_resolving_callbacks = {}
        self._global_resolving_callbacks = []
        self._resolving_callbacks = {}
        self._global_after_resolving_callbacks = []
        self._after_resolving_callbacks = {}
        self._rebinding_callbacks = {}
        self.environment_resolver = None

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

    def _normalize_abstract(self, abstract) -> str:
        """
        Normalize abstract type to string representation.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            String representation of the abstract type.
        """
        return Str.class_to_string(abstract)

    def bound(self, abstract) -> bool:
        """
        Determine if the given abstract type has been bound.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return (
            abstract_str in self._bindings
            or abstract_str in self._instances
            or abstract_str in self._scoped_instances
            or self.is_alias(abstract_str)
        )

    def has(self, id: str | T) -> bool:
        """
        Returns true if the container can return an entry for the given identifier.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            bool
        """
        return self.bound(id)

    def get(self, id: str | T) -> T | Any:
        """
        Finds an entry of the container by its identifier and returns it.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            Entry.

        Raises:
            EntryNotFoundException: If the entry is not found.
        """
        try:
            return self.make(id)
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

    def _build(self, concrete: Callable, **kwargs) -> Any:
        """Build an instance of the given type with dependency injection."""
        if inspect.isclass(concrete) and inspect.isabstract(concrete):
            raise EntryNotFoundException(f"Target [{self._normalize_abstract(concrete)}] is not instantiable.")

        if not inspect.isclass(concrete):
            # It's a factory/closure. We'll try to pass the container as the first
            # argument, which is a common convention in our containers.
            try:
                return concrete(self, **kwargs)
            except TypeError as e:
                # If the closure doesn't accept the container, it will raise a
                # TypeError. We can inspect the error to see if that's the case
                # and then try calling it without the container.
                if "positional argument" in str(e):
                    return concrete(**kwargs)
                raise

        try:
            # Get constructor signature
            constructor = getattr(concrete, "__init__")
            signature = inspect.signature(constructor)
        except (AttributeError, ValueError):
            # No constructor or not inspectable, just instantiate
            return concrete(**kwargs)

        dependencies = {}
        for param in signature.parameters.values():
            # Skip 'self' and variable args
            if param.name == "self" or param.kind in [param.VAR_POSITIONAL, param.VAR_KEYWORD]:
                continue

            # If a value is already provided in kwargs, use it
            if param.name in kwargs:
                dependencies[param.name] = kwargs.pop(param.name)
                continue

            # Resolve from type hint
            if param.annotation is not inspect.Parameter.empty:
                type_to_resolve = param.annotation

                # Unwrap Optional[T] to T
                origin = get_origin(type_to_resolve)
                if origin is Union or origin is types.UnionType:
                    args = get_args(type_to_resolve)
                    non_none_args = [arg for arg in args if arg is not types.NoneType]
                    if len(args) > len(non_none_args) and len(non_none_args) == 1:
                        type_to_resolve = non_none_args[0]

                # For parameters with default values, only resolve if the type is explicitly bound.
                if param.default is not inspect.Parameter.empty and not self.bound(type_to_resolve):
                    continue  # Let Python use the default value

                try:
                    # We need to handle non-class annotations gracefully, but skip built-ins
                    if inspect.isclass(type_to_resolve) and type_to_resolve.__module__ != "builtins":
                        dependencies[param.name] = self.make(type_to_resolve)
                        continue
                    elif isinstance(type_to_resolve, str):
                        dependencies[param.name] = self.make(type_to_resolve)
                        continue
                except EntryNotFoundException as e:
                    # If resolution fails, check for a default value before re-raising with context.
                    if param.default is inspect.Parameter.empty:
                        message = e.id if hasattr(e, "id") else str(e)
                        raise EntryNotFoundException(
                            f"{message} while building [{self._normalize_abstract(concrete)}]"
                        ) from e
                    # If a default value exists, we can ignore the exception and let Python use it.
                    pass

            # If there's a default value, we don't need to do anything, Python will handle it
            if param.default is not inspect.Parameter.empty:
                continue

            # If we're here, we can't resolve the dependency and it has no default.
            raise EntryNotFoundException(
                f"Unresolvable dependency: parameter '{param.name}' of type '{param.annotation}' in class '{concrete.__name__}'"
            )

        return concrete(**dependencies)

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

    def _fire_resolving_callbacks(self, abstract: str, instance: Any) -> None:
        """
        Fire all resolving callbacks for the given abstract type.

        Args:
            abstract: Abstract type identifier.
            instance: The resolved instance.

        Returns:
            None
        """
        self._fire_callback_array(self._global_resolving_callbacks, instance, self)

        if abstract in self._resolving_callbacks:
            self._fire_callback_array(self._resolving_callbacks[abstract], instance, self)

        # Fire callbacks for the concrete class and parent classes/interfaces
        if hasattr(instance, "__class__"):
            for base in instance.__class__.__mro__:
                base_str = self._normalize_abstract(base)
                # Skip if we already fired for this abstract
                if base_str != abstract and base_str in self._resolving_callbacks:
                    self._fire_callback_array(self._resolving_callbacks[base_str], instance, self)

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

    def _fire_rebinding_callbacks(self, abstract: str) -> None:
        """
        Fire all rebinding callbacks for the given abstract type.

        Args:
            abstract: Abstract type identifier.

        Returns:
            None
        """
        if abstract in self._rebinding_callbacks:
            self._fire_callback_array(self._rebinding_callbacks[abstract], abstract, self)

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
        abstract_str = self.get_alias(abstract_str)

        if raise_events:
            self._fire_before_resolving_callbacks(abstract_str, **kwargs)

        # If an instance already exists and we're not passing parameters, return it.
        if not kwargs and abstract_str in self._scoped_instances:
            return self._scoped_instances[abstract_str]

        if not kwargs and abstract_str in self._instances:
            return self._instances[abstract_str]

        binding = self._bindings.get(abstract_str)

        # If we don't have a binding, we'll attempt to auto-wire the class.
        if not binding:
            if isinstance(original_abstract, type):
                concrete = original_abstract
            else:
                raise EntryNotFoundException(abstract_str)
        else:
            concrete = binding["concrete"]

        # We're ready to build an instance of the concrete implementation.
        if callable(concrete):
            instance = self._build(concrete, **kwargs)
        else:
            instance = concrete

        # If the binding is scoped, cache the instance so it can be reused within the same scope.
        if not kwargs and self.is_scoped(abstract_str):
            self._scoped_instances[abstract_str] = instance

        # If the binding is shared and we're not passing parameters, cache the instance.
        if not kwargs and self.is_shared(abstract_str):
            self._instances[abstract_str] = instance

        self._resolved[abstract_str] = True

        # Fire resolving callbacks
        if raise_events:
            self._fire_resolving_callbacks(abstract_str, instance)

        # Fire after resolving callbacks
        if raise_events:
            self._fire_after_resolving_callbacks(abstract_str, instance)

        return instance

    def _drop_stale_instances(self, abstract: str) -> None:
        """
        Drop all of the stale instances and aliases.

        Args:
            abstract: The abstract type to drop.
        """
        if abstract in self._instances:
            del self._instances[abstract]

        if abstract in self._scoped_instances:
            del self._scoped_instances[abstract]

        if abstract in self._aliases:
            del self._aliases[abstract]

    def _get_closure_return_types(self, closure: Callable) -> list[type]:
        """
        Get the class types from the return type hint of the given closure.

        This method inspects the return type hint of a callable and extracts
        all non-built-in class types, including those within a Union.

        Args:
            closure: The callable to inspect.

        Returns:
            A list of class types found in the return type hint.
        """
        try:
            signature = inspect.signature(closure)
            return_type = signature.return_annotation
        except (ValueError, TypeError):
            return []

        if return_type is inspect.Signature.empty:
            return []

        # Handle Union types (e.g., Union[MyClass, None] or MyClass | None)
        origin = get_origin(return_type)
        if origin is Union or origin is types.UnionType:
            types_to_check = get_args(return_type)
        else:
            types_to_check = [return_type]

        # Filter for actual, non-built-in classes
        concrete_types = []
        for t in types_to_check:
            if inspect.isclass(t) and t.__module__ != "builtins":
                concrete_types.append(t)

        return concrete_types

    def _bind_based_on_closure_return_types(
        self, abstract: Callable, concrete: Callable | None = None, shared: bool = False, scoped: bool = False
    ) -> None:
        """
        Register a binding with the container based on the given closure's return types.

        Args:
            abstract: The factory closure.
            concrete: The concrete implementation (defaults to the abstract closure).
            shared: Whether the binding should be a singleton.
        """
        if concrete is None:
            concrete = abstract

        for return_type in self._get_closure_return_types(abstract):
            self.bind(return_type, concrete, shared, scoped=scoped)

    def bind(
        self,
        abstract,
        concrete=None,
        shared: bool = False,
        **kwargs,
    ) -> None:
        """
        Register a binding with the container.

        Args:
            abstract: Abstract type identifier or closure.
            concrete: Concrete implementation or closure.
            shared: Whether the binding should be shared (singleton).
        """
        scoped = kwargs.get("scoped", False)

        if callable(abstract) and not inspect.isclass(abstract):
            return self._bind_based_on_closure_return_types(abstract, concrete, shared, scoped)

        abstract_str = self._normalize_abstract(abstract)

        self._drop_stale_instances(abstract_str)

        if concrete is None:
            concrete = abstract

        # Check if this is a rebinding
        needs_rebinding = abstract_str in self._bindings

        self._bindings[abstract_str] = {"concrete": concrete, "shared": shared, "scoped": scoped}

        # Fire rebinding callbacks if this was a rebind
        if needs_rebinding and abstract_str in self._rebinding_callbacks:
            self._fire_rebinding_callbacks(abstract_str)
            # Resolve the new binding and fire resolving callbacks
            instance = self.resolve(abstract_str, raise_events=False)
            self._fire_resolving_callbacks(abstract_str, instance)

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
        self.bind_if(abstract, concrete, shared=True)

    def scoped(self, abstract, concrete=None) -> None:
        """Register a scoped binding in the container."""
        self.bind(abstract, concrete, scoped=True)

    def is_shared(self, abstract) -> bool:
        """
        Determine if a given type is shared (singleton).

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return abstract_str in self._instances or self._bindings.get(abstract_str, {}).get("shared", False)

    def is_scoped(self, abstract) -> bool:
        """
        Determine if a given type is scoped.

        Args:
            abstract: Abstract type identifier.

        Returns:
            bool
        """
        abstract_str = self._normalize_abstract(abstract)
        return abstract_str in self._scoped_instances or self._bindings.get(abstract_str, {}).get("scoped", False)

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

        # Remove any existing alias
        if abstract_str in self._aliases:
            del self._aliases[abstract_str]

        # Store the instance
        self._instances[abstract_str] = instance

        return instance

    def alias(self, abstract, alias) -> None:
        """
        Alias a type to a different name.

        Args:
            abstract: Abstract type identifier.
            alias: Alias name.
        """
        abstract_str = self._normalize_abstract(abstract)
        alias_str = self._normalize_abstract(alias)

        if not self.bound(abstract_str):
            raise ValueError(f"Cannot alias unbound abstract: {abstract_str}")

        if alias_str == abstract_str:
            raise ValueError(f"[{alias_str}] is aliased to itself.")

        self._aliases[alias_str] = abstract_str

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
        self._aliases = {}
        self._resolved = {}
        self._bindings = {}
        self._instances = {}
        self._scoped_instances = {}

    def call(
        self,
        callback,
        parameters: dict[str, Any] | None = None,
        default_method: str | None = None,
    ) -> Any:
        """
        Call the given Closure / class:method and inject its dependencies.

        Args:
            callback: Callable or string in format 'Class:method'.
            parameters: Parameters to pass to the callback.
            default_method: Default method name if not specified in callback string.

        Returns:
            Result of the callback.
        """

        if parameters is None:
            parameters = {}

        if isinstance(callback, str):
            class_name, method_name = Str.parse_callback(callback, default_method or "__invoke__")

            # If the class is not bound, try to import it dynamically
            if not self.bound(class_name):
                # Import the class dynamically
                parts = class_name.rsplit(".", 1)
                if len(parts) == 2:
                    module_name, class_attr = parts
                    try:
                        module = __import__(module_name, fromlist=[class_attr])
                        class_obj = getattr(module, class_attr)
                        instance = self.make(class_obj)
                    except (ImportError, AttributeError) as e:
                        raise ValueError(f"Cannot import class '{class_name}': {e}")
                else:
                    raise ValueError(f"Invalid class name format: '{class_name}'")
            else:
                instance = self.make(class_name)

            if method_name is None:
                raise ValueError(f"No method specified for callback '{callback}' and no default method provided")

            callback = getattr(instance, method_name)

        result = callback(**parameters)
        return result

    def before_resolving(self, abstract, callback: Callable | None = None) -> None:
        """
        Register a new before resolving callback.

        Args:
            abstract: Abstract type identifier or closure.
            callback: Callback to execute before resolving.

        Returns:
            None
        """
        # If abstract is a callable and no callback provided, it's a global callback
        if callable(abstract) and callback is None:
            self._global_before_resolving_callbacks.append(abstract)
        else:
            # Normalize abstract to string and resolve aliases
            if isinstance(abstract, str) or isinstance(abstract, type):
                abstract_str = self._normalize_abstract(abstract)
                abstract_str = self.get_alias(abstract_str)
            else:
                abstract_str = self._normalize_abstract(abstract)

            # Store callback for specific abstract type
            if abstract_str not in self._before_resolving_callbacks:
                self._before_resolving_callbacks[abstract_str] = []
            self._before_resolving_callbacks[abstract_str].append(callback)

    def resolving(self, abstract, callback: Callable | None = None) -> None:
        """
        Register a new resolving callback.

        Args:
            abstract: Abstract type identifier or closure.
            callback: Callback to execute during resolving.

        Returns:
            None
        """
        # If abstract is a callable and no callback provided, it's a global callback
        if callable(abstract) and callback is None:
            self._global_resolving_callbacks.append(abstract)
        else:
            # Normalize abstract to string and resolve aliases
            if isinstance(abstract, str) or isinstance(abstract, type):
                abstract_str = self._normalize_abstract(abstract)
                abstract_str = self.get_alias(abstract_str)
            else:
                abstract_str = self._normalize_abstract(abstract)

            # Store callback for specific abstract type
            if abstract_str not in self._resolving_callbacks:
                self._resolving_callbacks[abstract_str] = []
            self._resolving_callbacks[abstract_str].append(callback)

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

    def rebinding(self, abstract, callback: Callable) -> None:
        """
        Register a rebinding callback for the given abstract type.

        Args:
            abstract: Abstract type identifier.
            callback: Callback to execute when rebinding occurs.

        Returns:
            None
        """
        abstract_str = self._normalize_abstract(abstract)
        abstract_str = self.get_alias(abstract_str)

        if abstract_str not in self._rebinding_callbacks:
            self._rebinding_callbacks[abstract_str] = []
        self._rebinding_callbacks[abstract_str].append(callback)

    def factory(self, abstract) -> Callable:
        """
        Resolve the given type from the container as a factory.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            A callable that will resolve the abstract type.
        """
        return lambda: self.make(abstract)

    def make_with(self, abstract, **kwargs):
        """
        Resolve the given type from the container with parameters.

        Args:
            abstract: Abstract type identifier or class.
            **kwargs: Parameters to pass to the constructor.

        Returns:
            Resolved instance.
        """
        return self.make(abstract, **kwargs)

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

    def forget_instance(self, abstract) -> None:
        """
        Remove a resolved instance from the instance cache.

        Args:
            abstract: The abstract type to forget.
        """
        abstract_str = self._normalize_abstract(abstract)
        if abstract_str in self._instances:
            del self._instances[abstract_str]

    def forget_instances(self) -> None:
        """Clear all of the instances from the container."""
        self._instances = {}

    def forget_scoped_instances(self) -> None:
        """Clear all of the scoped instances from the container."""
        self._scoped_instances = {}

    def resolve_environment_using(self, callback: Callable) -> None:
        """
        Set the callback which determines the current container environment.

        Args:
            callback: The callback to resolve the environment.
        """
        self.environment_resolver = callback

    def current_environment_is(self, environments: Union[str, list[str]]) -> bool:
        """
        Determine the environment for the container.

        Args:
            environments: The environment(s) to check against.

        Returns:
            True if the current environment matches, False otherwise.
        """
        if self.environment_resolver is None:
            return False

        return self.environment_resolver(environments)

    def __getitem__(self, key: str) -> Any:
        """Resolve an item from the container by key."""
        return self.make(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Register a binding or instance with the container."""
        # If the value is a closure, we'll bind it as a factory.
        # Otherwise, we'll register it as a concrete instance.
        if callable(value) and not inspect.isclass(value):
            self.bind(key, value)
        else:
            self.instance(key, value)

    def __delitem__(self, key: str) -> None:
        """Remove a binding from the container."""
        key_str = self._normalize_abstract(key)
        if key_str in self._bindings:
            del self._bindings[key_str]
        if key_str in self._instances:
            del self._instances[key_str]
        if key_str in self._resolved:
            del self._resolved[key_str]

    def __contains__(self, key: str) -> bool:
        """Determine if a given type is bound in the container."""
        return self.bound(key)
