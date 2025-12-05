from abc import ABC, abstractmethod
from typing import Any


class ArrayStoreContract(ABC):
    """Contract for array-based data storage."""

    @abstractmethod
    def all(self) -> dict[str, Any]:
        """
        Retrieve all the items.

        Returns:
            Dictionary of all items.
        """
        pass

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a single item.

        Args:
            key: The key to retrieve.
            default: Default value if key not found.

        Returns:
            The value or default.
        """
        pass

    @abstractmethod
    def set(self, data: dict[str, Any]) -> "ArrayStoreContract":
        """
        Overwrite the entire repository's contents.

        Args:
            data: Dictionary of data to set.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def merge(self, *arrays: dict[str, Any]) -> "ArrayStoreContract":
        """
        Merge in other arrays.

        Args:
            *arrays: Variable number of dictionaries to merge.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def add(self, key: str, value: Any) -> "ArrayStoreContract":
        """
        Add an item to the repository.

        Args:
            key: The key to add.
            value: The value to add.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def remove(self, key: str) -> "ArrayStoreContract":
        """
        Remove an item from the store.

        Args:
            key: The key to remove.

        Returns:
            Self for method chaining.
        """
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Determine if the store is empty.

        Returns:
            True if empty, False otherwise.
        """
        pass

    @abstractmethod
    def is_not_empty(self) -> bool:
        """
        Determine if the store is not empty.

        Returns:
            True if not empty, False otherwise.
        """
        pass
