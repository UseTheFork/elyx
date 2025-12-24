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


class ExampleEvent:
    pass


class TestEventDispatcher(BaseTest):
    """Test suite for Event Dispatcher class."""

    async def test_basic_event_execution(self):
        """Test basic event execution with listeners."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate global state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(value):
            test_storage["event_result"] = value

        dispatcher.listen("foo", listener)
        response = await dispatcher.dispatch("foo", "bar")

        assert response == [None]
        assert test_storage["event_result"] == "bar"

        # we can still add listeners after the event has fired
        def append_listener(value):
            test_storage["event_result"] += value

        dispatcher.listen("foo", append_listener)

        await dispatcher.dispatch("foo", "bar")
        assert test_storage["event_result"] == "barbar"

    async def test_defer_event_execution(self):
        """Test that events are deferred during callback execution."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate global state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(value):
            test_storage["deferred_result"] = value

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

        def foo_listener(value):
            event_results.append(value)

        def bar_listener(value):
            event_results.append(value)

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

        def foo_listener(value):
            event_results.append(value)

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

        def foo_listener(value):
            event_results.append(value)

        def bar_listener(value):
            event_results.append(value)

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

        def foo_listener(value):
            event_results.append(value)

        def bar_listener(value):
            event_results.append(value)

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

        def defer_test_listener(event_obj):
            event_results.append("DeferTestEvent")

        def immediate_test_listener(event_obj):
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

        def first_listener(value):
            assert True
            return "here"

        def second_listener(value):
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

        def first_listener(value):
            return value

        def second_listener(value):
            test_storage["event_result"] = value
            return False

        def third_listener(value):
            raise Exception("should not be called")

        dispatcher.listen("foo", first_listener)
        dispatcher.listen("foo", second_listener)
        dispatcher.listen("foo", third_listener)

        response = await dispatcher.dispatch("foo", ["bar"])

        assert test_storage["event_result"] == "bar"
        assert response == ["bar", False]

    async def test_returning_falsy_values_continues_propagation(self):
        """Test that returning falsy values (except False) continues event propagation."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)

        def listener_zero(value):
            return 0

        def listener_empty_list(value):
            return []

        def listener_empty_string(value):
            return ""

        def listener_none(value):
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

        def first_listener(value):
            test_storage["event_result"] = value

        dispatcher.listen("update", first_listener)
        dispatcher.push("update", ["value"])

        def second_listener(value):
            test_storage["event_result"] += "_" + value

        dispatcher.listen("update", second_listener)

        assert "event_result" not in test_storage
        await dispatcher.flush("update")

        def third_listener(value):
            test_storage["event_result"] += value

        dispatcher.listen("update", third_listener)
        assert test_storage["event_result"] == "value_value"

    async def test_queued_events_can_be_forgotten(self):
        """Test that queued events can be forgotten."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {"event_test": "unset"}

        dispatcher = Dispatcher(self.container)

        def listener(value):
            test_storage["event_test"] = value

        dispatcher.push("update", ["taylor"])
        dispatcher.listen("update", listener)

        dispatcher.forget_pushed()
        await dispatcher.flush("update")

        assert test_storage["event_test"] == "unset"

    async def test_multiple_pushed_events_will_get_flushed(self):
        """Test that multiple pushed events will get flushed."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {"event_test": ""}

        dispatcher = Dispatcher(self.container)

        def listener(value):
            test_storage["event_test"] += value

        dispatcher.push("update", ["hello "])
        dispatcher.push("update", ["world"])
        dispatcher.listen("update", listener)

        await dispatcher.flush("update")

        assert test_storage["event_test"] == "hello world"

    async def test_push_method_can_accept_object_as_payload(self):
        """Test that push method can accept an object as payload."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        event_instance = DeferTestEvent()

        def listener(value):
            test_storage["event_test"] = value

        dispatcher.push(DeferTestEvent, event_instance)
        dispatcher.listen(DeferTestEvent, listener)

        await dispatcher.flush(DeferTestEvent)

        assert test_storage["event_test"] is event_instance

    async def test_wildcard_listeners(self):
        """Test that wildcard listeners are called for matching events."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def regular_listener():
            test_storage["event_test"] = "regular"

        def wildcard_listener(event, payload):
            test_storage["event_test"] = "wildcard"

        def nope_listener(event, payload):
            test_storage["event_test"] = "nope"

        dispatcher.listen("foo.bar", regular_listener)
        dispatcher.listen("foo.*", wildcard_listener)
        dispatcher.listen("bar.*", nope_listener)

        response = await dispatcher.dispatch("foo.bar")

        assert response == [None, None]
        assert test_storage["event_test"] == "wildcard"

    async def test_wildcard_listeners_with_responses(self):
        """Test that wildcard listeners return responses for matching events."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)

        def regular_listener(payload=None):
            return "regular"

        def wildcard_listener(event, payload):
            return "wildcard"

        def nope_listener(event, payload):
            return "nope"

        dispatcher.listen("foo.bar", regular_listener)
        dispatcher.listen("foo.*", wildcard_listener)
        dispatcher.listen("bar.*", nope_listener)

        response = await dispatcher.dispatch("foo.bar")

        assert response == ["regular", "wildcard"]

    async def test_wildcard_listeners_cache_flushing(self):
        """Test that wildcard listeners cache is flushed when new listeners are added."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def cached_wildcard_listener(event, payload):
            test_storage["event_test"] = "cached_wildcard"

        dispatcher.listen("foo.*", cached_wildcard_listener)
        await dispatcher.dispatch("foo.bar")
        assert test_storage["event_test"] == "cached_wildcard"

        def new_wildcard_listener(event, payload):
            test_storage["event_test"] = "new_wildcard"

        dispatcher.listen("foo.*", new_wildcard_listener)
        await dispatcher.dispatch("foo.bar")
        assert test_storage["event_test"] == "new_wildcard"

    async def test_listeners_can_be_removed(self):
        """Test that listeners can be removed using forget."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(value):
            test_storage["event_test"] = "foo"

        dispatcher.listen("foo", listener)
        dispatcher.forget("foo")
        await dispatcher.dispatch("foo")

        assert "event_test" not in test_storage

    async def test_wildcard_listeners_can_be_removed(self):
        """Test that wildcard listeners can be removed using forget."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(event, payload):
            test_storage["event_test"] = "foo"

        dispatcher.listen("foo.*", listener)
        dispatcher.forget("foo.*")
        await dispatcher.dispatch("foo.bar")

        assert "event_test" not in test_storage

    async def test_has_wildcard_listeners(self):
        """Test that has_wildcard_listeners correctly identifies wildcard listeners."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)

        def listener(value):
            pass

        dispatcher.listen("foo", listener)
        assert dispatcher.has_wildcard_listeners("foo") is False

        dispatcher.listen("foo*", listener)
        assert dispatcher.has_wildcard_listeners("foo") is True

    async def test_listeners_can_be_found(self):
        """Test that listeners can be found using has_listeners."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)
        assert dispatcher.has_listeners("foo") is False

        def listener(value):
            pass

        dispatcher.listen("foo", listener)
        assert dispatcher.has_listeners("foo") is True

    async def test_wildcard_listeners_can_be_found(self):
        """Test that wildcard listeners can be found using has_listeners."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)
        assert dispatcher.has_listeners("foo.*") is False

        def listener(event, payload):
            pass

        dispatcher.listen("foo.*", listener)
        assert dispatcher.has_listeners("foo.*") is True
        assert dispatcher.has_listeners("foo.bar") is True

    async def test_event_passed_first_to_wildcards(self):
        """Test that event name is passed first to wildcard listeners."""
        from elyx.events.dispatcher import Dispatcher

        # Test wildcard listener receives event name and payload
        dispatcher = Dispatcher(self.container)

        def wildcard_listener(event, data):
            assert event == "foo.bar"
            assert data == ["first", "second"]

        dispatcher.listen("foo.*", wildcard_listener)
        await dispatcher.dispatch("foo.bar", ["first", "second"])

        # Test regular listener receives unpacked payload
        dispatcher2 = Dispatcher(self.container)

        def regular_listener(first, second):
            assert first == "first"
            assert second == "second"

        dispatcher2.listen("foo.bar", regular_listener)
        await dispatcher2.dispatch("foo.bar", ["first", "second"])

    async def test_classes_work(self):
        """Test that event classes work with the dispatcher."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(event):
            test_storage["event_test"] = "baz"

        dispatcher.listen(ExampleEvent, listener)
        await dispatcher.dispatch(ExampleEvent())

        assert test_storage["event_test"] == "baz"

    async def test_classes_work_with_anonymous_listeners(self):
        """Test that event classes work with anonymous listeners."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(event, payload):
            test_storage["event_test"] = "qux"

        dispatcher.listen(listener)
        await dispatcher.dispatch(ExampleEvent())

        assert test_storage["event_test"] == "qux"

    async def test_event_classes_are_payload(self):
        """Test that event class instances are passed as payload to listeners."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage dict to simulate state
        test_storage = {}

        dispatcher = Dispatcher(self.container)

        def listener(event):
            test_storage["event_test"] = event

        dispatcher.listen(ExampleEvent, listener)
        event_instance = ExampleEvent()
        await dispatcher.dispatch(event_instance, ["foo"])

        assert test_storage["event_test"] is event_instance
