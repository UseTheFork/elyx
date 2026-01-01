"""Support contracts for service providers and array storage."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.contracts.support.array_store_contract import ArrayStoreContract
    from elyx.contracts.support.service_provider import ServiceProvider

__all__ = (
    "ArrayStoreContract",
    "ServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "ArrayStoreContract": "array_store_contract",
    "ServiceProvider": "service_provider",
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
