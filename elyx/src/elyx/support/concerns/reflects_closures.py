import inspect
import types
from typing import Callable, get_args, get_origin


class ReflectsClosures:
    """Provides reflection utilities for closures."""

    def _closure_parameter_types(self, closure: Callable) -> dict[str, str | None]:
        """
        Get the class names / types of the parameters of the given Closure.

        Args:
            closure: The closure to inspect.

        Returns:
            Dictionary mapping parameter names to their class names/types.
        """
        signature = inspect.signature(closure)
        result = {}

        for param_name, param in signature.parameters.items():
            # Skip 'self' and 'cls' parameters
            if param_name in ("self", "cls"):
                continue

            # Check if parameter is variadic (*args or **kwargs)
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                result[param_name] = None
                continue

            # Get the parameter's type annotation
            if param.annotation is not inspect.Parameter.empty:
                annotation = param.annotation
                # If it's a class, get its fully qualified name
                if inspect.isclass(annotation):
                    result[param_name] = f"{annotation.__module__}.{annotation.__qualname__}"
                else:
                    # For other types (like Union, Optional, etc.), convert to string
                    result[param_name] = str(annotation)
            else:
                result[param_name] = None

        return result

    def _first_closure_parameter_type(self, closure: Callable) -> str:
        """
        Get the class name of the first parameter of the given Closure.

        Args:
            closure: The closure to inspect.

        Returns:
            Class name of the first parameter.

        Raises:
            RuntimeError: If the closure has no parameters or the first parameter is missing a type hint.
        """
        types = list(self._closure_parameter_types(closure).values())

        if not types:
            raise RuntimeError("The given Closure has no parameters.")

        if types[0] is None:
            raise RuntimeError("The first parameter of the given Closure is missing a type hint.")

        return types[0]

    def _first_closure_parameter_types(self, closure: Callable) -> list[str]:
        """
        Get the class names of the first parameter of the given Closure, including union types.

        Args:
            closure: The closure to inspect.

        Returns:
            List of class names from the first parameter's type annotation.

        Raises:
            RuntimeError: If the closure has no parameters or the first parameter is missing a type hint.
        """
        signature = inspect.signature(closure)
        parameters = list(signature.parameters.values())

        # Filter out 'self' and 'cls' parameters
        parameters = [p for p in parameters if p.name not in ("self", "cls")]

        if not parameters:
            raise RuntimeError("The given Closure has no parameters.")

        first_param = parameters[0]

        # Check if parameter is variadic
        if first_param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            return []

        # Check if parameter has type annotation
        if first_param.annotation is inspect.Parameter.empty:
            raise RuntimeError("The first parameter of the given Closure is missing a type hint.")

        annotation = first_param.annotation

        # Handle Union types (e.g., Union[MyClass, OtherClass] or MyClass | OtherClass)
        origin = get_origin(annotation)
        if origin is types.UnionType or (hasattr(types, "Union") and origin is getattr(types, "Union", None)):
            type_args = get_args(annotation)
        else:
            type_args = [annotation]

        result = []
        for type_arg in type_args:
            # Skip built-in types and None
            if not inspect.isclass(type_arg):
                continue
            if type_arg.__module__ == "builtins":
                continue
            if type_arg is type(None):
                continue

            result.append(f"{type_arg.__module__}.{type_arg.__qualname__}")

        if not result:
            raise RuntimeError("The first parameter of the given Closure is missing a type hint.")

        return result

    def _closure_return_types(self, closure: Callable) -> list[str]:
        """
        Get the class names / types of the return type of the given Closure.

        Args:
            closure: The closure to inspect.

        Returns:
            List of class names from the return type annotation.
        """
        try:
            signature = inspect.signature(closure)
            return_annotation = signature.return_annotation
        except (ValueError, TypeError):
            return []

        if return_annotation is inspect.Signature.empty:
            return []

        # Handle Union types (e.g., Union[MyClass, None] or MyClass | None)
        origin = get_origin(return_annotation)
        if origin is types.UnionType or (hasattr(types, "Union") and origin is getattr(types, "Union", None)):
            type_args = get_args(return_annotation)
        else:
            type_args = [return_annotation]

        result = []
        for type_arg in type_args:
            # Skip built-in types
            if not inspect.isclass(type_arg):
                continue
            if type_arg.__module__ == "builtins":
                continue
            # Skip 'self' and 'static' references (though rare in return types)
            if type_arg.__name__ in ("self", "static"):
                continue

            result.append(f"{type_arg.__module__}.{type_arg.__qualname__}")

        return result
