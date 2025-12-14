from test.base_test import BaseTest


class ContainerConcreteStub:
    pass


class IContainerContractStub:
    pass


class ContainerImplementationStub(IContainerContractStub):
    pass


class ContainerImplementationStubTwo(IContainerContractStub):
    pass


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
