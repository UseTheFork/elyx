from abc import ABC, abstractmethod
from pathlib import Path

import pytest
from elyx.support import ServiceProvider
from test.base_test import BaseTest


class SampleClassStub(ABC):
    @abstractmethod
    def get_primitive(self):
        pass


class SampleClassImplementationStub(SampleClassStub):
    def __init__(self, primitive):
        self.primitive = primitive

    def get_primitive(self):
        return self.primitive


class InterfaceToImplementationDeferredServiceProvider(ServiceProvider):
    def register(self) -> None:
        """
        Register a booting callback to be run before the "boot" method is called.

        Args:
            callback: Callback to execute before boot.
        """
        self.app.bind(SampleClassStub, SampleClassImplementationStub)


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

    @pytest.fixture(autouse=True)
    def setup_application(self):
        """Set up Application instance before each test method."""
        from elyx.foundation import Application

        self.app = Application()
        yield
        self.app.flush()

    def test_termination_tests(self):
        """Test that termination callbacks are executed in order."""
        result = []

        def callback1():
            result.append(1)

        def callback2():
            result.append(2)

        def callback3():
            result.append(3)

        self.app.terminating(callback1)
        self.app.terminating(callback2)
        self.app.terminating(callback3)

        self.app.terminate()

        assert [1, 2, 3] == result

    def test_termination_callbacks_can_accept_colon_notation(self):
        """Test that termination callbacks can accept class:method notation."""
        ConcreteTerminator.counter = 0

        self.app.terminating("foundation_application_test.ConcreteTerminator:terminate")

        self.app.terminate()

        assert 1 == ConcreteTerminator.counter

    def test_booting_callbacks(self):
        """Test that booting callbacks are executed during boot."""
        counter = {"value": 0}

        def closure(app):
            counter["value"] += 1
            assert self.app is app

        def closure2(app):
            counter["value"] += 1
            assert self.app is app

        self.app.booting(closure)
        self.app.booting(closure2)

        self.app.boot()

        assert 2 == counter["value"]

    def test_after_bootstrapping_adds_closure(self):
        """Test that afterBootstrapping registers event listeners for bootstrapper completion."""
        from elyx.foundation import RegisterFacades

        closure_called = {"value": False}

        def closure():
            closure_called["value"] = True

        self.app.after_bootstrapping(RegisterFacades, closure)

        # Verify the listener was registered for the bootstrapped event
        events = self.app["events"]
        listeners = events.get_listeners(f"bootstrapped: {RegisterFacades.__module__}.{RegisterFacades.__qualname__}")

        assert len(listeners) > 0
        assert 0 in range(len(listeners))

    def test_booted_callbacks(self):
        """Test that booted callbacks are executed during and after boot."""
        counter = {"value": 0}

        def closure(app):
            counter["value"] += 1
            assert self.app is app

        def closure2(app):
            counter["value"] += 1
            assert self.app is app

        def closure3(app):
            counter["value"] += 1
            assert self.app is app

        self.app.booting(closure)
        self.app.booted(closure)
        self.app.booted(closure2)
        self.app.boot()

        assert 3 == counter["value"]

        self.app.booted(closure3)

        assert 4 == counter["value"]

    def test_macroable(self):
        """Test that Application supports macros for dynamic method registration."""
        self.app["env"] = "foo"

        self.app.macro("foo", lambda self: self.environment("foo"))

        assert self.app.foo()

        self.app["env"] = "bar"

        assert not self.app.foo()

    def test_use_config_path(self):
        """Test that use_config_path sets a custom configuration directory path."""
        from elyx.foundation.bootstrap.load_configuration import LoadConfiguration

        test_dir = Path(__file__).parent
        config_path = test_dir / "fixtures" / "config"

        self.app.use_config_path(config_path)
        self.app.bootstrap_with([LoadConfiguration])

        config = self.app.make("config")

        assert "bar" == config.get("app.foo")

    def test_merging_config(self):
        """Test that configuration files are properly merged from the config directory."""
        from elyx.foundation import LoadConfiguration

        test_dir = Path(__file__).parent
        config_path = test_dir / "fixtures" / "config"

        self.app.use_config_path(config_path)
        self.app.bootstrap_with([LoadConfiguration])

        config = self.app.make("config")

        assert "bar" == config.get("app.foo")

        assert "overwrite" == config.get("broadcasting.default")
        assert "broadcasting" == config.get("broadcasting.custom_option")

        assert isinstance(config.get("broadcasting.connections.reverb"), dict)
        assert {"overwrite": True} == config.get("broadcasting.connections.reverb")
        assert {"merge": True} == config.get("broadcasting.connections.new")

    def test_method_after_loading_environment_adds_closure(self):
        """Test that afterLoadingEnvironment registers event listeners for LoadEnvironmentVariables completion."""
        from elyx.foundation import LoadEnvironmentVariables

        closure_called = {"value": False}

        def closure():
            closure_called["value"] = True

        self.app.after_loading_environment(closure)

        # Verify the listener was registered for the bootstrapped event
        events = self.app["events"]
        listeners = events.get_listeners(
            f"bootstrapped: {LoadEnvironmentVariables.__module__}.{LoadEnvironmentVariables.__qualname__}"
        )

        assert len(listeners) > 0
        assert 0 in range(len(listeners))

    def test_debug_helper(self):
        """Test that has_debug_mode_enabled correctly returns the debug mode status from configuration."""
        from elyx.config import Repository
        from elyx.foundation import Application

        debug_off = Application()
        debug_off["config"] = Repository({"app": {"debug": False}})

        assert not debug_off.has_debug_mode_enabled()

        debug_on = Application()
        debug_on["config"] = Repository({"app": {"debug": True}})

        assert debug_on.has_debug_mode_enabled()

    def test_environment_helpers(self):
        """Test that environment helper methods correctly identify the current environment."""
        from elyx.foundation import Application

        local = Application()
        local["env"] = "local"

        assert local.is_local()
        assert not local.is_production()
        assert not local.running_unit_tests()

        production = Application()
        production["env"] = "production"

        assert production.is_production()
        assert not production.is_local()
        assert not production.running_unit_tests()

        testing = Application()
        testing["env"] = "testing"

        assert testing.running_unit_tests()
        assert not testing.is_local()
        assert not testing.is_production()

    def test_environment(self):
        """Test that environment method returns current environment and checks against patterns."""
        from elyx.foundation import Application

        app = Application()
        app["env"] = "foo"

        assert "foo" == app.environment()

        assert app.environment("foo")
        assert app.environment("f*")
        assert app.environment("foo", "bar")
        assert app.environment(["foo", "bar"])

        assert not app.environment("qux")
        assert not app.environment("q*")
        assert not app.environment("qux", "bar")
        assert not app.environment(["qux", "bar"])

    def test_deferred_service_is_loaded_when_accessing_implementation_through_interface(self):
        """Test that deferred service is loaded when accessing implementation through interface."""
        from elyx.foundation import Application

        app = Application()
        app.set_deferred_services(
            {
                SampleClassStub: SampleClassImplementationStub,
            }
        )
        instance = app.make(SampleClassStub)
        assert "foo" == instance.get_primitive()
