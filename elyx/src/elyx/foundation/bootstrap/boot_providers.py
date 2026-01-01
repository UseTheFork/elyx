from typing import TYPE_CHECKING

from elyx.contracts.foundation import Bootstrapper

if TYPE_CHECKING:
    from elyx.foundation import Application


class BootProviders(Bootstrapper):
    def bootstrap(self, app: Application) -> None:
        app.boot()
