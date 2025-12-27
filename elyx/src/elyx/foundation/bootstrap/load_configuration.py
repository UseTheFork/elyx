from __future__ import annotations

from pathlib import Path

from elyx.config.repository import Repository
from elyx.contracts.foundation.application import Application
from elyx.contracts.foundation.bootstrapper import Bootstrapper


class LoadConfiguration(Bootstrapper):
    """Bootstrap class for loading configuration files from the config directory."""

    app: Application | None = None

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap environment variable loading.

        Args:
            app: The application instance.
        """

        config = app.instance("config", Repository())
        self.load_configuration_files(app, config)

        app.detect_environment(lambda: config.get("app.env", "production"))

        app.resolve_environment_using(lambda environments: app.environment(*environments))

    def load_configuration_files(self, app: Application, config: Repository):
        """
        Load the configuration items from all of the files.

        Args:
            app: The application instance.
            config: The configuration repository.
        """
        files = self.get_configuration_files(app)

        for name, path in files.items():
            self.load_configuration_file(config, name, path)

    def get_configuration_files(self, app: Application) -> dict[str, Path]:
        """
        Get all of the configuration files for the application.

        Args:
            app: The application instance.

        Returns:
            Dictionary mapping config keys to file paths.
        """

        files = {}
        config_path = app.config_path()

        if not config_path.exists() or not config_path.is_dir():
            return {}

        # Find all .py files in config directory (recursively)
        for file in sorted(config_path.rglob("*.py")):
            if file.name.startswith("_"):
                continue

            # Get relative path from config directory
            relative_path = file.relative_to(config_path)

            # Build config key (e.g., "database" or "services/cache")
            parts = list(relative_path.parts[:-1])  # Get directory parts
            filename = file.stem  # Get filename without extension

            if parts:
                config_key = "/".join(parts) + "/" + filename
            else:
                config_key = filename

            files[config_key] = file

        return files

    def load_configuration_file(self, repository: Repository, name: str, path: Path) -> None:
        """
        Load the given configuration file.

        Args:
            repository: The configuration repository.
            name: The configuration key name.
            path: The path to the configuration file.
        """
        # Load the configuration file
        spec = __import__("importlib.util").util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            return

        module = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get the config dict from the module
        if hasattr(module, "config"):
            config_data = module.config
            repository.add(name, config_data)

    def get_nested_directory(self, file: Path, config_path: Path) -> str:
        """
        Get the nested directory for a configuration file.

        Args:
            file: The configuration file path.
            config_path: The base configuration directory path.

        Returns:
            The nested directory path with trailing slash, or empty string.
        """
        relative_path = file.relative_to(config_path)
        directory_parts = relative_path.parts[:-1]

        if directory_parts:
            return "/".join(directory_parts) + "/"
        return ""
