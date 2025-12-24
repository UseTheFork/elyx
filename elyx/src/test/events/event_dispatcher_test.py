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


class TestEvent:
    pass


class DisptachListener1:
    def __init__(self, test_storage):
        self.test_storage = test_storage
        self.test_storage.append("cons-1")

    def handle(self, event):
        self.test_storage.append("handle-1")


class DisptachListener2:
    def __init__(self, test_storage):
        self.test_storage = test_storage
        self.test_storage.append("cons-2")

    def handle(self, event):
        self.test_storage.append("handle-2")


class DisptachListener3:
    def __init__(self, test_storage):
        self.test_storage = test_storage
        self.test_storage.append("cons-3")

    def handle(self, event):
        self.test_storage.append("handle-3")


class DisptachListener2Falser:
    def __init__(self, test_storage):
        self.test_storage = test_storage
        self.test_storage.append("cons-2-falser")

    def handle(self, event):
        self.test_storage.append("handle-2-falser")
        return False


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

    async def test_nested_event(self):
        """Test that nested event listeners are registered and fired correctly."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage list to simulate state
        test_storage = []

        dispatcher = Dispatcher(self.container)

        def outer_listener():
            def inner_listener_1():
                test_storage.append("fired 1")

            def inner_listener_2():
                test_storage.append("fired 2")

            dispatcher.listen("event", inner_listener_1)
            dispatcher.listen("event", inner_listener_2)

        dispatcher.listen("event", outer_listener)

        await dispatcher.dispatch("event")
        assert test_storage == []

        await dispatcher.dispatch("event")
        assert test_storage == ["fired 1", "fired 2"]

    async def test_get_listeners(self):
        """Test that get_listeners returns the correct number of listeners."""
        from elyx.events.dispatcher import Dispatcher

        dispatcher = Dispatcher(self.container)
        dispatcher.listen(ExampleEvent, "Listener1")
        dispatcher.listen(ExampleEvent, "Listener2")
        listeners = dispatcher.get_listeners("event_dispatcher_test.ExampleEvent")
        assert len(listeners) == 2

        dispatcher.listen(ExampleEvent, "Listener3")
        listeners = dispatcher.get_listeners("event_dispatcher_test.ExampleEvent")
        assert len(listeners) == 3

    async def test_listeners_objects_creation_order(self):
        """Test that listener objects are re-resolved on each dispatch (no memoization)."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage list to simulate state
        test_storage = []

        dispatcher = Dispatcher(self.container)

        # Bind listeners with test_storage dependency
        self.container.bind(DisptachListener1, lambda c: DisptachListener1(test_storage))
        self.container.bind(DisptachListener2, lambda c: DisptachListener2(test_storage))
        self.container.bind(DisptachListener3, lambda c: DisptachListener3(test_storage))

        dispatcher.listen(TestEvent, DisptachListener1)
        dispatcher.listen(TestEvent, DisptachListener2)
        dispatcher.listen(TestEvent, DisptachListener3)

        # Attaching events does not make any objects
        assert test_storage == []

        await dispatcher.dispatch(TestEvent())

        # Dispatching event does not make an object of the event class
        assert test_storage == [
            "cons-1",
            "handle-1",
            "cons-2",
            "handle-2",
            "cons-3",
            "handle-3",
        ]

        await dispatcher.dispatch(TestEvent())

        # Event Objects are re-resolved on each dispatch (no memoization)
        assert test_storage == [
            "cons-1",
            "handle-1",
            "cons-2",
            "handle-2",
            "cons-3",
            "handle-3",
            "cons-1",
            "handle-1",
            "cons-2",
            "handle-2",
            "cons-3",
            "handle-3",
        ]

    async def test_listener_object_creation_is_lazy(self):
        """Test that listener objects are created lazily (only when needed)."""
        from elyx.events.dispatcher import Dispatcher

        # Create a test storage list to simulate state
        test_storage = []

        dispatcher = Dispatcher(self.container)

        # Bind listeners with test_storage dependency
        self.container.bind(DisptachListener1, lambda c: DisptachListener1(test_storage))
        self.container.bind(DisptachListener2, lambda c: DisptachListener2(test_storage))
        self.container.bind(DisptachListener2Falser, lambda c: DisptachListener2Falser(test_storage))
        self.container.bind(DisptachListener3, lambda c: DisptachListener3(test_storage))

        dispatcher.listen(TestEvent, DisptachListener1)
        dispatcher.listen(TestEvent, DisptachListener2Falser)
        dispatcher.listen(TestEvent, DisptachListener3)
        dispatcher.listen(ExampleEvent, DisptachListener2)

        test_storage.clear()
        await dispatcher.dispatch(ExampleEvent())

        # It only resolves relevant listeners not all
        assert test_storage == ["cons-2", "handle-2"]

        test_storage.clear()
        await dispatcher.dispatch(TestEvent())

        # DisptachListener2Falser returns False, stopping propagation before DisptachListener3
        assert test_storage == [
            "cons-1",
            "handle-1",
            "cons-2-falser",
            "handle-2-falser",
        ]

        # Test with halt=True - need a listener that returns non-null
        class DisptachListener1WithReturn:
            def __init__(self, test_storage):
                self.test_storage = test_storage
                self.test_storage.append("cons-1")

            def handle(self, event):
                self.test_storage.append("handle-1")
                return "result"

        dispatcher2 = Dispatcher(self.container)
        test_storage2 = []

        self.container.bind(DisptachListener1WithReturn, lambda c: DisptachListener1WithReturn(test_storage2))
        self.container.bind(DisptachListener2Falser, lambda c: DisptachListener2Falser(test_storage2))
        self.container.bind(DisptachListener3, lambda c: DisptachListener3(test_storage2))

        dispatcher2.listen(TestEvent, DisptachListener1WithReturn)
        dispatcher2.listen(TestEvent, DisptachListener2Falser)
        dispatcher2.listen(TestEvent, DisptachListener3)

        test_storage2.clear()
        await dispatcher2.dispatch(TestEvent(), halt=True)

        # With halt=True, stops after first non-null response
        assert test_storage2 == [
            "cons-1",
            "handle-1",
        ]
