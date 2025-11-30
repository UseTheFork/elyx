#!/usr/bin/env python
"""Elyx's command-line utility entrypoint."""

import asyncio
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    os.environ.setdefault("ELYX_SETTINGS_MODULE", "config.settings")
    try:
        from elyx.foundation.application import Application

        # application = Application.configure(Path(__file__)).with_commands([TestCommand]).create()
        application = Application.configure(Path(__file__).parent).create()

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Elyx. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    asyncio.run(application.handle_command(sys.argv))


if __name__ == "__main__":
    main()
