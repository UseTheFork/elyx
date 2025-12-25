from typing import Any, Callable


class Macroable:
    """Mixin for adding macro functionality to classes."""

    _macros: dict[str, Callable] = {}

    @classmethod
    def __class_getitem__(cls, name: str) -> Any:
        """
        Dynamically handle static calls to the class.

        Args:
            name: The method name.

        Returns:
            The macro result.

        Raises:
            AttributeError: If the macro doesn't exist.
        """
        if not cls.has_macro(name):
            raise AttributeError(f"Method {cls.__name__}.{name} does not exist.")

        macro = cls._macros[name]

        if callable(macro):
            return lambda *args, **kwargs: macro(*args, **kwargs)

        return macro

    @classmethod
    def macro(cls, name: str, macro: Callable) -> None:
        """
        Register a custom macro.

        Args:
            name: The name of the macro.
            macro: The callable to register.
        """
        cls._macros[name] = macro

    @classmethod
    def mixin(cls, mixin: object, replace: bool = True) -> None:
        """
        Mix another object into the class.

        Args:
            mixin: The object to mix in.
            replace: Whether to replace existing macros.
        """
        for method_name in dir(mixin):
            if method_name.startswith("_"):
                continue

            method = getattr(mixin, method_name)
            if not callable(method):
                continue

            if replace or not cls.has_macro(method_name):
                cls.macro(method_name, method)

    @classmethod
    def has_macro(cls, name: str) -> bool:
        """
        Check if a macro is registered.

        Args:
            name: The name of the macro.

        Returns:
            True if the macro exists, False otherwise.
        """
        return name in cls._macros

    @classmethod
    def flush_macros(cls) -> None:
        """Flush the existing macros."""
        cls._macros = {}

    def __getattr__(self, name: str) -> Any:
        """
        Dynamically handle calls to the class.

        Args:
            name: The method name.

        Returns:
            The macro result.

        Raises:
            AttributeError: If the macro doesn't exist.
        """
        if not self.__class__.has_macro(name):
            raise AttributeError(f"Method {self.__class__.__name__}.{name} does not exist.")

        macro = self.__class__._macros[name]

        if callable(macro):
            return lambda *args, **kwargs: macro(self, *args, **kwargs)

        return macro
