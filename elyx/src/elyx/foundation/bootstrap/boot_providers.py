from __future__ import annotations

from typing import TYPE_CHECKING

from elyx.foundation.bootstrap.base import Bootstrapper

if TYPE_CHECKING:
    from elyx.foundation.application import Application


class BootProviders(Bootstrapper):
    async def bootstrap(self, app: Application) -> None:
        await app.boot()
