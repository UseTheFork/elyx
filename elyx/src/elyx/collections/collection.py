from typing import Any, Iterable

from elyx.contracts.collections.collection import Collection as CollectionContract


class Collection(CollectionContract):
    """Collection class for managing items."""

    def _get_arrayable_items(self, items: Iterable[Any] | None) -> dict[Any, Any]:
        """
        Convert items to a dict.

        Args:
            items: Items to convert.

        Returns:
            Dict of items.
        """
        if items is None:
            return {}
        if isinstance(items, dict):
            return items
        if isinstance(items, list):
            return {i: item for i, item in enumerate(items)}
        if isinstance(items, (tuple, set)):
            return {i: item for i, item in enumerate(items)}
        if hasattr(items, "__iter__"):
            return {i: item for i, item in enumerate(items)}
        return {0: items}

    def __init__(self, items: Iterable[Any] | None = None):
        """
        Create a new collection.

        Args:
            items: Initial items for the collection.
        """
        self._items: dict[Any, Any] = self._get_arrayable_items(items)

    def all(self) -> dict[Any, Any]:
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
            return next(iter(self._items.values())) if self._items else default

        for item in self._items.values():
            if callback(item):
                return item
        return default

    def last(self, callback: Any | None = None, default: Any = None) -> Any:
        """Get the last item in the collection."""
        if callback is None:
            return list(self._items.values())[-1] if self._items else default

        for item in reversed(list(self._items.values())):
            if callback(item):
                return item
        return default

    def each(self, callback: Any) -> "Collection":
        """Execute a callback over each item."""
        for key, item in self._items.items():
            if callback(item, key) is False:
                break
        return self

    def map(self, callback: Any) -> "Collection":
        """Run a map over each of the items."""
        return Collection({key: callback(item, key) for key, item in self._items.items()})

    def filter(self, callback: Any | None = None) -> "Collection":
        """Run a filter over each of the items."""
        if callback is None:
            return Collection({key: item for key, item in self._items.items() if item})

        return Collection({key: item for key, item in self._items.items() if callback(item, key)})

    def to_array(self) -> dict[Any, Any]:
        """Get the collection as a plain dict."""
        return self._items

    def __getitem__(self, key: Any) -> Any:
        """Get an item at a given offset."""
        return self._items[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set an item at a given offset."""
        self._items[key] = value

    def __delitem__(self, key: Any) -> None:
        """Unset an item at a given offset."""
        del self._items[key]

    def __iter__(self) -> Any:
        """Get an iterator for the items."""
        return iter(self._items.values())

    def __contains__(self, key: Any) -> bool:
        """Determine if an item exists at an offset."""
        return key in self._items

    def __len__(self) -> int:
        """Count the number of items in the collection."""
        return len(self._items)
