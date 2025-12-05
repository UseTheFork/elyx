import re

from rich.console import Console

from elyx.console.argument_parser import ArgumentParser
from elyx.contracts.console.command import Command as CommandContract
from elyx.contracts.container.container import Container


class Command(CommandContract):
    """Console application for handling command execution."""

    name: str = ""
    description: str = ""
    signature: str = ""
    hidden: bool = False
    console: Console | None = None

    def __init__(self):
        """Initialize command and parse signature if provided."""
        if not self.signature:
            raise ValueError(f"Command {self.__class__.__name__} must define a signature")

        self._parsed_args = None
        self._parse_signature()

    def _parse_signature(self):
        """Parse signature into name and build argparse."""
        # Extract command name (everything before first space or {)
        match = re.match(r"^([^\s{]+)", self.signature)
        if match and not self.name:
            self.name = match.group(1)

        # Build parser
        self._parser = ArgumentParser(
            prog=self.name,
            description=self.description,
        )

        # Find all arguments {arg} and options {--opt}
        args_pattern = r"\{([^}]+)\}"
        for arg_match in re.finditer(args_pattern, self.signature):
            arg_def = arg_match.group(1)
            self._add_argument_to_parser(arg_def)

    def _add_argument_to_parser(self, arg_def: str):
        """
        Add a single argument/option to the parser.

        Supports:
        - {user} - Required argument
        - {user?} - Optional argument
        - {user=foo} - Optional argument with default value
        - {--queue} - Flag option
        - {--queue=} - Option with required value
        - {--queue=default} - Option with default value
        - {--Q|queue=} - Option with shortcut
        - {user*} - Multiple input values
        - {user?*} - Optional multiple values
        - {--id=*} - Option array
        """
        # Option: {--option} or {--option=}
        if arg_def.startswith("--"):
            # Handle shortcuts: {--Q|queue=}
            if "|" in arg_def:
                shortcut_part, rest = arg_def[2:].split("|", 1)
                shortcut = f"-{shortcut_part}"
                option_name = rest.split("=")[0].split(":")[0].strip()
            else:
                shortcut = None
                option_name = arg_def[2:].split("=")[0].split(":")[0].strip()

            args = [f"--{option_name}"]
            if shortcut:
                args.insert(0, shortcut)

            # Flag option: {--queue}
            if "=" not in arg_def:
                self._parser.add_argument(*args, action="store_true")
            # Array option: {--id=*}
            elif "=*" in arg_def:
                self._parser.add_argument(*args, action="append")
            # Option with default: {--queue=default}
            elif "=" in arg_def and not arg_def.endswith("="):
                default_value = arg_def.split("=", 1)[1].split(":")[0].strip()
                self._parser.add_argument(*args, default=default_value)
            # Required value: {--queue=}
            else:
                self._parser.add_argument(*args, required=True)

        # Positional argument: {user} or {user?} or {user*}
        else:
            # Handle default values: {user=foo}
            if "=" in arg_def:
                arg_name, default_value = arg_def.split("=", 1)
                arg_name = arg_name.rstrip("?*").strip()
                default_value = default_value.split(":")[0].strip()
                self._parser.add_argument(arg_name, nargs="?", default=default_value)
            # Handle multiple values: {user*} or {user?*}
            elif "*" in arg_def:
                arg_name = arg_def.rstrip("?*").strip()
                is_optional = "?" in arg_def
                if is_optional:
                    self._parser.add_argument(arg_name, nargs="*")
                else:
                    self._parser.add_argument(arg_name, nargs="+")
            # Handle optional: {user?}
            elif arg_def.endswith("?"):
                arg_name = arg_def.rstrip("?").strip()
                self._parser.add_argument(arg_name, nargs="?")
            # Required argument: {user}
            else:
                arg_name = arg_def.strip()
                self._parser.add_argument(arg_name)

    def parse_args(self, args: list[str]):
        """
        Parse command line arguments.

        Args:
            args: List of command line arguments to parse.
        """
        self._parsed_args = self._parser.parse_args(args)

    def argument(self, key: str):
        """
        Get the value of a command argument.

        Args:
            key: The argument name.

        Returns:
            The argument value or None if not found.
        """
        if self._parsed_args is None:
            return None
        return getattr(self._parsed_args, key, None)

    def arguments(self) -> dict:
        """
        Get all command arguments as a dictionary.

        Returns:
            Dictionary of all arguments.
        """
        if self._parsed_args is None:
            return {}
        return vars(self._parsed_args)

    def option(self, key: str):
        """
        Get the value of a command option.

        Args:
            key: The option name.

        Returns:
            The option value or None if not found.
        """
        return self.argument(key)

    def options(self) -> dict:
        """
        Get all command options as a dictionary.

        Returns:
            Dictionary of all options.
        """
        return self.arguments()

    def get_elyx(self) -> Container:
        """
        Get the Elyx console application instance.

        Returns:
            ConsoleApplication instance.
        """
        return self.elyx

    def set_elyx(self, elyx: Container) -> None:
        """
        Set the Elyx application instance.

        Returns:
            ConsoleApplication instance.
        """
        self.elyx = elyx
