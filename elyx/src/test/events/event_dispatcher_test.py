from test.base_test import BaseTest


class DeferTestEvent:
    pass


class ImmediateTestEvent:
    pass


class TestEventListener:
    def handle(self, foo, bar):
        return "baz"

    def on_foo_event(self, foo, bar):
        return "baz"


class TestEventDispatcher(BaseTest):
    """Test suite for Event Dispatcher class."""

    async def test_basic_event_execution(self):
        """Test basic event execution with listeners."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate global state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(event, payload):
            test_storage["event_result"] = payload

        dispatcher.listen("foo", listener)
        response = await dispatcher.dispatch("foo", "bar")

        assert response == [None]
        assert test_storage["event_result"] == "bar"

        # we can still add listeners after the event has fired
        def append_listener(event, payload):
            test_storage["event_result"] += payload

        dispatcher.listen("foo", append_listener)

        await dispatcher.dispatch("foo", "bar")
        assert test_storage["event_result"] == "barbar"

    async def test_defer_event_execution(self):
        """Test that events are deferred during callback execution."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate global state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(event, payload):
            test_storage["deferred_result"] = payload

        dispatcher.listen("foo", listener)

        async def callback():
            await dispatcher.dispatch("foo", "bar")
            assert "deferred_result" not in test_storage
            return "callback_result"

        result = await dispatcher.defer(callback)

        assert result == "callback_result"
        assert test_storage["deferred_result"] == "bar"

    async def test_defer_multiple_events(self):
        """Test that multiple events can be deferred."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage list to collect event results
        event_results = []

        dispatcher = Dispatcher(self.container)

        def foo_listener(event, payload):
            event_results.append(payload)

        def bar_listener(event, payload):
            event_results.append(payload)

        dispatcher.listen("foo", foo_listener)
        dispatcher.listen("bar", bar_listener)

        async def callback():
            await dispatcher.dispatch("foo", "foo")
            await dispatcher.dispatch("bar", "bar")
            assert event_results == []

        await dispatcher.defer(callback)

        assert event_results == ["foo", "bar"]

    async def test_defer_nested_events(self):
        """Test that nested deferred events are handled correctly."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage list to collect event results
        event_results = []

        dispatcher = Dispatcher(self.container)

        def foo_listener(event, payload):
            event_results.append(payload)

        dispatcher.listen("foo", foo_listener)

        async def outer_callback():
            await dispatcher.dispatch("foo", "outer1")

            async def inner_callback():
                await dispatcher.dispatch("foo", "inner")
                assert event_results == []

            await dispatcher.defer(inner_callback)

            assert event_results == ["inner"]
            await dispatcher.dispatch("foo", "outer2")

        await dispatcher.defer(outer_callback)

        assert event_results == ["inner", "outer1", "outer2"]

    async def test_defer_specific_events(self):
        """Test that only specific events can be deferred."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage list to collect event results
        event_results = []

        dispatcher = Dispatcher(self.container)

        def foo_listener(event, payload):
            event_results.append(payload)

        def bar_listener(event, payload):
            event_results.append(payload)

        dispatcher.listen("foo", foo_listener)
        dispatcher.listen("bar", bar_listener)

        async def callback():
            await dispatcher.dispatch("foo", "deferred")
            await dispatcher.dispatch("bar", "immediate")

            assert event_results == ["immediate"]

        await dispatcher.defer(callback, ["foo"])

        assert event_results == ["immediate", "deferred"]

    async def test_defer_specific_nested_events(self):
        """Test that only specific nested events can be deferred."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage list to collect event results
        event_results = []

        dispatcher = Dispatcher(self.container)

        def foo_listener(event, payload):
            event_results.append(payload)

        def bar_listener(event, payload):
            event_results.append(payload)

        dispatcher.listen("foo", foo_listener)
        dispatcher.listen("bar", bar_listener)

        async def outer_callback():
            await dispatcher.dispatch("foo", "outer-deferred")
            await dispatcher.dispatch("bar", "outer-immediate")

            assert event_results == ["outer-immediate"]

            async def inner_callback():
                await dispatcher.dispatch("foo", "inner-deferred")
                await dispatcher.dispatch("bar", "inner-immediate")

                assert event_results == ["outer-immediate", "inner-immediate"]

            await dispatcher.defer(inner_callback, ["foo"])

            assert event_results == ["outer-immediate", "inner-immediate", "inner-deferred"]

        await dispatcher.defer(outer_callback, ["foo"])

        assert event_results == ["outer-immediate", "inner-immediate", "inner-deferred", "outer-deferred"]

    async def test_defer_specific_object_events(self):
        """Test that only specific object events can be deferred."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage list to collect event results
        event_results = []

        dispatcher = Dispatcher(self.container)

        def defer_test_listener(event, payload):
            event_results.append("DeferTestEvent")

        def immediate_test_listener(event, payload):
            event_results.append("ImmediateTestEvent")

        dispatcher.listen(DeferTestEvent, defer_test_listener)
        dispatcher.listen(ImmediateTestEvent, immediate_test_listener)

        async def callback():
            await dispatcher.dispatch(DeferTestEvent())
            await dispatcher.dispatch(ImmediateTestEvent())

            assert event_results == ["ImmediateTestEvent"]

        await dispatcher.defer(callback, [DeferTestEvent])

        assert event_results == ["ImmediateTestEvent", "DeferTestEvent"]

    async def test_halting_event_execution(self):
        """Test that event execution can be halted and return first non-null response."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)

        def first_listener(event, payload):
            assert True
            return "here"

        def second_listener(event, payload):
            raise Exception("should not be called")

        dispatcher.listen("foo", first_listener)
        dispatcher.listen("foo", second_listener)

        response = await dispatcher.dispatch("foo", ["bar"], halt=True)
        assert response == "here"

        response = await dispatcher.until("foo", ["bar"])
        assert response == "here"

    async def test_response_when_no_listeners_are_set(self):
        """Test that dispatch returns empty list or None when no listeners are set."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)
        response = await dispatcher.dispatch("foo")

        assert response == []

        response = await dispatcher.dispatch("foo", [], halt=True)
        assert response is None

    async def test_returning_false_stops_propagation(self):
        """Test that returning False from a listener stops event propagation."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate global state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def first_listener(event, payload):
            return payload

        def second_listener(event, payload):
            test_storage["event_result"] = payload
            return False

        def third_listener(event, payload):
            raise Exception("should not be called")

        dispatcher.listen("foo", first_listener)
        dispatcher.listen("foo", second_listener)
        dispatcher.listen("foo", third_listener)

        response = await dispatcher.dispatch("foo", ["bar"])

        assert test_storage["event_result"] == ["bar"]
        assert response == [["bar"], False]

    async def test_returning_falsy_values_continues_propagation(self):
        """Test that returning falsy values (except False) continues event propagation."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)

        def listener_zero(event, payload):
            return 0

        def listener_empty_list(event, payload):
            return []

        def listener_empty_string(event, payload):
            return ""

        def listener_none(event, payload):
            return None

        dispatcher.listen("foo", listener_zero)
        dispatcher.listen("foo", listener_empty_list)
        dispatcher.listen("foo", listener_empty_string)
        dispatcher.listen("foo", listener_none)

        response = await dispatcher.dispatch("foo", ["bar"])

        assert response == [0, [], "", None]

    async def test_container_resolution_of_event_handlers(self):
        """Test that the container can resolve event handlers from class@method strings."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)

        # Register the TestEventListener in the container
        self.container.bind(TestEventListener, lambda: TestEventListener())

        # Listen using the class:method syntax
        dispatcher.listen("foo", "event_dispatcher_test.TestEventListener:on_foo_event")

        # Dispatch the event
        response = await dispatcher.dispatch("foo", ["foo", "bar"])

        assert response == ["baz"]

    async def test_container_resolution_of_event_handlers_with_default_methods(self):
        """Test that the container can resolve event handlers with default methods."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)

        # Register the TestEventListener in the container
        self.container.bind(TestEventListener, lambda: TestEventListener())

        # Listen using just the class (should use default 'handle' method)
        dispatcher.listen("foo", TestEventListener)

        # Dispatch the event
        response = await dispatcher.dispatch("foo", ["foo", "bar"])

        assert response == ["baz"]

    async def test_queued_events_are_fired(self):
        """Test that queued events are fired when flush is called."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def first_listener(event, payload):
            test_storage["event_result"] = payload

        dispatcher.listen("update", first_listener)
        dispatcher.push("update", ["value"])

        def second_listener(event, payload):
            test_storage["event_result"] += "_" + payload

        dispatcher.listen("update", second_listener)

        assert "event_result" not in test_storage
        await dispatcher.flush("update")

        def third_listener(event, payload):
            test_storage["event_result"] += payload

        dispatcher.listen("update", third_listener)
        assert test_storage["event_result"] == "value_value"
