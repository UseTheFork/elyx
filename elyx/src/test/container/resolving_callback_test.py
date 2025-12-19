from abc import ABC

from test.base_test import BaseTest


class ResolvingContractStub(ABC):
    pass


class ResolvingImplementationStub(ResolvingContractStub):
    pass


class ResolvingImplementationStubTwo(ResolvingContractStub):
    pass


class ResolvingImplementationStubThree:
    pass


class TestResolvingCallback(BaseTest):
    """Test suite for Container class."""

    def test_resolving_callbacks_are_called_for_concretes_when_attached_on_interface(self):
        """Test that resolving callbacks are called for concretes when attached on interface."""
        container = self.container
        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingImplementationStub, increment_counter)
        container.bind(ResolvingContractStub, ResolvingImplementationStub)
        container.make(ResolvingContractStub)
        assert call_counter == 1
        container.make(ResolvingImplementationStub)
        assert call_counter == 2

    def test_resolving_callbacks_are_called_for_concretes_when_attached_on_concretes(self):
        """Test that resolving callbacks are called for concretes when attached on concretes."""
        container = self.container
        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingImplementationStub, increment_counter)
        container.bind(ResolvingContractStub, ResolvingImplementationStub)
        container.make(ResolvingContractStub)
        assert call_counter == 1
        container.make(ResolvingImplementationStub)
        assert call_counter == 2

    def test_after_resolving_callbacks_are_called_once_for_implementation(self):
        """Test that after resolving callbacks are called once for implementation."""
        container = self.container
        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.after_resolving(ResolvingContractStub, increment_counter)
        container.bind(ResolvingContractStub, ResolvingImplementationStub)
        container.make(ResolvingContractStub)
        assert call_counter == 1
        container.make(ResolvingContractStub)
        assert call_counter == 2

    def test_before_resolving_callbacks_are_called(self):
        """Test that specific before resolving callbacks are called."""
        # Given a call counter initialized to zero.
        container = self.container
        call_counter = 0

        # And a contract/implementation stub binding.
        container.bind(ResolvingContractStub, ResolvingImplementationStub)

        # When we add a before resolving callback that increment the counter by one.
        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.before_resolving(ResolvingContractStub, increment_counter)

        # Then resolving the implementation stub increases the counter by one.
        container.make(ResolvingContractStub)
        assert call_counter == 1

        # And resolving the contract stub increases the counter by one.
        container.make(ResolvingContractStub)
        assert call_counter == 2

    def test_global_before_resolving_callbacks_are_called(self):
        """Test global before resolving callbacks are called."""
        # Given a call counter initialized to zero.
        container = self.container
        call_counter = 0

        # When we add a global before resolving callback that increment that counter by one.
        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.before_resolving(increment_counter)

        # Then resolving anything increases the counter by one.
        container.make(ResolvingImplementationStub)
        assert call_counter == 1

    def test_resolving_callbacks_are_called_for_concretes_with_no_binding(self):
        """Test that resolving callbacks are called for concretes with no binding."""
        container = self.container
        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingImplementationStub, increment_counter)
        container.make(ResolvingImplementationStub)
        assert call_counter == 1
        container.make(ResolvingImplementationStub)
        assert call_counter == 2

    def test_resolving_callbacks_are_called_for_interfaces_with_no_binding(self):
        """Test that resolving callbacks are called for interfaces with no binding."""
        container = self.container
        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingContractStub, increment_counter)
        container.make(ResolvingImplementationStub)
        assert call_counter == 1
        container.make(ResolvingImplementationStub)
        assert call_counter == 2

    def test_rebinding_does_not_affect_multiple_resolving_callbacks(self):
        """Test that rebinding does not affect multiple resolving callbacks."""
        container = self.container
        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingContractStub, increment_counter)
        container.resolving(ResolvingImplementationStubTwo, increment_counter)
        container.bind(ResolvingContractStub, ResolvingImplementationStub)
        # it should call the callback for interface
        container.make(ResolvingContractStub)
        assert call_counter == 1
        # it should call the callback for interface
        container.make(ResolvingImplementationStub)
        assert call_counter == 2
        # should call the callback for the interface it implements
        # plus the callback for ResolvingImplementationStubTwo.
        container.make(ResolvingImplementationStubTwo)
        assert call_counter == 4

    def test_resolving_callbacks_arent_called_when_no_rebindings_are_registered(self):
        """Test that resolving callbacks aren't called when no rebindings are registered."""
        container = self.container
        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingContractStub, increment_counter)
        container.bind(ResolvingContractStub, ResolvingImplementationStub)

        container.make(ResolvingContractStub)
        assert call_counter == 1

        container.bind(ResolvingContractStub, ResolvingImplementationStubTwo)
        assert call_counter == 1

        container.make(ResolvingImplementationStubTwo)
        assert call_counter == 2

        container.bind(ResolvingContractStub, lambda: ResolvingImplementationStubTwo())
        assert call_counter == 2

        container.make(ResolvingContractStub)
        assert call_counter == 3

    def test_resolving_callbacks_are_called_when_rebind_happens(self):
        """Test that resolving callbacks are called when rebind happens."""
        container = self.container

        resolving_call_counter = 0

        def increment_resolving_counter(*args, **kwargs):
            nonlocal resolving_call_counter
            resolving_call_counter += 1

        container.resolving(ResolvingContractStub, increment_resolving_counter)

        rebind_call_counter = 0

        def increment_rebind_counter(*args, **kwargs):
            nonlocal rebind_call_counter
            rebind_call_counter += 1

        container.rebinding(ResolvingContractStub, increment_rebind_counter)

        container.bind(ResolvingContractStub, ResolvingImplementationStub)

        container.make(ResolvingContractStub)
        assert resolving_call_counter == 1
        assert rebind_call_counter == 0

        container.bind(ResolvingContractStub, ResolvingImplementationStubTwo)
        assert resolving_call_counter == 2
        assert rebind_call_counter == 1

        container.make(ResolvingImplementationStubTwo)
        assert resolving_call_counter == 3
        assert rebind_call_counter == 1

        container.bind(ResolvingContractStub, lambda: ResolvingImplementationStubTwo())
        assert resolving_call_counter == 4
        assert rebind_call_counter == 2

        container.make(ResolvingContractStub)
        assert resolving_call_counter == 5
        assert rebind_call_counter == 2

    def test_parameters_passed_into_resolving_callbacks(self):
        """Test that parameters are passed into resolving callbacks."""
        container = self.container

        def resolving_callback(obj, app):
            assert isinstance(obj, ResolvingContractStub)
            assert isinstance(obj, ResolvingImplementationStubTwo)
            assert app is container

        container.resolving(ResolvingContractStub, resolving_callback)

        def after_resolving_callback(obj, app):
            assert isinstance(obj, ResolvingContractStub)
            assert isinstance(obj, ResolvingImplementationStubTwo)
            assert app is container

        container.after_resolving(ResolvingContractStub, after_resolving_callback)

        def global_after_resolving_callback(obj, app):
            assert isinstance(obj, ResolvingContractStub)
            assert isinstance(obj, ResolvingImplementationStubTwo)
            assert app is container

        container.after_resolving(global_after_resolving_callback)

        container.bind(ResolvingContractStub, ResolvingImplementationStubTwo)
        container.make(ResolvingContractStub)

    def test_rebinding_does_not_affect_resolving_callbacks(self):
        """Test that rebinding does not affect resolving callbacks."""
        container = self.container

        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingContractStub, increment_counter)

        container.bind(ResolvingContractStub, ResolvingImplementationStub)
        container.bind(ResolvingContractStub, lambda: ResolvingImplementationStub())

        container.make(ResolvingContractStub)
        assert call_counter == 1

        container.make(ResolvingImplementationStub)
        assert call_counter == 2

        container.make(ResolvingImplementationStub)
        assert call_counter == 3

        container.make(ResolvingContractStub)
        assert call_counter == 4

    def test_resolving_callbacks_are_called_once_for_implementation_2(self):
        """Test that resolving callbacks are called once for implementation."""
        container = self.container

        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingContractStub, increment_counter)

        container.bind(ResolvingContractStub, lambda: ResolvingImplementationStub())

        container.make(ResolvingContractStub)
        assert call_counter == 1

        container.make(ResolvingImplementationStub)
        assert call_counter == 2

        container.make(ResolvingImplementationStub)
        assert call_counter == 3

        container.make(ResolvingContractStub)
        assert call_counter == 4

    def test_resolving_callbacks_for_concretes_are_called_once_for_string_abstractions(self):
        """Test that resolving callbacks for concretes are called once for string abstractions."""
        container = self.container

        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingImplementationStub, increment_counter)

        container.bind("foo", ResolvingImplementationStub)
        container.bind("bar", ResolvingImplementationStub)
        container.bind(ResolvingContractStub, ResolvingImplementationStub)

        container.make(ResolvingImplementationStub)
        assert call_counter == 1

        container.make("foo")
        assert call_counter == 2

        container.make("bar")
        assert call_counter == 3

        container.make(ResolvingContractStub)
        assert call_counter == 4

    def test_resolving_callbacks_are_called_once_for_string_abstractions(self):
        """Test that resolving callbacks are called once for string abstractions."""
        container = self.container

        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving("foo", increment_counter)

        container.bind("foo", ResolvingImplementationStub)

        container.make("foo")
        assert call_counter == 1

        container.make("foo")
        assert call_counter == 2

    def test_resolving_callbacks_are_canceled_when_interface_gets_bound_to_some_other_concrete(self):
        """Test that resolving callbacks are canceled when interface gets bound to some other concrete."""
        container = self.container

        container.bind(ResolvingContractStub, ResolvingImplementationStub)

        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingImplementationStub, increment_counter)

        container.make(ResolvingContractStub)
        assert call_counter == 1

        container.bind(ResolvingContractStub, ResolvingImplementationStubTwo)
        container.make(ResolvingContractStub)
        assert call_counter == 1

    def test_resolving_callbacks_can_still_be_added_after_the_first_resolution(self):
        """Test that resolving callbacks can still be added after the first resolution."""
        container = self.container

        container.bind(ResolvingContractStub, ResolvingImplementationStub)

        container.make(ResolvingImplementationStub)

        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingContractStub, increment_counter)

        container.make(ResolvingImplementationStub)
        assert call_counter == 1

    def test_global_resolving_callbacks_are_called_once_for_implementation(self):
        """Test that global resolving callbacks are called once for implementation."""
        container = self.container

        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(increment_counter)

        container.bind(ResolvingContractStub, ResolvingImplementationStub)

        container.make(ResolvingImplementationStub)
        assert call_counter == 1

        container.make(ResolvingContractStub)
        assert call_counter == 2

    def test_resolving_callbacks_are_called_once_for_implementation(self):
        """Test that resolving callbacks are called once for implementation."""
        container = self.container

        call_counter = 0

        def increment_counter(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1

        container.resolving(ResolvingContractStub, increment_counter)

        container.bind(ResolvingContractStub, ResolvingImplementationStub)

        container.make(ResolvingImplementationStub)
        assert call_counter == 1

        container.make(ResolvingImplementationStub)
        assert call_counter == 2

    def test_resolving_callbacks_are_called_for_specific_abstracts(self):
        """Test that resolving callbacks are called for specific abstracts."""
        container = self.container

        def set_name(obj, app):
            obj.name = "Fork"

        container.resolving("foo", set_name)

        def factory(app):
            class SimpleObject:
                pass

            return SimpleObject()

        container.bind("foo", factory)
        instance = container.make("foo")

        assert instance.name == "Fork"

    def test_resolving_callbacks_are_called(self):
        """Test that resolving callbacks are called."""
        container = self.container

        def set_name(obj, app):
            obj.name = "Fork"

        container.resolving(set_name)

        def factory(app):
            class SimpleObject:
                pass

            return SimpleObject()

        container.bind("foo", factory)
        instance = container.make("foo")

        assert instance.name == "Fork"

    def test_resolving_callbacks_are_called_for_type(self):
        """Test that resolving callbacks are called for type."""
        container = self.container

        class SimpleObject:
            pass

        def set_name(obj, app):
            obj.name = "Fork"

        container.resolving(SimpleObject, set_name)

        def factory(app):
            return SimpleObject()

        container.bind("foo", factory)
        instance = container.make("foo")

        assert instance.name == "Fork"

    def test_resolving_callbacks_should_be_fired_when_called_with_aliases(self):
        """Test that resolving callbacks should be fired when called with aliases."""
        container = self.container

        class SimpleObject:
            pass

        container.bind(SimpleObject, lambda app: SimpleObject())
        container.alias(SimpleObject, "std")

        def set_name(obj, app):
            obj.name = "Fork"

        container.resolving("std", set_name)

        def factory(app):
            return SimpleObject()

        container.bind("foo", factory)
        instance = container.make("foo")

        assert instance.name == "Fork"
