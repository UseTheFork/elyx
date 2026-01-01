"""Contracts defining interfaces for core framework components."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.contracts.collections.array_access import ArrayAccess
    from elyx.contracts.collections.collection import Collection
    from elyx.contracts.console.application import Application as ConsoleApplication
    from elyx.contracts.console.command import Command
    from elyx.contracts.console.kernel import Kernel
    from elyx.contracts.container.container import Container
    from elyx.contracts.container.container_interface import ContainerInterface
    from elyx.contracts.events.dispatcher import Dispatcher
    from elyx.contracts.foundation.application import Application
    from elyx.contracts.foundation.bootstrapper import Bootstrapper
    from elyx.contracts.logging.logger import Logger
    from elyx.contracts.support.array_store_contract import ArrayStoreContract
    from elyx.contracts.support.service_provider import ServiceProvider

__all__ = (
    "Application",
    "ArrayAccess",
    "ArrayStoreContract",
    "Bootstrapper",
    "Collection",
    "Command",
    "ConsoleApplication",
    "Container",
    "ContainerInterface",
    "Dispatcher",
    "Kernel",
    "Logger",
    "ServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "Application": "foundation.application",
    "ArrayAccess": "collections.array_access",
    "ArrayStoreContract": "support.array_store_contract",
    "Bootstrapper": "foundation.bootstrapper",
    "Collection": "collections.collection",
    "Command": "console.command",
    "ConsoleApplication": "console.application",
    "Container": "container.container",
    "ContainerInterface": "container.container_interface",
    "Dispatcher": "events.dispatcher",
    "Kernel": "console.kernel",
    "Logger": "logging.logger",
    "ServiceProvider": "support.service_provider",
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
