from typing import Any, ClassVar

from elyx.contracts.foundation.application import Application


class FacadeMeta(type):
    """Metaclass that intercepts attribute access on Facade classes."""

    def __getattr__(cls, name: str) -> Any:
        """
        Handle dynamic static method calls to the facade.

        Args:
            name: Method name to call.

        Returns:
            Callable that will invoke the method on the resolved instance.

        Raises:
            RuntimeError: If facade root has not been set.
        """
        instance = cls.get_facade_root()
        if not instance:
            raise RuntimeError("A facade root has not been set.")
        return getattr(instance, name)


class Facade(metaclass=FacadeMeta):
    """Base class for facades providing static-like access to container services."""

    _app: ClassVar[Application | None] = None
    _resolved_instance: ClassVar[dict[str, Any]] = {}
    _cached: ClassVar[bool] = True

    _accessor: ClassVar[str | None] = None

    @classmethod
    def get_facade_accessor(cls):
        """
        Get the registered name of the component.

        Returns:
            The container binding key.

        Raises:
            RuntimeError: If accessor is not defined.
        """
        raise RuntimeError(f"Facade {cls.__name__} does not implement get_facade_accessor")

    @classmethod
    def get_facade_root(cls) -> Any:
        """
        Resolve the facade root instance from the container.

        Returns:
            The resolved instance from the container.
        """
        app = cls.get_facade_application()
        if app is None:
            raise RuntimeError("Facade application has not been set.")
        return app.make(cls.get_facade_accessor())

    @classmethod
    def get_facade_application(cls) -> Application | None:
        """
        Get the application instance behind the facade.

        Returns:
            The application instance or None.
        """
        return cls._app

    @classmethod
    def set_facade_application(cls, app: Application | None) -> None:
        """
        Set the application instance.

        Args:
            app: The application instance to set.
        """
        cls._app = app

    @classmethod
    def clear_resolved_instances(cls) -> None:
        """Clear all of the resolved instances."""
        cls._resolved_instance = {}

    @classmethod
    def swap(cls, instance: Any) -> None:
        """
        Hotswap the underlying instance behind the facade.

        Args:
            instance: The instance to swap in.
        """
        accessor = cls.get_facade_accessor()
        cls._resolved_instance[accessor] = instance

        app = cls.get_facade_application()
        if app is not None:
            app.instance(accessor, instance)
