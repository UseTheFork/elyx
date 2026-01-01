"""Collection contracts for array-accessible and enumerable types."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.contracts.collections.array_access import ArrayAccess
    from elyx.contracts.collections.collection import Collection

__all__ = (
    "ArrayAccess",
    "Collection",
)

_dynamic_imports = {
    # keep-sorted start
    "ArrayAccess": "array_access",
    "Collection": "collection",
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
