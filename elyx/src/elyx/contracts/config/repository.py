from abc import ABC, abstractmethod
from typing import Any


class Repository(ABC):
    """Contract for"""

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
