#!/usr/bin/env python
"""Elyx's command-line utility entrypoint."""

import os
from pathlib import Path

from app.test_command import TestCommand


def main():
    """Run administrative tasks."""
    os.environ.setdefault("ELYX_SETTINGS_MODULE", "config.settings")
    try:
        # from django.core.management import execute_from_command_line
        from elyx.foundation.application import Application

        application = Application.configure(Path(__file__)).with_commands([TestCommand]).create()

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Elyx. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
