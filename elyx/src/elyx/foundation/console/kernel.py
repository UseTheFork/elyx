from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

from elyx.console.application import Application as ConsoleApplication
from elyx.contracts.console.kernel_contract import KernelContract
from elyx.foundation.bootstrap.boot_providers import BootProviders
from elyx.foundation.bootstrap.register_providers import RegisterProviders

if TYPE_CHECKING:
    from elyx.foundation.application import Application


# AI: would it make more sense to create various mixins to inject things like `Application` then we can do a check in make and boot these mixens etc ai?


class ConsoleKernel(KernelContract):
    """Console kernel for handling command registration and execution."""

    elyx: ConsoleApplication | None = None

    commands: list = []
    command_paths: list = []
    command_route_paths: list = []

    command_started_at: float | None = None
    commands_loaded: bool = False

    def bootstrappers(self):
        return [
            RegisterProviders,
            BootProviders,
        ]

    def __init__(self, app: Application):
        self.app = app

    async def bootstrap(self) -> None:
        """
        Bootstrap the application for artisan commands.

        Returns:
            None
        """
        if not self.app.has_been_bootstrapped():
            await self.app.bootstrap_with(self.bootstrappers())

        if not self.commands_loaded:
            # Auto-discover commands from app/commands/ directory
            if self.app.base_path:
                commands_dir = self.app.base_path / "app" / "console" / "commands"
                if commands_dir.exists() and commands_dir.is_dir():
                    self._discover_commands_from_directory(commands_dir)

            # if self.should_discover_commands():
            #     self.discover_commands()

            self.commands_loaded = True

    def _discover_commands_from_directory(self, directory: Path) -> None:
        """
        Auto-discover command classes from a directory.

        Args:
            directory: Path to the directory containing command files.
        """
        for file in directory.glob("*.py"):
            if file.name.startswith("_"):
                continue
            self._load_commands_from_file(file)

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

    async def call(
        self, command: str, parameters: dict[str, Any] | None = None, output_buffer: Any | None = None
    ) -> int:
        return await self.get_elyx().call(command, parameters, output_buffer)

    async def handle(self, input: list[str]) -> int:
        """
        Handle an incoming console command.

        Returns:
            Exit status code.
        """
        try:
            await self.bootstrap()

            return await self.get_elyx().run(input)
        except Exception as e:
            print("TODO: ADD EXCEPTIONS CATCHING HERE")
            print(e)
            return 1

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
            self.elyx.resolve_commands(self.commands)

        return self.elyx

    async def all(self):
        await self.bootstrap()

        return self.get_elyx().all()

    def output(self):
        pass

    def queue(self):
        pass

    def terminate(self):
        pass
