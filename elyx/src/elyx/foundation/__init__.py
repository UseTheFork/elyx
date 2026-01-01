""""""

from typing import TYPE_CHECKING

from elyx._import_utils import import_attr

if TYPE_CHECKING:
    from elyx.foundation.application import Application
    from elyx.foundation.bootstrap.boot_providers import BootProviders
    from elyx.foundation.bootstrap.handle_exceptions import HandleExceptions
    from elyx.foundation.bootstrap.load_configuration import LoadConfiguration
    from elyx.foundation.bootstrap.load_environment_variables import LoadEnvironmentVariables
    from elyx.foundation.bootstrap.register_facades import RegisterFacades
    from elyx.foundation.bootstrap.register_providers import RegisterProviders
    from elyx.foundation.console.about_command import AboutCommand
    from elyx.foundation.console.kernel import ConsoleKernel
    from elyx.foundation.providers.console_command_service_provider import ConsoleCommandServiceProvider

__all__ = (
    "AboutCommand",
    "Application",
    "BootProviders",
    "ConsoleCommandServiceProvider",
    "ConsoleKernel",
    "HandleExceptions",
    "LoadConfiguration",
    "LoadEnvironmentVariables",
    "RegisterFacades",
    "RegisterProviders",
)

_dynamic_imports = {
    # keep-sorted start
    "AboutCommand": "console.about_command",
    "Application": "application",
    "BootProviders": "bootstrap.boot_providers",
    "ConsoleCommandServiceProvider": "providers.console_command_service_provider",
    "ConsoleKernel": "console.kernel",
    "HandleExceptions": "bootstrap.handle_exceptions",
    "LoadConfiguration": "bootstrap.load_configuration",
    "LoadEnvironmentVariables": "bootstrap.load_environment_variables",
    "RegisterFacades": "bootstrap.register_facades",
    "RegisterProviders": "bootstrap.register_providers",
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
