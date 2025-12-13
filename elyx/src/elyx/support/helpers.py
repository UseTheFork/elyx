from elyx.foundation.application import Application

_app: Application | None = None


def app(abstract=None, **kwargs):
    """Get the application instance or resolve from container."""
    global _app
    if _app is None:
        raise RuntimeError("Application not initialized")

    if abstract is None:
        return _app

    return _app.make(abstract, **kwargs)


def config(key: str = None, default=None):
    """Get configuration value."""
    repository = app("config")
    if key is None:
        return repository
    return repository.get(key, default)


def str(value: str = ""):
    """Create a new Stringable instance."""
    # When you implement Str helper class
    pass
