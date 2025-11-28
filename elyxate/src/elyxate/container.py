from collections.abc import Callable
from typing import Any, TypeVar

from elyxate.contracts.container_contract import ContainerContract

T = TypeVar("T")


class Container(ContainerContract):
    """
    Laravel-like dependency injection container.
    """

    def __init__(self):
        """Initialize the container with empty registries."""
        # An array of the types that have been resolved.
        self._resolved: dict[str, bool] = {}

        # The container's bindings.
        self._bindings: dict[str, dict[str, Any]] = {}

        # The container's method bindings.
        self._method_bindings: dict[str, Callable] = {}

        # The container's shared instances.
        self._instances: dict[str, Any] = {}

        # The registered type aliases.
        self._aliases: dict[str, str] = {}

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

    def _is_alias(self, name: str) -> bool:
        """
        Check if a name is registered as an alias.

        Args:
            name: Name to check.

        Returns:
            bool
        """
        return name in self._aliases

    def _get_alias(self, abstract: str) -> str:
        """
        Get the alias for an abstract type.

        Args:
            abstract: Abstract type identifier.

        Returns:
            The actual abstract type the alias points to.
        """
        return self._aliases.get(abstract, abstract)
