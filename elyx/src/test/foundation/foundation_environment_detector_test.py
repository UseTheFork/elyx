from elyx.foundation.environment_detector import EnvironmentDetector
from test.base_test import BaseTest


class TestEnvironmentDetector(BaseTest):
    """Test suite for EnvironmentDetector class."""

    def test_closure_can_be_used_for_custom_environment_detection(self):
        """Test that a closure can be used for custom environment detection."""
        env = EnvironmentDetector()

        result = env.detect(lambda: "foobar")

        assert "foobar" == result

    def test_console_environment_detection(self):
        """Test console environment detection with --env=value format."""
        env = EnvironmentDetector()

        result = env.detect(lambda: "foobar", ["--env=local"])

        assert "local" == result

    def test_console_environment_detection_separated_with_space(self):
        """Test console environment detection with --env value format."""
        env = EnvironmentDetector()

        result = env.detect(lambda: "foobar", ["--env", "local"])

        assert "local" == result

    def test_console_environment_detection_with_no_value(self):
        """Test console environment detection with --env but no value falls back to callback."""
        env = EnvironmentDetector()

        result = env.detect(lambda: "foobar", ["--env"])

        assert "foobar" == result

    def test_console_environment_detection_does_not_use_argument_that_starts_with_env(self):
        """Test that arguments starting with 'env' but not '--env' are ignored."""
        env = EnvironmentDetector()

        result = env.detect(lambda: "foobar", ["--envelope=mail"])

        assert "foobar" == result

    def test_console_environment_detection_does_not_use_argument_that_starts_with_env_separated_with_space(self):
        """Test that arguments starting with 'env' but not '--env' are ignored when separated with space."""
        env = EnvironmentDetector()

        result = env.detect(lambda: "foobar", ["--envelope", "mail"])

        assert "foobar" == result

    def test_console_environment_detection_does_not_use_argument_that_starts_with_env_with_no_value(self):
        """Test that arguments starting with 'env' but not '--env' are ignored."""
        env = EnvironmentDetector()

        result = env.detect(lambda: "foobar", ["--envelope"])

        assert "foobar" == result
