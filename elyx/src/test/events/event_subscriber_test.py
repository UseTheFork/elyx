from test.base_test import BaseTest


class ExampleSubscriber:
    """Example subscriber for testing."""

    def subscribe(self, dispatcher):
        """Subscribe to events."""
        return "foo"


# Global test storage for DeclarativeSubscriber
test_storage = []


class DeclarativeSubscriber:
    """Subscriber that returns event-to-listener mappings."""

    def subscribe(self, dispatcher):
        return {
            "myEvent1": [
                "event_subscriber_test.DeclarativeSubscriber:listener1",
                "event_subscriber_test.DeclarativeSubscriber:listener2",
            ],
            "myEvent2": [
                "event_subscriber_test.DeclarativeSubscriber:listener3",
            ],
        }

    def listener1(self):
        test_storage.append("L1_")

    def listener2(self):
        test_storage.append("L2_")

    def listener3(self):
        test_storage.append("L3")


class TestEventsSubscriber(BaseTest):
    """Test suite for Event Subscriber functionality."""

    async def test_event_subscribers(self):
        """Test that event subscribers are registered correctly."""
        from unittest.mock import Mock

        from elyx.events.dispatcher import Dispatcher

        # Create a mock subscriber instance
        mock_subscriber = Mock()
        mock_subscriber.subscribe = Mock(return_value=None)

        # Create a mock container that returns the mock subscriber
        mock_container = Mock()
        mock_container.make = Mock(return_value=mock_subscriber)

        # Create dispatcher with mock container
        dispatcher = Dispatcher(mock_container)

        # Subscribe using class name
        await dispatcher.subscribe(ExampleSubscriber)

        # Verify container.make was called with the subscriber class
        mock_container.make.assert_called_once_with(ExampleSubscriber)

        # Verify subscriber.subscribe was called with the dispatcher
        mock_subscriber.subscribe.assert_called_once_with(dispatcher)

    async def test_event_subscribe_can_accept_object(self):
        """Test that event subscribers can accept object instances."""
        from unittest.mock import Mock

        from elyx.events.dispatcher import Dispatcher

        # Create a mock subscriber instance
        mock_subscriber = Mock()
        mock_subscriber.subscribe = Mock(return_value=None)

        # Create dispatcher with container
        dispatcher = Dispatcher(self.container)

        # Subscribe using object instance directly
        await dispatcher.subscribe(mock_subscriber)

        # Verify subscriber.subscribe was called with the dispatcher
        mock_subscriber.subscribe.assert_called_once_with(dispatcher)

    async def test_event_subscribe_can_return_mappings(self):
        """Test that event subscribers can return event-to-listener mappings."""
        from elyx.events.dispatcher import Dispatcher

        # Clear the global test storage
        test_storage.clear()

        # Register the subscriber class in the container
        self.container.bind(DeclarativeSubscriber)

        dispatcher = Dispatcher(self.container)
        await dispatcher.subscribe(DeclarativeSubscriber)

        await dispatcher.dispatch("myEvent1")
        assert test_storage == ["L1_", "L2_"]

        await dispatcher.dispatch("myEvent2")
        assert test_storage == ["L1_", "L2_", "L3"]
