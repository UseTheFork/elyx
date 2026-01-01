"""Logging system for structured application logging."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.logging.console_logger import ConsoleLogger
    from elyx.logging.log_manager import LogManager
    from elyx.logging.log_service_provider import LogServiceProvider

__all__ = (
    "ConsoleLogger",
    "LogManager",
    "LogServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "ConsoleLogger": "console_logger",
    "LogManager": "log_manager",
    "LogServiceProvider": "log_service_provider",
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
