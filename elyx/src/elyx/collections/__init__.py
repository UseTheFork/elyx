"""Collection utilities for array manipulation and enumerable types."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.collections.arr import Arr
    from elyx.collections.collection import Collection

__all__ = ("Arr", "Collection")

_dynamic_imports = {
    # keep-sorted start
    "Arr": "arr",
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
