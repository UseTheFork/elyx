# Elyx Testing Patterns Convention

## Key Principles

- **pytest framework**: All tests use pytest with class-based organization
- **BaseTest inheritance**: Test classes inherit from `BaseTest` for shared fixtures
- **Descriptive docstrings**: Every test method has a one-line docstring explaining what it tests
- **Async when needed**: Use `async def` for tests that involve async operations (events, dispatchers)

## Test Structure

**Class-based organization:**

```python
class TestContainer(BaseTest):
    """Test suite for Container class."""
    
    def test_closure_resolution(self):
        """Test that container can resolve closures bound to names."""
        container = Container()
        container.bind("name", lambda: "use_the_fork")
        assert container.make("name") == "use_the_fork"
```

**Async tests:** Use `async def` for event dispatchers and async operations

## Fixtures

**BaseTest provides container with auto-cleanup:**

```python
class BaseTest:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.container = Container()
        yield
        self.container.flush()
```

**Additional fixtures:** Use `@pytest.fixture(autouse=True)` for test-specific setup

## Test Naming

**Pattern: `test_<what_is_being_tested>`**

- `test_container_singleton` - Tests singleton behavior
- `test_bind_if_doesnt_register_if_service_already_registered` - Descriptive for complex scenarios
- `test_exception_on_uninstantiable_abstract` - Tests exception cases

## Stubs & Assertions

**Define test stubs at module level:**

```python
class ContainerConcreteStub:
    pass

class IContainerContractStub(ABC):
    @abstractmethod
    def get_value(self):
        pass
```

**Direct assertions:**

```python
assert isinstance(instance, ContainerConcreteStub)
assert var1 is var2  # Identity checks for singletons
```

**Exception testing:**

```python
with pytest.raises(EntryNotFoundException) as exc_info:
    container.make("NonExistent")
assert "Entry not found" in str(exc_info.value)
```

## State Tracking

**Use dicts/lists for test state:**

```python
test_storage = {}
def listener(value):
    test_storage["event_result"] = value
```

**Counters for callbacks:**

```python
call_counter = 0
def increment_counter(*args):
    nonlocal call_counter
    call_counter += 1
```

## Things to Avoid

- ❌ Tests without docstrings
- ❌ Generic names like `test_1`
- ❌ Shared mutable state between tests