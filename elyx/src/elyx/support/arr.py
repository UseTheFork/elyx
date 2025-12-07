from typing import Any


class Arr:
    """Array helper utilities."""

    @staticmethod
    def accessible(value: Any) -> bool:
        """
        Determine whether the given value is array accessible.

        Args:
            value: Value to check.

        Returns:
            True if accessible as array/dict, False otherwise.
        """
        return isinstance(value, (dict, list))

    @staticmethod
    def exists(array: dict | list, key: str | int) -> bool:
        """
        Determine if the given key exists in the provided array.

        Args:
            array: Array/dict to check.
            key: Key to look for.

        Returns:
            True if key exists, False otherwise.
        """
        if isinstance(array, dict):
            return key in array
        elif isinstance(array, list):
            return isinstance(key, int) and 0 <= key < len(array)
        return False

    @staticmethod
    def get(array: dict | list | Any, key: str | int | None = None, default: Any = None) -> Any:
        """
        Get an item from an array using "dot" notation.

        Args:
            array: Array/dict to retrieve from.
            key: Key in dot notation (e.g., 'app.name').
            default: Default value if key not found.

        Returns:
            Retrieved value or default.
        """

        # Handle callable defaults
        def value(val):
            return val() if callable(val) else val

        if not Arr.accessible(array):
            return value(default)

        if key is None:
            return array

        if Arr.exists(array, key):
            if isinstance(array, dict):
                return array[key]
            elif isinstance(array, list) and isinstance(key, int):
                return array[key]

        if not isinstance(key, str) or "." not in key:
            return value(default)

        for segment in key.split("."):
            if Arr.accessible(array) and Arr.exists(array, segment):
                if isinstance(array, dict):
                    array = array[segment]
                elif isinstance(array, list) and isinstance(segment, int):
                    array = array[segment]
            else:
                return value(default)

        return array
