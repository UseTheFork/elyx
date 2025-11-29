import importlib.util
import sys
from pathlib import Path


def main():
    cwd = Path.cwd()

    # Check if bootstrap directory exists
    bootstrap_dir = cwd / "bootstrap"
    if not bootstrap_dir.exists() or not bootstrap_dir.is_dir():
        raise FileNotFoundError(f"Bootstrap directory not found at: {bootstrap_dir}")

    # Check if app.py exists in bootstrap directory
    app_file = bootstrap_dir / "app.py"
    if not app_file.exists() or not app_file.is_file():
        raise FileNotFoundError(f"app.py not found in bootstrap directory at: {app_file}")

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location("bootstrap.app", app_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from: {app_file}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["bootstrap.app"] = module
    spec.loader.exec_module(module)

    # Get the application object
    if not hasattr(module, "application"):
        raise AttributeError(f"'application' not found in {app_file}")

    application = module.application
    status = application.handle_command()

    sys.exit(status)
