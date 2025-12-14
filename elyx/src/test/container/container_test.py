from test.base_test import BaseTest


class ContainerConcreteStub:
    pass


class IContainerContractStub:
    pass


class ContainerImplementationStub(IContainerContractStub):
    pass


class ContainerImplementationStubTwo(IContainerContractStub):
    pass


class ContainerDependentStub:
    def __init__(self, impl: IContainerContractStub):
        self.impl = impl


class ContainerNestedDependentStub:
    def __init__(self, inner: ContainerDependentStub):
        self.inner = inner


class TestContainer(BaseTest):
    """Test suite for Container class."""

    def test_container_singleton(self):
        """Test that Container singleton pattern works correctly."""
        from elyx.container.container import Container

        # Set a container instance as singleton
        container = Container.set_instance(Container())
        assert container is Container.get_instance()

        # Clear the singleton
        Container.set_instance(None)
        container2 = Container.get_instance()

        # New instance should be created and be different from first
        assert isinstance(container2, Container)
        assert container is not container2

    def test_closure_resolution(self):
        """Test that container can resolve closures bound to names."""
        from elyx.container.container import Container

        container = Container()
        container.bind("name", lambda: "use_the_fork")
        assert container.make("name") == "use_the_fork"

    def test_abstract_can_be_bound_from_concrete_return_type(self):
        """Test that abstract types can be bound from callable return type hints."""
        from elyx.container.container import Container

        container = Container()

        def factory() -> IContainerContractStub | ContainerImplementationStub:
            return ContainerImplementationStub()

        def singleton_factory() -> ContainerConcreteStub:
            return ContainerConcreteStub()

        container.bind(factory)
        container.singleton(singleton_factory)

        assert isinstance(container.make(IContainerContractStub), IContainerContractStub)
        assert container.is_shared(ContainerConcreteStub)

    def test_bind_if_doesnt_register_if_service_already_registered(self):
        """Test that bind_if doesn't register if service is already registered."""
        from elyx.container.container import Container

        container = Container()
        container.bind("name", lambda: "use_the_fork")
        container.bind_if("name", lambda: "use_the_not_fork")
        assert container.make("name") == "use_the_fork"

    def test_bind_if_does_register_if_service_not_registered_yet(self):
        """Test that bind_if does register if service is not registered yet."""
        from elyx.container.container import Container

        container = Container()
        container.bind("surname", lambda: "use_the_fork")
        container.bind_if("name", lambda: "use_the_not_fork")
        assert container.make("name") == "use_the_not_fork"

    def test_singleton_if_doesnt_register_if_binding_already_registered(self):
        """Test singleton_if doesn't register if binding already registered."""
        from elyx.container.container import Container

        container = Container()
        container.singleton("class", lambda: object())
        first_instantiation = container.make("class")
        container.singleton_if("class", lambda: ContainerConcreteStub())
        second_instantiation = container.make("class")
        assert first_instantiation is second_instantiation

    def test_singleton_if_does_register_if_binding_not_registered_yet(self):
        """Test singleton_if does register if binding not registered yet."""
        from elyx.container.container import Container

        container = Container()
        container.singleton("class", lambda: object())
        container.singleton_if("otherClass", lambda: ContainerConcreteStub())
        first_instantiation = container.make("otherClass")
        second_instantiation = container.make("otherClass")
        assert first_instantiation is second_instantiation

    def test_shared_closure_resolution(self):
        """Test that shared closures are resolved as singletons."""
        from elyx.container.container import Container

        container = Container()
        container.singleton("class", lambda: object())
        first_instantiation = container.make("class")
        second_instantiation = container.make("class")
        assert first_instantiation is second_instantiation

    def test_auto_concrete_resolution(self):
        """Test that the container can auto-resolve concrete classes."""
        from elyx.container.container import Container

        container = Container()
        instance = container.make(ContainerConcreteStub)
        assert isinstance(instance, ContainerConcreteStub)

    def test_shared_concrete_resolution(self):
        """Test that concrete classes registered as singletons are shared."""
        from elyx.container.container import Container

        container = Container()
        container.singleton(ContainerConcreteStub)
        var1 = container.make(ContainerConcreteStub)
        var2 = container.make(ContainerConcreteStub)
        assert var1 is var2

    def test_abstract_to_concrete_resolution(self):
        """Test that the container can resolve dependencies via constructor."""
        from elyx.container.container import Container

        container = Container()
        container.bind(IContainerContractStub, ContainerImplementationStub)
        instance = container.make(ContainerDependentStub)
        assert isinstance(instance.impl, ContainerImplementationStub)

    def test_nested_dependency_resolution(self):
        """Test that the container can resolve nested dependencies."""
        from elyx.container.container import Container

        container = Container()
        container.bind(IContainerContractStub, ContainerImplementationStub)
        instance = container.make(ContainerNestedDependentStub)
        assert isinstance(instance.inner, ContainerDependentStub)
        assert isinstance(instance.inner.impl, ContainerImplementationStub)


    def test_container_is_passed_to_resolvers(self):
        """Test that the container instance is passed to factory closures."""
        from elyx.container.container import Container

        container = Container()
        container.bind("something", lambda c: c)
        c = container.make("something")
        assert c is container
