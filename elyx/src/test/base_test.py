import pytest
from elyx.container.container import Container


class BaseTest:
    """Base test class for all Elyx tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures before each test method."""
        Container._instance = None  # Clear singleton
        self.container = Container()
        yield
        # Cleanup after test
        self.container.flush()
        Container._instance = None  # Clear after test too
