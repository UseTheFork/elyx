from typing import Optional

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


class ContainerDefaultValueStub:
    def __init__(self, stub: ContainerConcreteStub, default: str = "use_the_fork"):
        self.stub = stub
        self.default = default


class ContainerClassWithDefaultValueStub:
    def __init__(self, no_default: ContainerConcreteStub, default: Optional[ContainerConcreteStub] = None):
        self.no_default = no_default
        self.default = default


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

    def test_array_access(self):
        """Test that the container can be used with array access syntax."""
        from elyx.container.container import Container

        container = Container()
        assert "something" not in container

        container["something"] = lambda: "foo"
        assert "something" in container
        assert container["something"] == "foo"

        del container["something"]
        assert "something" not in container

        # Test offsetSet when it's not a Closure
        container["something"] = "text"
        assert "something" in container
        assert container["something"] == "text"

        del container["something"]
        assert "something" not in container

    def test_aliases(self):
        """Test that aliases can be chained and resolved."""
        from elyx.container.container import Container

        container = Container()
        container["foo"] = "bar"
        container.alias("foo", "baz")
        container.alias("baz", "bat")
        assert container.make("foo") == "bar"
        assert container.make("baz") == "bar"
        assert container.make("bat") == "bar"

    def test_aliases_with_parameters(self):
        """Test that parameters are passed through aliases to the factory."""
        from elyx.container.container import Container

        container = Container()
        container.bind("foo", lambda app, config: config)
        container.alias("foo", "baz")
        assert container.make("baz", config=[1, 2, 3]) == [1, 2, 3]

    def test_bindings_can_be_overridden(self):
        """Test that bindings can be overridden."""
        from elyx.container.container import Container

        container = Container()
        container["foo"] = "bar"
        container["foo"] = "baz"
        assert container["foo"] == "baz"

    def test_binding_an_instance_returns_the_instance(self):
        """Test that binding an instance returns the instance."""
        from elyx.container.container import Container

        container = Container()
        bound = object()
        resolved = container.instance("foo", bound)
        assert bound is resolved

    def test_binding_an_instance_as_shared(self):
        """Test that an instance binding is shared."""
        from elyx.container.container import Container

        container = Container()
        bound = object()
        container.instance("foo", bound)
        resolved = container.make("foo")
        assert bound is resolved

    def test_resolution_of_default_parameters(self):
        """Test that the container correctly resolves dependencies with default parameters."""
        from elyx.container.container import Container

        container = Container()
        instance = container.make(ContainerDefaultValueStub)
        assert isinstance(instance.stub, ContainerConcreteStub)
        assert instance.default == "use_the_fork"

    def test_resolution_of_class_with_default_parameters(self):
        """Test resolution of class dependencies with default null values."""
        from elyx.container.container import Container

        container = Container()
        instance = container.make(ContainerClassWithDefaultValueStub)
        assert isinstance(instance.no_default, ContainerConcreteStub)
        assert instance.default is None

        container.bind(ContainerConcreteStub, lambda: ContainerConcreteStub())
        instance = container.make(ContainerClassWithDefaultValueStub)
        assert isinstance(instance.default, ContainerConcreteStub)

    def test_bound(self):
        """Test the bound method."""
        from elyx.container.container import Container

        container = Container()
        container.bind(ContainerConcreteStub, lambda: ContainerConcreteStub())
        assert container.bound(ContainerConcreteStub) is True
        assert container.bound(IContainerContractStub) is False

        container = Container()
        container.bind(IContainerContractStub, ContainerConcreteStub)
        assert container.bound(IContainerContractStub) is True
        assert container.bound(ContainerConcreteStub) is False

    def test_unset_removes_bound_instances(self):
        """Test that del removes bound instances."""
        from elyx.container.container import Container

        container = Container()
        container.instance("object", object())
        del container["object"]
        assert container.bound("object") is False

    def test_bound_instance_and_alias_check_via_array_access(self):
        """Test that bound checks work for instances and aliases via array access."""
        from elyx.container.container import Container

        container = Container()
        container.instance("object", object())
        container.alias("object", "alias")
        assert "object" in container
        assert "alias" in container

    # public function testInternalClassWithDefaultParameters()
    # {
    #     $this->expectException(BindingResolutionException::class);
    #     $this->expectExceptionMessage('Unresolvable dependency resolving [Parameter #0 [ <required> $first ]] in class Illuminate\Tests\Container\ContainerMixedPrimitiveStub');
    #     $container = new Container;
    #     $container->make(ContainerMixedPrimitiveStub::class, []);
    # }


# class ContainerMixedPrimitiveStub
# {
#     public $first;
#     public $last;
#     public $stub;
#     public function __construct($first, ContainerConcreteStub $stub, $last)
#     {
#         $this->stub = $stub;
#         $this->last = $last;
#         $this->first = $first;
#     }
# }
