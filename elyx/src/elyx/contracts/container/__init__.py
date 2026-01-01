"""Container contracts for dependency injection and service resolution."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.contracts.container.container import Container
    from elyx.contracts.container.container_interface import ContainerInterface

__all__ = (
    "Container",
    "ContainerInterface",
)

_dynamic_imports = {
    # keep-sorted start
    "Container": "container",
    "ContainerInterface": "container_interface",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
