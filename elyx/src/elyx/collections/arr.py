from typing import Any

from elyx.contracts.collections import ArrayAccess
from elyx.support import Macroable


class Arr(Macroable):
    """Array helper utilities."""

    @staticmethod
    def _normalize_to_dict(value: Any) -> dict | Any:
        """
        Convert lists to dicts with integer keys to make them array-like.

        Args:
            value: Value to normalize.

        Returns:
            Dict if value is a list, otherwise returns value unchanged.
        """
        if isinstance(value, list):
            return {i: item for i, item in enumerate(value)}
        return value

    @staticmethod
    def accessible(value: Any) -> bool:
        """
        Determine whether the given value is array accessible.

        Args:
            value: Value to check.

        Returns:
            True if accessible as array/dict, False otherwise.
        """
        return isinstance(value, (dict, list, ArrayAccess))

    @staticmethod
    def exists(array, key) -> bool:
        """
        Determine if the given key exists in the provided array.

        Args:
            array: Array/dict to check.
            key: Key to look for.

        Returns:
            True if key exists, False otherwise.
        """
        array = Arr._normalize_to_dict(array)

        if isinstance(array, (dict, ArrayAccess)):
            return key in array
        return False

    @staticmethod
    def has(array, key) -> bool:
        """
        Determine if the given key exists in the provided array using "dot" notation.

        Args:
            array: Array/dict to check.
            key: Key in dot notation (e.g., 'app.name') or list of keys.

        Returns:
            True if key exists, False otherwise.
        """
        array = Arr._normalize_to_dict(array)

        if isinstance(key, list):
            if not array or not key:
                return False
            for k in key:
                if not Arr.has(array, k):
                    return False
            return True

        if not Arr.accessible(array):
            return False

        if key is None:
            return False

        if Arr.exists(array, key):
            return True

        if not isinstance(key, str) or "." not in key:
            return False

        for segment in key.split("."):
            if segment.isdigit():
                segment = int(segment)

            if Arr.accessible(array) and Arr.exists(array, segment):
                array = Arr._normalize_to_dict(array[segment])
            else:
                return False

        return True

    @staticmethod
    def get(array, key, default: Any = None) -> Any:
        """
        Get an item from an array using "dot" notation.

        Args:
            array: Array/dict to retrieve from.
            key: Key in dot notation (e.g., 'app.name').
            default: Default value if key not found.

        Returns:
            Retrieved value or default.
        """
        array = Arr._normalize_to_dict(array)

        # Handle callable defaults
        def value(val):
            return val() if callable(val) else val

        if not Arr.accessible(array):
            return value(default)

        if key is None:
            return array

        if Arr.exists(array, key):
            return array[key]

        if not isinstance(key, str) or "." not in key:
            return value(default)

        for segment in key.split("."):
            if segment.isdigit():
                segment = int(segment)

            if Arr.accessible(array) and Arr.exists(array, segment):
                array = Arr._normalize_to_dict(array[segment])
            else:
                return value(default)

        return array

    @staticmethod
    def set(array: dict | list, key, value: Any) -> dict | list:
        """
        Set an array item to a given value using "dot" notation.

        Args:
            array: Array/dict to modify.
            key: Key in dot notation (e.g., 'products.desk.price') or None to replace entire array.
            value: Value to set.

        Returns:
            Modified array.
        """
        array = Arr._normalize_to_dict(array)

        if key is None:
            return value

        if not isinstance(key, str):
            array[key] = value
            return array

        keys = key.split(".")
        current = array

        while len(keys) > 1:
            segment = keys.pop(0)

            # If the key doesn't exist at this depth, create an empty dict
            if not isinstance(current, dict) or not Arr.exists(current, segment):
                current[segment] = {}

            if segment not in current or not Arr.accessible(current[segment]):
                current[segment] = {}
            current = current[segment]

        segment = keys[0]

        current[segment] = value

        return array

    @staticmethod
    def wrap(value: Any) -> list:
        """
        Wrap the given value in a list if it is not already a list.

        Args:
            value: Value to wrap.

        Returns:
            List containing the value, or the value itself if already a list.
        """
        if value is None:
            return []
        return value if isinstance(value, list) else [value]
