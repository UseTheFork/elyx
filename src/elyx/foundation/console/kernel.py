import importlib.util
import inspect
from pathlib import Path
from typing import List


class ConsoleKernel:
    """Console kernel for handling command registration and execution."""

    def __init__(self):
        self._commands = []
        self._command_paths = []
        self._command_route_paths = []

    def add_commands(self, commands: List[type]) -> None:
        """Register command classes directly."""
        self._commands.extend(commands)

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
                    self._commands.append(obj)

    def _load_command_routes(self, file: Path) -> None:
        """Load and execute command route file."""
        spec = importlib.util.spec_from_file_location(file.stem, file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
