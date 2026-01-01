from typing import TYPE_CHECKING

from dotenv import load_dotenv
from elyx.contracts.foundation import Bootstrapper

if TYPE_CHECKING:
    from elyx.foundation import Application


class LoadEnvironmentVariables(Bootstrapper):
    """Bootstrap class for loading environment variables from .env file."""

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
