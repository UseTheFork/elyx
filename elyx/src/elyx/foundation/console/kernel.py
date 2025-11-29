import importlib.util
import inspect
from pathlib import Path
from typing import List

from elyx.console.application import Application as ConsoleApplication
from elyx.contracts.console.kernel_contract import KernelContract
from elyx.foundation.application import Application


class ConsoleKernel(KernelContract):
    """Console kernel for handling command registration and execution."""

    app: Application | None = None
    elyx: ConsoleApplication | None = None

    commands: list = []
    command_paths: list = []
    command_route_paths: list = []

    command_started_at: float | None = None

    def __init__(self, app: Application):
        self.app = app

    def add_commands(self, commands: List[type]) -> None:
        """Register command classes directly."""
        self.commands.extend(commands)

    def add_command_paths(self, paths: List[Path]) -> None:
        """Register directories to scan for commands."""
        for path in paths:
            if path.is_dir():
                # Scan directory for Python files
                for file in path.glob("*.py"):
                    if file.name.startswith("_"):
                        continue
                    self._load_commands_from_file(file)

    def add_command_route_paths(self, paths: List[Path]) -> None:
        """Register command route files."""
        for path in paths:
            if path.is_file():
                self._load_command_routes(path)

    def _load_commands_from_file(self, file: Path) -> None:
        """Load command classes from a Python file."""
        spec = importlib.util.spec_from_file_location(file.stem, file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find command classes in module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, "handle") and not name.startswith("_"):
                    self.commands.append(obj)

    def _load_command_routes(self, file: Path) -> None:
        """Load and execute command route file."""
        spec = importlib.util.spec_from_file_location(file.stem, file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

    def handle(self) -> int:
        """
        Handle an incoming console command.

        Returns:
            Exit status code.
        """
        return self.get_elyx().run()

    def get_elyx(self) -> ConsoleApplication:
        """
        Get the Elyx console application instance.

        Returns:
            ConsoleApplication instance.
        """
        if self.elyx is None:
            # Create the console application
            self.elyx = ConsoleApplication(self.app)

            # Register all commands
            for command in self.commands:
                # Get command name (assume commands have a 'name' attribute or use class name)
                command_name = getattr(command, "name", command.__name__.lower())
                self.elyx.register(command_name, command)

        return self.elyx
