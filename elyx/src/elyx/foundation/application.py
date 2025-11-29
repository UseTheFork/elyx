from collections.abc import Callable
from pathlib import Path
from typing import Optional, TypeVar

from elyx.container import Container

T = TypeVar("T")


class Application(Container):
    @staticmethod
    def configure(base_path: Optional[Path] = None):
        """
        Create and configure a new Application instance.

        Args:
            base_path: Optional base path for the application.

        Returns:
            Application instance.
        """
        from elyx.foundation.configuration.application_builder import ApplicationBuilder

        return ApplicationBuilder(Application(base_path=base_path)).with_kernels()

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the container with empty registries."""
        super().__init__()
        self.base_path = base_path

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
        # If abstract is a callable and no concrete provided, use abstract as concrete
        if callable(abstract) and concrete is None:
            concrete = abstract
            abstract = abstract.__name__

        # If concrete is None, use abstract as concrete
        if concrete is None:
            concrete = abstract

        abstract_str = self._normalize_abstract(abstract)

        # Remove any existing instance if rebinding
        self._instances.pop(abstract_str, None)

        # Store the binding
        self._bindings[abstract_str] = {
            "concrete": concrete,
            "shared": shared,
        }

    def alias(self, abstract: str | type[T], alias: str) -> None:
        """
        Alias a type to a different name.

        Args:
            abstract: Abstract type identifier.
            alias: Alias name.

        Raises:
            LogicError: If aliasing fails.
        """
        if alias == abstract:
            raise ValueError(f"[{abstract}] is aliased to itself.")

        self._aliases[alias] = self._normalize_abstract(abstract)

    def _is_alias(self, name: str) -> bool:
        """
        Check if a name is an alias.

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
            The aliased abstract type.
        """
        return self._aliases.get(abstract, abstract)

    def flush(self) -> None:
        """
        Flush the container of all bindings and resolved instances.
        """

        self._resolved.clear()
        self._bindings.clear()
        self._method_bindings.clear()
        self._instances.clear()
        self._aliases.clear()
        self._before_resolving_callbacks.clear()
        self._resolving_callbacks.clear()
        self._after_resolving_callbacks.clear()
        self._global_before_resolving_callbacks.clear()
        self._global_resolving_callbacks.clear()
        self._global_after_resolving_callbacks.clear()
