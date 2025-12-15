class ContainerException(Exception):
    """Base exception for container errors."""

    pass


class EntryNotFoundException(ContainerException):
    """Exception thrown when an entry is not found in the container."""

    def __init__(self, id: str, code: int = 0, previous: Exception | None = None):
        self.id = id
        message = f"Entry not found for identifier: {id}"
        super().__init__(message)
        self.__cause__ = previous


class CircularDependencyException(ContainerException):
    """Exception thrown when a circular dependency is detected."""

    pass


class BindingResolutionException(ContainerException):
    """Exception thrown when a binding cannot be resolved."""

    pass
