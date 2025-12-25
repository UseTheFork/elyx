import pytest
from elyx.collections import Collection
from elyx.config.repository import Repository
from test.base_test import BaseTest


class TestRepository(BaseTest):
    """Test suite for Repository class."""

    @pytest.fixture(autouse=True)
    def setup_repository(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "foo": "bar",
            "bar": "baz",
            "baz": "bat",
            "null": None,
            "boolean": True,
            "integer": 1,
            "float": 1.1,
            "associate": {
                "x": "xxx",
                "y": "yyy",
            },
            "array": [
                "aaa",
                "zzz",
            ],
            "x": {
                "z": "zoo",
            },
            "a.b": "c",
            "a": {
                "b.c": "d",
            },
        }
        self.repository = Repository(self.config)
        return

    def test_get_value_when_key_contain_dot(self):
        """Test that get() correctly handles keys containing dots."""
        assert self.repository.get("a.b") == "c"
        assert self.repository.get("a.b.c") is None
        assert self.repository.get("x.y.z") is None
        assert self.repository.get(".") is None

    def test_get_boolean_value(self):
        """Test that get() correctly retrieves boolean values."""
        assert self.repository.get("boolean") is True

    def test_get_null_value(self):
        """Test that get() correctly retrieves null values."""
        assert self.repository.get("null") is None

    def test_construct(self):
        """Test that Repository is properly instantiated."""
        assert isinstance(self.repository, Repository)

    def test_has_is_true(self):
        """Test that has() returns True for existing keys."""
        assert self.repository.has("foo") is True

    def test_has_is_false(self):
        """Test that has() returns False for non-existing keys."""
        assert self.repository.has("not-exist") is False

    def test_get(self):
        """Test that get() retrieves the correct value."""
        assert self.repository.get("foo") == "bar"

    def test_get_with_array_of_keys(self):
        """Test that get() can retrieve multiple values with an array of keys."""
        assert self.repository.get(["foo", "bar", "none"]) == {
            "foo": "bar",
            "bar": "baz",
            "none": None,
        }

        assert self.repository.get({"x.y": "default", "x.z": "default", "bar": "default", "baz": None}) == {
            "x.y": "default",
            "x.z": "zoo",
            "bar": "baz",
            "baz": "bat",
        }

    def test_get_with_default(self):
        """Test that get() returns default value for non-existing keys."""
        assert self.repository.get("not-exist", "default") == "default"

    def test_set(self):
        """Test that set() can add a single key-value pair."""
        self.repository.add("key", "value")
        assert self.repository.get("key") == "value"

    def test_set_array(self):
        """Test that set() can add multiple key-value pairs from a dict."""
        self.repository.merge(
            {
                "key1": "value1",
                "key2": "value2",
                "key3": None,
                "key4": {
                    "foo": "bar",
                    "bar": {
                        "foo": "bar",
                    },
                },
            }
        )
        assert self.repository.get("key1") == "value1"
        assert self.repository.get("key2") == "value2"
        assert self.repository.get("key3") is None
        assert self.repository.get("key4.foo") == "bar"
        assert self.repository.get("key4.bar.foo") == "bar"
        assert self.repository.get("key5") is None

    def test_prepend(self):
        """Test that prepend() adds a value to the beginning of an array."""
        assert self.repository.get("array.0") == "aaa"
        assert self.repository.get("array.1") == "zzz"

        self.repository.prepend("array", "xxx")
        assert self.repository.get("array.0") == "xxx"
        assert self.repository.get("array.1") == "aaa"
        assert self.repository.get("array.2") == "zzz"
        assert self.repository.get("array.3") is None
        assert len(self.repository.get("array")) == 3

    def test_push(self):
        """Test that push() adds a value to the end of an array."""
        assert self.repository.get("array.0") == "aaa"
        assert self.repository.get("array.1") == "zzz"
        self.repository.push("array", "xxx")
        assert self.repository.get("array.0") == "aaa"
        assert self.repository.get("array.1") == "zzz"
        assert self.repository.get("array.2") == "xxx"

        assert len(self.repository.get("array")) == 3

    def test_prepend_with_new_key(self):
        """Test that prepend() creates a new array when key doesn't exist."""
        self.repository.prepend("new_key", "xxx")
        assert self.repository.get("new_key") == ["xxx"]

    def test_push_with_new_key(self):
        """Test that push() creates a new array when key doesn't exist."""
        self.repository.push("new_key", "xxx")
        assert self.repository.get("new_key") == ["xxx"]

    def test_it_gets_as_string(self):
        """Test that string() retrieves a string value."""
        assert self.repository.string("a.b") == "c"

    def test_it_throws_an_exception_when_trying_to_get_non_string_value_as_string(self):
        """Test that string() throws an exception for non-string values."""
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            self.repository.string("a")

        assert "Configuration value for key [a] must be a string" in str(exc_info.value)

    def test_it_gets_as_array(self):
        """Test that array() retrieves an array value."""
        assert self.repository.array("array") == ["aaa", "zzz"]

    def test_it_throws_an_exception_when_trying_to_get_non_array_value_as_array(self):
        """Test that array() throws an exception for non-array values."""
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            self.repository.array("a.b")

        assert "Configuration value for key [a.b] must be an array" in str(exc_info.value)

    def test_it_gets_as_collection(self):
        """Test that collection() retrieves an array value as a Collection."""
        collection = self.repository.collection("array")

        assert isinstance(collection, Collection)
        assert collection.to_array() == {0: "aaa", 1: "zzz"}

    def test_it_gets_as_boolean(self):
        """Test that boolean() retrieves a boolean value."""
        assert self.repository.boolean("boolean") is True

    def test_it_throws_an_exception_when_trying_to_get_non_boolean_value_as_boolean(self):
        """Test that boolean() throws an exception for non-boolean values."""
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            self.repository.boolean("a.b")

        assert "Configuration value for key [a.b] must be a boolean" in str(exc_info.value)

    def test_it_gets_as_integer(self):
        """Test that integer() retrieves an integer value."""
        assert self.repository.integer("integer") == 1

    def test_it_throws_an_exception_when_trying_to_get_non_integer_value_as_integer(self):
        """Test that integer() throws an exception for non-integer values."""
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            self.repository.integer("a.b")

        assert "Configuration value for key [a.b] must be an integer" in str(exc_info.value)

    def test_it_gets_as_float(self):
        """Test that float() retrieves a float value."""
        assert self.repository.float("float") == 1.1

    def test_it_throws_an_exception_when_trying_to_get_non_float_value_as_float(self):
        """Test that float() throws an exception for non-float values."""
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            self.repository.float("a.b")

        assert "Configuration value for key [a.b] must be a float" in str(exc_info.value)
