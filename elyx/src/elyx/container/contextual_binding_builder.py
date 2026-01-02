from typing import Any, Callable

from elyx.collections import Arr
from elyx.contracts.container import Container as ContainerContract


class ContextualBindingBuilder:
    """Builder for contextual bindings in the container."""

    def __init__(self, container: ContainerContract, concrete: str | list[str]):
        """
        Create a new contextual binding builder.

        Args:
            container: The container instance.
            concrete: The concrete class(es) that need the binding.
        """
        self._container = container
        self._concrete = concrete
        self._needs = None

    def needs(self, abstract: str | type) -> ContextualBindingBuilder:
        """
        Define the abstract target that depends on the context.

        Args:
            abstract: The abstract type that is needed.

        Returns:
            Self for method chaining.
        """
        self._needs = abstract
        return self

    def give(self, implementation: Callable | str | list[str]) -> ContextualBindingBuilder:
        """
        Define the implementation for the contextual binding.

        Args:
            implementation: The implementation to use.

        Returns:
            Self for method chaining.
        """
        for concrete in Arr.wrap(self._concrete):
            self._container.add_contextual_binding(concrete, self._needs, implementation)
        return self

    def give_tagged(self, tag: str) -> ContextualBindingBuilder:
        """
        Define tagged services to be used as the implementation for the contextual binding.

        Args:
            tag: The tag name.

        Returns:
            Self for method chaining.
        """
        return self.give(lambda container: list(container.tagged(tag)))

    def give_config(self, key: str, default: Any = None) -> ContextualBindingBuilder:
        """
        Specify the configuration item to bind as a primitive.

        Args:
            key: The configuration key.
            default: The default value if key not found.

        Returns:
            Self for method chaining.
        """
        return self.give(lambda container: container.get("config").get(key, default))
