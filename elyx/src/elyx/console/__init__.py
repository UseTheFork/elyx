"""Console application for command execution and argument parsing."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.console.application import Application
    from elyx.console.argument_parser import ArgumentParser
    from elyx.console.command import Command
    from elyx.console.console import Console
    from elyx.console.container_command_loader import ContainerCommandLoader

__all__ = (
    "Application",
    "ArgumentParser",
    "Command",
    "Console",
    "ContainerCommandLoader",
)

_dynamic_imports = {
    # keep-sorted start
    "Application": "application",
    "ArgumentParser": "argument_parser",
    "Command": "command",
    "Console": "console",
    "ContainerCommandLoader": "container_command_loader",
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
