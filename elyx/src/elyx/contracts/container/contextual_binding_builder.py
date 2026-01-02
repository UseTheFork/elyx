from abc import ABC, abstractmethod
from typing import Any, Callable


class ContextualBindingBuilder(ABC):
    """Contract for contextual binding builder."""

    @abstractmethod
    def needs(self, abstract: str | type) -> ContextualBindingBuilder:
        """
        Define the abstract target that depends on the context.

        Args:
            abstract: The abstract type that is needed.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def give(self, implementation: Callable | str | list[str]) -> ContextualBindingBuilder:
        """
        Define the implementation for the contextual binding.

        Args:
            implementation: The implementation to use.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def give_tagged(self, tag: str) -> ContextualBindingBuilder:
        """
        Define tagged services to be used as the implementation for the contextual binding.

        Args:
            tag: The tag name.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def give_config(self, key: str, default: Any = None) -> ContextualBindingBuilder:
        """
        Specify the configuration item to bind as a primitive.

        Args:
            key: The configuration key.
            default: The default value if key not found.

        Returns:
            Self for method chaining.
        """
        pass
