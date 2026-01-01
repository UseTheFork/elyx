from abc import ABC, abstractmethod
from pathlib import Path

from test.base_test import BaseTest


class AbstractClassStub(ABC):
    @abstractmethod
    def get_value(self):
        pass


class ConcreteClassStub(AbstractClassStub):
    def get_value(self):
        pass


class NonContractBackedClass:
    pass


class ConcreteTerminator:
    counter = 0

    def terminate(self):
        ConcreteTerminator.counter += 1


class TestFoundationApplication(BaseTest):
    """Test suite for Application class."""

    def test_termination_callbacks_can_accept_colon_notation(self):
        """Test that termination callbacks can accept class:method notation."""
        from elyx.foundation.application import Application

        ConcreteTerminator.counter = 0

        app = Application()
        app.terminating("foundation_application_test.ConcreteTerminator::terminate")
        # app.terminating(f"{ConcreteTerminator.__module__}.{ConcreteTerminator.__qualname__}:terminate")

        app.terminate()

        assert 1 == ConcreteTerminator.counter

    def test_booting_callbacks(self):
        """Test that booting callbacks are executed during boot."""
        from elyx.foundation.application import Application

        application = Application()

        counter = {"value": 0}

        def closure(app):
            counter["value"] += 1
            assert application is app

        def closure2(app):
            counter["value"] += 1
            assert application is app

        application.booting(closure)
        application.booting(closure2)

        application.boot()

        assert 2 == counter["value"]

    def test_booted_callbacks(self):
        """Test that booted callbacks are executed during and after boot."""
        from elyx.foundation.application import Application

        application = Application()

        counter = {"value": 0}

        def closure(app):
            counter["value"] += 1
            assert application is app

        def closure2(app):
            counter["value"] += 1
            assert application is app

        def closure3(app):
            counter["value"] += 1
            assert application is app

        application.booting(closure)
        application.booted(closure)
        application.booted(closure2)
        application.boot()

        assert 3 == counter["value"]

        application.booted(closure3)

        assert 4 == counter["value"]

    def test_macroable(self):
        """Test that Application supports macros for dynamic method registration."""
        from elyx.foundation.application import Application

        app = Application()
        app["env"] = "foo"

        app.macro("foo", lambda self: self.environment("foo"))

        assert app.foo()

        app["env"] = "bar"

        assert not app.foo()

    def test_use_config_path(self):
        """Test that use_config_path sets a custom configuration directory path."""
        from elyx.foundation.application import Application
        from elyx.foundation.bootstrap.load_configuration import LoadConfiguration

        # Set a container instance as singleton
        app = Application()

        test_dir = Path(__file__).parent
        config_path = test_dir / "fixtures" / "config"

        app.use_config_path(config_path)
        app.bootstrap_with([LoadConfiguration])

        config = app.make("config")

        assert "bar" == config.get("app.foo")

    def test_merging_config(self):
        """Test that configuration files are properly merged from the config directory."""
        from elyx.foundation.application import Application
        from elyx.foundation.bootstrap.load_configuration import LoadConfiguration

        # Set a container instance as singleton
        app = Application()

        test_dir = Path(__file__).parent
        config_path = test_dir / "fixtures" / "config"

        app.use_config_path(config_path)
        app.bootstrap_with([LoadConfiguration])

        config = app.make("config")

        assert "bar" == config.get("app.foo")

        assert "overwrite" == config.get("broadcasting.default")
        assert "broadcasting" == config.get("broadcasting.custom_option")

        assert isinstance(config.get("broadcasting.connections.reverb"), dict)
        assert {"overwrite": True} == config.get("broadcasting.connections.reverb")
        assert {"merge": True} == config.get("broadcasting.connections.new")
