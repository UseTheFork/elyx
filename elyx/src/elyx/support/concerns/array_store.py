from typing import Any

from elyx.contracts.support.array_store_contract import ArrayStoreContract
from elyx.support import Arr


class ArrayStore(ArrayStoreContract):
    """Mixin for array-based data storage."""

    def __init__(self, data: dict[str, Any] | None = None):
        """
        Initialize the array store.

        Args:
            data: Initial data dictionary.
        """
        self._data: dict[str, Any] = data if data is not None else {}

    def all(self) -> dict[str, Any]:
        """Retrieve all the items."""
        return self._data

    def has(self, key: str) -> bool:
        """Determine if an item exists in the store."""
        return Arr.has(self._data, key)

    def get(self, key: str | list | dict, default: Any = None) -> Any:
        """
        Retrieve a single item or multiple items, supporting dot notation for nested access.

        Args:
            key: Key string, list of keys, or dict of keys with defaults.
            default: Default value if key not found (only used for string keys).

        Returns:
            Single value, or dict of key-value pairs if key is list/dict.
        """
        if isinstance(key, list):
            return {k: Arr.get(self._data, k) for k in key}
        elif isinstance(key, dict):
            return {k: Arr.get(self._data, k, v) for k, v in key.items()}
        return Arr.get(self._data, key, default)

    def set(self, data: dict[str, Any]) -> "ArrayStore":
        """Overwrite the entire repository."""
        self._data = data
        return self

    def merge(self, *arrays: dict[str, Any]) -> "ArrayStore":
        """Merge in other arrays."""
        for array in arrays:
            self._data.update(array)
        return self

    def add(self, key: str, value: Any) -> "ArrayStore":
        """Add an item to the repository."""
        # Handle callable values (similar to Helpers::value in PHP)
        if callable(value):
            value = value()
        self._data[key] = value
        return self

    def remove(self, key: str) -> "ArrayStore":
        """Remove an item from the store."""
        self._data.pop(key, None)
        return self

    def is_empty(self) -> bool:
        """Determine if the store is empty."""
        return len(self._data) == 0

    def is_not_empty(self) -> bool:
        """Determine if the store is not empty."""
        return not self.is_empty()

    def __getitem__(self, key: str) -> Any:
        """Get an item using dictionary syntax."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an item using dictionary syntax."""
        self.add(key, value)

    def __delitem__(self, key: str) -> None:
        """Delete an item using dictionary syntax."""
        self.remove(key)

    def __iter__(self):
        """Iterate over the keys in the store."""
        return iter(self._data)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists using 'in' operator."""
        return key in self._data

    def __len__(self) -> int:
        """Get the number of items in the store."""
        return len(self._data)
