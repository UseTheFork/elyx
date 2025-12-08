from __future__ import annotations

from elyx.contracts.foundation.application import Application
from elyx.contracts.foundation.bootstrapper import Bootstrapper


class BootProviders(Bootstrapper):
    def bootstrap(self, app: Application) -> None:
        app.boot()
