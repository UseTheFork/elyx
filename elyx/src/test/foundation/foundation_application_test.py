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


class TestFoundationApplication(BaseTest):
    """Test suite for Application class."""

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
