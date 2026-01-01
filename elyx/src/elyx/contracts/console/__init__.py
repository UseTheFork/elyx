"""Console contracts for command execution and kernel management."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.contracts.console.application import Application
    from elyx.contracts.console.command import Command
    from elyx.contracts.console.kernel import Kernel

__all__ = (
    "Application",
    "Command",
    "Kernel",
)

_dynamic_imports = {
    # keep-sorted start
    "Application": "application",
    "Command": "command",
    "Kernel": "kernel",
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
