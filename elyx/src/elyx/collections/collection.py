from typing import Any, Iterable

from elyx.contracts.collections.collection import Collection as CollectionContract


class Collection(CollectionContract):
    """Collection class for managing items."""

    def __init__(self, items: Iterable[Any] | None = None):
        """
        Create a new collection.

        Args:
            items: Initial items for the collection.
        """
        self._items: list[Any] = self._get_arrayable_items(items)

    def _get_arrayable_items(self, items: Iterable[Any] | None) -> list[Any]:
        """
        Convert items to a list.

        Args:
            items: Items to convert.

        Returns:
            List of items.
        """
        if items is None:
            return []
        if isinstance(items, list):
            return items
        if isinstance(items, (tuple, set)):
            return list(items)
        if hasattr(items, "__iter__"):
            return list(items)
        return [items]


    def __getitem__(self, key: Any) -> Any:
        """Get an item at a given offset."""
        return self._items[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set an item at a given offset."""
        self._items[key] = value

    def __delitem__(self, key: Any) -> None:
        """Unset an item at a given offset."""
        del self._items[key]

    def __contains__(self, key: Any) -> bool:
        """Determine if an item exists at an offset."""
        return key in self._items

    def __iter__(self) -> Any:
        """Get an iterator for the items."""
        return iter(self._items)

    def __len__(self) -> int:
        """Count the number of items in the collection."""
        return len(self._items)

    def all(self) -> list[Any]:
        """Get all of the items in the collection."""
        return self._items

    def count(self) -> int:
        """Count the number of items in the collection."""
        return len(self._items)

    def is_empty(self) -> bool:
        """Determine if the collection is empty."""
        return len(self._items) == 0

    def is_not_empty(self) -> bool:
        """Determine if the collection is not empty."""
        return len(self._items) > 0

    def first(self, callback: Any | None = None, default: Any = None) -> Any:
        """Get the first item in the collection."""
        if callback is None:
            return self._items[0] if self._items else default

        for item in self._items:
            if callback(item):
                return item
        return default

    def last(self, callback: Any | None = None, default: Any = None) -> Any:
        """Get the last item in the collection."""
        if callback is None:
            return self._items[-1] if self._items else default

        for item in reversed(self._items):
            if callback(item):
                return item
        return default

    def each(self, callback: Any) -> "Collection":
        """Execute a callback over each item."""
        for key, item in enumerate(self._items):
            if callback(item, key) is False:
                break
        return self

    def map(self, callback: Any) -> "Collection":
        """Run a map over each of the items."""
        return Collection([callback(item, key) for key, item in enumerate(self._items)])

    def filter(self, callback: Any | None = None) -> "Collection":
        """Run a filter over each of the items."""
        if callback is None:
            return Collection([item for item in self._items if item])

        return Collection([item for key, item in enumerate(self._items) if callback(item, key)])

    def to_array(self) -> list[Any]:
        """Get the collection as a plain list."""
        return self._items
