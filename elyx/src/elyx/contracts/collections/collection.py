from abc import ABC, abstractmethod
from typing import Any, Callable, Iterator


class Collection(ABC):
    """Contract for collection classes with array access and enumerable capabilities."""

    @abstractmethod
    def __getitem__(self, key: Any) -> Any:
        """
        Get an item at a given offset.

        Args:
            key: The offset to retrieve.

        Returns:
            The item at the given offset.
        """
        pass

    @abstractmethod
    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set an item at a given offset.

        Args:
            key: The offset to set.
            value: The value to set.
        """
        pass

    @abstractmethod
    def __delitem__(self, key: Any) -> None:
        """
        Unset an item at a given offset.

        Args:
            key: The offset to unset.
        """
        pass

    @abstractmethod
    def __contains__(self, key: Any) -> bool:
        """
        Determine if an item exists at an offset.

        Args:
            key: The offset to check.

        Returns:
            True if the offset exists, False otherwise.
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterator:
        """
        Get an iterator for the items.

        Returns:
            Iterator for the collection items.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        Count the number of items in the collection.

        Returns:
            The number of items.
        """
        pass

    @abstractmethod
    def all(self) -> list[Any]:
        """
        Get all of the items in the collection.

        Returns:
            List of all items.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Count the number of items in the collection.

        Returns:
            The number of items.
        """
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Determine if the collection is empty.

        Returns:
            True if empty, False otherwise.
        """
        pass

    @abstractmethod
    def is_not_empty(self) -> bool:
        """
        Determine if the collection is not empty.

        Returns:
            True if not empty, False otherwise.
        """
        pass

    @abstractmethod
    def first(self, callback: Callable[[Any], bool] | None = None, default: Any = None) -> Any:
        """
        Get the first item in the collection.

        Args:
            callback: Optional callback to filter items.
            default: Default value if no item found.

        Returns:
            The first item or default.
        """
        pass

    @abstractmethod
    def last(self, callback: Callable[[Any], bool] | None = None, default: Any = None) -> Any:
        """
        Get the last item in the collection.

        Args:
            callback: Optional callback to filter items.
            default: Default value if no item found.

        Returns:
            The last item or default.
        """
        pass

    @abstractmethod
    def each(self, callback: Callable[[Any, Any], bool | None]) -> "Collection":
        """
        Execute a callback over each item.

        Args:
            callback: Callback to execute for each item.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def map(self, callback: Callable[[Any, Any], Any]) -> "Collection":
        """
        Run a map over each of the items.

        Args:
            callback: Callback to transform each item.

        Returns:
            New collection with transformed items.
        """
        pass

    @abstractmethod
    def filter(self, callback: Callable[[Any, Any], bool] | None = None) -> "Collection":
        """
        Run a filter over each of the items.

        Args:
            callback: Optional callback to filter items.

        Returns:
            New collection with filtered items.
        """
        pass

    @abstractmethod
    def to_array(self) -> list[Any]:
        """
        Get the collection as a plain list.

        Returns:
            List representation of the collection.
        """
        pass
