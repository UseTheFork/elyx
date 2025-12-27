from typing import Callable


class EnvironmentDetector:
    """Detect the application's current environment."""

    def detect(self, callback: Callable, console_args: list[str] | None = None) -> str:
        """
        Detect the application's current environment.

        Args:
            callback: Closure that returns the environment name.
            console_args: Console arguments to check for --env flag.

        Returns:
            Environment name.
        """
        if console_args:
            return self.detect_console_environment(callback, console_args)

        return self.detect_web_environment(callback)

    def detect_web_environment(self, callback: Callable) -> str:
        """
        Set the application environment for a web request.

        Args:
            callback: Closure that returns the environment name.

        Returns:
            Environment name.
        """
        return callback()

    def detect_console_environment(self, callback: Callable, args: list[str]) -> str:
        """
        Set the application environment from command-line arguments.

        Args:
            callback: Closure that returns the environment name.
            args: Console arguments.

        Returns:
            Environment name.
        """
        value = self.get_environment_argument(args)
        if value is not None:
            return value

        return self.detect_web_environment(callback)

    def get_environment_argument(self, args: list[str]) -> str | None:
        """
        Get the environment argument from the console.

        Args:
            args: Console arguments.

        Returns:
            Environment name or None if not found.
        """
        for i, value in enumerate(args):
            if value == "--env":
                return args[i + 1] if i + 1 < len(args) else None

            if value.startswith("--env="):
                parts = value.split("=", 1)
                return parts[1] if len(parts) > 1 else None

        return None
