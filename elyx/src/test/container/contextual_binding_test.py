from abc import ABC

from test.base_test import BaseTest


class IContainerContextContractStub(ABC):
    pass


class ContainerContextNonContractStub:
    pass


class ContainerContextImplementationStub(IContainerContextContractStub):
    pass


class ContainerContextImplementationStubTwo(IContainerContextContractStub):
    pass


class ContainerTestContextInjectInstantiations(IContainerContextContractStub):
    instantiations = 0

    def __init__(self):
        self.instantiations = self.instantiations + 1


class ContainerTestContextInjectMethodArgument:
    def method(self, dependency: IContainerContextContractStub):
        return dependency


class ContainerTestContextInjectFromConfigArray:
    def __init__(self, settings: dict):
        self.settings = settings


class ContainerTestContextInjectFromConfigIndividualValues:
    def __init__(self, username, password, alias=None):
        self.username = username
        self.password = password
        self.alias = alias


class ContainerTestContextInjectVariadic:
    def __init__(self, *stubs: IContainerContextContractStub):
        self.stubs = stubs


class ContainerTestContextInjectVariadicAfterNonVariadic:
    def __init__(self, concrete: ContainerContextNonContractStub, *stubs: IContainerContextContractStub):
        self.concrete = concrete
        self.stubs = stubs


class ContainerTestContextWithOptionalInnerDependency:
    def __init__(self, inner: IContainerContextContractStub = None):
        self.inner = inner


class ContainerTestContextInjectTwo:
    def __init__(self, impl: IContainerContextContractStub):
        self.impl = impl


class ContainerTestContextInjectTwoInstances:
    def __init__(
        self,
        implOne: ContainerTestContextWithOptionalInnerDependency,
        implTwo: ContainerTestContextInjectTwo,
    ):
        self.implOne = implOne
        self.implTwo = implTwo


class TestContextualBinding(BaseTest):
    """Test suite for contextual binding."""

    def test_contextual_binding_works_for_method_invocation(self):
        """Test that contextual binding works for method invocation."""
        container = self.container

        container.when(ContainerTestContextInjectMethodArgument).needs(IContainerContextContractStub).give(
            ContainerContextImplementationStub
        )

        obj = ContainerTestContextInjectMethodArgument()

        # Call with instance method
        value_resolved = container.call(obj.method)
        assert isinstance(value_resolved, ContainerContextImplementationStub)

    def test_contextual_binding_gives_values_from_config_array(self):
        """Test that contextual binding can inject config values."""
        from elyx.config import Repository

        container = self.container

        container.singleton(
            "config",
            lambda: Repository(
                {
                    "test": {
                        "username": "elyx_user",
                        "password": "secure_pass_123",
                        "alias": "elyx_framework",
                    }
                }
            ),
        )

        container.when(ContainerTestContextInjectFromConfigArray).needs("settings").give_config("test")

        resolved_instance = container.make(ContainerTestContextInjectFromConfigArray)

        assert resolved_instance.settings["username"] == "elyx_user"
        assert resolved_instance.settings["password"] == "secure_pass_123"
        assert resolved_instance.settings["alias"] == "elyx_framework"

    def test_contextual_binding_gives_values_from_config_with_default(self):
        """Test that contextual binding can inject config values with defaults."""
        from elyx.config import Repository

        container = self.container

        container.singleton(
            "config",
            lambda: Repository(
                {
                    "test": {
                        "password": "secure_pass_123",
                    }
                }
            ),
        )

        container.when(ContainerTestContextInjectFromConfigIndividualValues).needs("username").give_config(
            "test.username", "DEFAULT_USERNAME"
        )

        container.when(ContainerTestContextInjectFromConfigIndividualValues).needs("password").give_config(
            "test.password"
        )

        resolved_instance = container.make(ContainerTestContextInjectFromConfigIndividualValues)

        assert resolved_instance.username == "DEFAULT_USERNAME"
        assert resolved_instance.password == "secure_pass_123"
        assert resolved_instance.alias is None

    def test_contextual_binding_gives_values_from_config_optional_value_set(self):
        """Test that contextual binding can inject config values when optional value is set."""
        from elyx.config import Repository

        container = self.container

        container.singleton(
            "config",
            lambda: Repository(
                {
                    "test": {
                        "username": "elyx_admin",
                        "password": "super_secure_456",
                        "alias": "elyx_core",
                    }
                }
            ),
        )

        container.when(ContainerTestContextInjectFromConfigIndividualValues).needs("username").give_config(
            "test.username"
        )

        container.when(ContainerTestContextInjectFromConfigIndividualValues).needs("password").give_config(
            "test.password"
        )

        container.when(ContainerTestContextInjectFromConfigIndividualValues).needs("alias").give_config("test.alias")

        resolved_instance = container.make(ContainerTestContextInjectFromConfigIndividualValues)

        assert resolved_instance.username == "elyx_admin"
        assert resolved_instance.password == "super_secure_456"
        assert resolved_instance.alias == "elyx_core"

    def test_contextual_binding_gives_values_from_config_optional_value_null(self):
        """Test that contextual binding can inject config values when optional value is null."""
        from elyx.config import Repository

        container = self.container

        container.singleton(
            "config",
            lambda: Repository(
                {
                    "test": {
                        "username": "elyx_admin",
                        "password": "super_secure_456",
                    }
                }
            ),
        )

        container.when(ContainerTestContextInjectFromConfigIndividualValues).needs("username").give_config(
            "test.username"
        )

        container.when(ContainerTestContextInjectFromConfigIndividualValues).needs("password").give_config(
            "test.password"
        )

        resolved_instance = container.make(ContainerTestContextInjectFromConfigIndividualValues)

        assert resolved_instance.username == "elyx_admin"
        assert resolved_instance.password == "super_secure_456"
        assert resolved_instance.alias is None

    def test_contextual_binding_works_for_variadic_dependencies_without_factory(self):
        """Test that contextual binding works for variadic dependencies without factory."""
        container = self.container

        container.when(ContainerTestContextInjectVariadic).needs(IContainerContextContractStub).give(
            [ContainerContextImplementationStub, ContainerContextImplementationStubTwo]
        )

        resolved_instance = container.make(ContainerTestContextInjectVariadic)

        assert len(resolved_instance.stubs) == 2
        assert isinstance(resolved_instance.stubs[0], ContainerContextImplementationStub)
        assert isinstance(resolved_instance.stubs[1], ContainerContextImplementationStubTwo)

    def test_contextual_binding_works_for_variadic_after_non_variadic_dependencies_with_nothing_bound(self):
        """Test that contextual binding works for variadic dependencies after non-variadic with nothing bound."""
        container = self.container

        resolved_instance = container.make(ContainerTestContextInjectVariadicAfterNonVariadic)

        assert len(resolved_instance.stubs) == 0

    def test_contextual_binding_works_for_variadic_after_non_variadic_dependencies(self):
        """Test that contextual binding works for variadic dependencies after non-variadic."""
        container = self.container

        container.when(ContainerTestContextInjectVariadicAfterNonVariadic).needs(IContainerContextContractStub).give(
            lambda c: [
                c.make(ContainerContextImplementationStub),
                c.make(ContainerContextImplementationStubTwo),
            ]
        )

        resolved_instance = container.make(ContainerTestContextInjectVariadicAfterNonVariadic)

        assert len(resolved_instance.stubs) == 2
        assert isinstance(resolved_instance.stubs[0], ContainerContextImplementationStub)
        assert isinstance(resolved_instance.stubs[1], ContainerContextImplementationStubTwo)

    def test_contextual_binding_works_for_variadic_dependencies_with_nothing_bound(self):
        """Test that contextual binding works for variadic dependencies with nothing bound."""
        container = self.container

        resolved_instance = container.make(ContainerTestContextInjectVariadic)

        assert len(resolved_instance.stubs) == 0

    def test_contextual_binding_works_for_variadic_dependencies(self):
        """Test that contextual binding works for variadic dependencies."""
        container = self.container

        container.when(ContainerTestContextInjectVariadic).needs(IContainerContextContractStub).give(
            lambda c: [
                c.make(ContainerContextImplementationStub),
                c.make(ContainerContextImplementationStubTwo),
            ]
        )

        resolved_instance = container.make(ContainerTestContextInjectVariadic)

        assert len(resolved_instance.stubs) == 2
        assert isinstance(resolved_instance.stubs[0], ContainerContextImplementationStub)
        assert isinstance(resolved_instance.stubs[1], ContainerContextImplementationStubTwo)

    def test_contextual_binding_works_for_nested_optional_dependencies(self):
        """Test that contextual binding works for nested optional dependencies."""
        container = self.container

        container.when(ContainerTestContextInjectTwoInstances).needs(ContainerTestContextInjectTwo).give(
            lambda c: ContainerTestContextInjectTwo(ContainerContextImplementationStubTwo())
        )

        resolved_instance = container.make(ContainerTestContextInjectTwoInstances)

        assert isinstance(resolved_instance.implOne, ContainerTestContextWithOptionalInnerDependency)
        assert resolved_instance.implOne.inner is None

        assert isinstance(resolved_instance.implTwo, ContainerTestContextInjectTwo)
        assert isinstance(resolved_instance.implTwo.impl, ContainerContextImplementationStubTwo)

    def test_contextual_binding_works_with_aliased_targets(self):
        """Test that contextual binding works with aliased targets."""
        container = self.container

        container.bind(IContainerContextContractStub, ContainerContextImplementationStub)
        container.alias(IContainerContextContractStub, "interface-stub")

        container.alias(ContainerContextImplementationStub, "stub-1")

        container.when(ContainerTestContextInjectTwo).needs("interface-stub").give("stub-1")
        container.when(ContainerTestContextInjectTwoInstances).needs("interface-stub").give(
            ContainerContextImplementationStubTwo
        )

        one = container.make(ContainerTestContextInjectTwo)
        two = container.make(ContainerTestContextInjectTwoInstances)

        assert isinstance(one.impl, ContainerContextImplementationStub)
        assert isinstance(two.implTwo.impl, ContainerContextImplementationStubTwo)
