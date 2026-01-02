from typing import TYPE_CHECKING

from elyx.contracts.foundation.application import Application
from elyx.contracts.foundation.bootstrapper import Bootstrapper
from elyx.support.facades import Facade

if TYPE_CHECKING:
    from elyx.foundation import Application


class RegisterFacades(Bootstrapper):
    """Bootstrap class for registering the facade application instance."""

    def bootstrap(self, app: Application) -> None:
        """
        Set the application instance for all facades.

        Args:
            app: The application instance.
        """
        Facade.clear_resolved_instances()
        Facade.set_facade_application(app)
