"""Support utilities including helpers, facades, and service providers."""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.support.concerns.array_store import ArrayStore
    from elyx.support.concerns.macroable import Macroable
    from elyx.support.concerns.reflects_closures import ReflectsClosures
    from elyx.support.service_provider import ServiceProvider
    from elyx.support.str import Str

__all__ = (
    "ArrayStore",
    "Macroable",
    "ReflectsClosures",
    "ServiceProvider",
    "Str",
)

_dynamic_imports = {
    # keep-sorted start
    "ArrayStore": "concerns.array_store",
    "Macroable": "concerns.macroable",
    "ReflectsClosures": "concerns.reflects_closures",
    "ServiceProvider": "service_provider",
    "Str": "str",
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
