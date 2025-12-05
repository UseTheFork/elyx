from __future__ import annotations

from dotenv import load_dotenv
from elyx.contracts.foundation.application import Application
from elyx.contracts.foundation.bootstrapper import Bootstrapper


class LoadConfiguration(Bootstrapper):
    """"""

    app: Application | None = None

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap environment variable loading.

        Args:
            app: The application instance.
        """
        env_file_path = app.environment_file_path()

        if env_file_path.exists():
            load_dotenv(dotenv_path=env_file_path)
