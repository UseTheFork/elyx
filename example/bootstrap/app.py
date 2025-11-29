from pathlib import Path

from elyx.foundation.application import Application

from ..app.test_command import TestCommand

application = Application.configure(Path(__file__)).with_commands([TestCommand]).create()
