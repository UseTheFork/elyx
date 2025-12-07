from typing import Callable

from elyx.support.concerns.array_store import ArrayStore


class Repository(ArrayStore):
    """Configuration repository with type-safe getters."""

    def string(self, key: str, default: Callable[[], str | None] | str | None = None) -> str:
        """
        Get the specified string configuration value.

        Args:
            key: Configuration key.
            default: Default value or callable returning default.

        Returns:
            String configuration value.

        Raises:
            ValueError: If the value is not a string.
        """
        value = self.get(key, default)
        if not isinstance(value, str):
            raise ValueError(f"Configuration value for key [{key}] must be a string, {type(value).__name__} given.")
        return value

    def integer(self, key: str, default: Callable[[], int | None] | int | None = None) -> int:
        """
        Get the specified integer configuration value.

        Args:
            key: Configuration key.
            default: Default value or callable returning default.

        Returns:
            Integer configuration value.

        Raises:
            ValueError: If the value is not an integer.
        """
        value = self.get(key, default)
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"Configuration value for key [{key}] must be an integer, {type(value).__name__} given.")
        return value

    def float(self, key: str, default: Callable[[], float | None] | float | None = None) -> float:
        """
        Get the specified float configuration value.

        Args:
            key: Configuration key.
            default: Default value or callable returning default.

        Returns:
            Float configuration value.

        Raises:
            ValueError: If the value is not a float.
        """
        value = self.get(key, default)
        if not isinstance(value, float):
            raise ValueError(f"Configuration value for key [{key}] must be a float, {type(value).__name__} given.")
        return value

    def boolean(self, key: str, default: Callable[[], bool | None] | bool | None = None) -> bool:
        """
        Get the specified boolean configuration value.

        Args:
            key: Configuration key.
            default: Default value or callable returning default.

        Returns:
            Boolean configuration value.

        Raises:
            ValueError: If the value is not a boolean.
        """
        value = self.get(key, default)
        if not isinstance(value, bool):
            raise ValueError(f"Configuration value for key [{key}] must be a boolean, {type(value).__name__} given.")
        return value
