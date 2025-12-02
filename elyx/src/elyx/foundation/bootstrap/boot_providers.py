from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from elyx.foundation.application import Application


class BootProviders:
    def __init__(self, **kwargs):
        pass

    async def bootstrap(self, app: Application) -> None:
        await app.boot()
