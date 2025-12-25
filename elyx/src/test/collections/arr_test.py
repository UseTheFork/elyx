from datetime import datetime

from elyx.collections.arr import Arr
from elyx.collections.collection import Collection
from test.base_test import BaseTest


class TestArr(BaseTest):
    """Test suite for Arr helper utilities."""

    def test_accessible(self):
        """Test that accessible correctly identifies array-accessible values."""
        assert Arr.accessible([]) is True
        assert Arr.accessible([1, 2]) is True
        assert Arr.accessible({"a": 1, "b": 2}) is True
        assert Arr.accessible(Collection()) is True

        assert Arr.accessible(None) is False
        assert Arr.accessible("abc") is False
        assert Arr.accessible(object()) is False
        assert Arr.accessible(123) is False
        assert Arr.accessible(12.34) is False
        assert Arr.accessible(True) is False
        assert Arr.accessible(datetime.now()) is False
        assert Arr.accessible(lambda: None) is False

    def test_exists(self):
        """Test that exists correctly identifies existing keys in arrays and dicts."""
        assert Arr.exists([1], 0) is True
        assert Arr.exists([None], 0) is True
        assert Arr.exists({"a": 1}, "a") is True
        assert Arr.exists({"a": None}, "a") is True
        assert Arr.exists(Collection({"a": None}), "a") is True

        assert Arr.exists([1], 1) is False
        assert Arr.exists([None], 1) is False
        assert Arr.exists({"a": 1}, 0) is False
        assert Arr.exists(Collection({"a": None}), "b") is False

    def test_has(self):
        """Test that has correctly identifies keys using dot notation."""
        array = {"products.desk": {"price": 100}}
        assert Arr.has(array, "products.desk") is True

        array = {"products": {"desk": {"price": 100}}}
        assert Arr.has(array, "products.desk") is True
        assert Arr.has(array, "products.desk.price") is True
        assert Arr.has(array, "products.foo") is False
        assert Arr.has(array, "products.desk.foo") is False

        array = {"foo": None, "bar": {"baz": None}}
        assert Arr.has(array, "foo") is True
        assert Arr.has(array, "bar.baz") is True

        array = Collection({"foo": 10, "bar": Collection({"baz": 10})})
        assert Arr.has(array, "foo") is True
        assert Arr.has(array, "bar") is True
        assert Arr.has(array, "bar.baz") is True
        assert Arr.has(array, "xxx") is False
        assert Arr.has(array, "xxx.yyy") is False
        assert Arr.has(array, "foo.xxx") is False
        assert Arr.has(array, "bar.xxx") is False

        array = Collection({"foo": None, "bar": Collection({"baz": None})})
        assert Arr.has(array, "foo") is True
        assert Arr.has(array, "bar.baz") is True

        array = ["foo", "bar"]
        assert Arr.has(array, None) is False

        assert Arr.has(None, "foo") is False
        assert Arr.has(False, "foo") is False

        assert Arr.has(None, None) is False
        assert Arr.has([], None) is False

        array = {"products": {"desk": {"price": 100}}}
        assert Arr.has(array, ["products.desk"]) is True
        assert Arr.has(array, ["products.desk", "products.desk.price"]) is True
        assert Arr.has(array, ["products", "products"]) is True
        assert Arr.has(array, ["foo"]) is False
        assert Arr.has(array, []) is False
        assert Arr.has(array, ["products.desk", "products.price"]) is False

        array = {"products": [{"name": "desk"}]}
        assert Arr.has(array, "products.0.name") is True
        assert Arr.has(array, "products.0.price") is False

        assert Arr.has([], [None]) is False
        assert Arr.has(None, [None]) is False

        assert Arr.has({"": "some"}, "") is True
        assert Arr.has({"": "some"}, [""]) is True
        assert Arr.has([""], "") is False
        assert Arr.has([], "") is False
        assert Arr.has([], [""]) is False

    def test_get(self):
        """Test that get correctly retrieves values using dot notation."""
        array = {"products.desk": {"price": 100}}
        assert Arr.get(array, "products.desk") == {"price": 100}

        array = {"products": {"desk": {"price": 100}}}
        value = Arr.get(array, "products.desk")
        assert value == {"price": 100}

        # Test null array values
        array = {"foo": None, "bar": {"baz": None}}
        assert Arr.get(array, "foo", "default") is None
        assert Arr.get(array, "bar.baz", "default") is None

        # Test direct Collection object
        array = {"products": {"desk": {"price": 100}}}
        collection_object = Collection(array)
        value = Arr.get(collection_object, "products.desk")
        assert value == {"price": 100}

        # Test array containing Collection object
        collection_child = Collection({"products": {"desk": {"price": 100}}})
        array = {"child": collection_child}
        value = Arr.get(array, "child.products.desk")
        assert value == {"price": 100}

        # Test array containing multiple nested Collection objects
        collection_child = Collection({"products": {"desk": {"price": 100}}})
        collection_parent = Collection({"child": collection_child})
        array = {"parent": collection_parent}
        value = Arr.get(array, "parent.child.products.desk")
        assert value == {"price": 100}

        # Test missing Collection object field
        collection_child = Collection({"products": {"desk": {"price": 100}}})
        collection_parent = Collection({"child": collection_child})
        array = {"parent": collection_parent}
        value = Arr.get(array, "parent.child.desk")
        assert value is None

        # Test missing Collection object field
        collection_object = Collection({"products": {"desk": None}})
        array = {"parent": collection_object}
        value = Arr.get(array, "parent.products.desk.price")
        assert value is None

        # Test null Collection object fields
        array = Collection({"foo": None, "bar": Collection({"baz": None})})
        assert Arr.get(array, "foo", "default") is None
        assert Arr.get(array, "bar.baz", "default") is None

        # Test null key returns the whole array
        array = ["foo", "bar"]
        assert Arr.get(array, None) == Arr._normalize_to_dict(array)

        # Test array not an array
        assert Arr.get(None, "foo", "default") == "default"
        assert Arr.get(False, "foo", "default") == "default"

        # Test array not an array and key is null
        assert Arr.get(None, None, "default") == "default"

        # Test array is empty and key is null
        assert Arr.get([], None) == {}
        assert Arr.get([], None, "default") == {}

        # Test numeric keys
        array = {
            "products": [
                {"name": "desk"},
                {"name": "chair"},
            ],
        }
        assert Arr.get(array, "products.0.name") == "desk"
        assert Arr.get(array, "products.1.name") == "chair"

        # Test return default value for non-existing key
        array = {"names": {"developer": "taylor"}}
        assert Arr.get(array, "names.otherDeveloper", "dayle") == "dayle"
        assert Arr.get(array, "names.otherDeveloper", lambda: "dayle") == "dayle"

        # Test array has an empty string key
        assert Arr.get({"": "bar"}, "") == "bar"
        assert Arr.get({"": {"": "bar"}}, ".") == "bar"

    def test_wrap(self):
        """Test that wrap correctly wraps values in a list."""
        string = "a"
        array = ["a"]

        class SimpleObject:
            def __init__(self):
                self.value = "a"

        obj = SimpleObject()

        assert Arr.wrap(string) == ["a"]
        assert Arr.wrap(array) == array
        assert Arr.wrap(obj) == [obj]
        assert Arr.wrap(None) == []
        assert Arr.wrap([None]) == [None]
        assert Arr.wrap([None, None]) == [None, None]
        assert Arr.wrap("") == [""]
        assert Arr.wrap([""]) == [""]
        assert Arr.wrap(False) == [False]
        assert Arr.wrap([False]) == [False]
        assert Arr.wrap(0) == [0]

        # Test object identity is preserved
        obj2 = SimpleObject()
        wrapped = Arr.wrap(obj2)
        assert wrapped == [obj2]
        assert wrapped[0] is obj2

    def test_set(self):
        """Test that set correctly sets values using dot notation."""
        array = {"products": {"desk": {"price": 100}}}
        Arr.set(array, "products.desk.price", 200)
        assert array == {"products": {"desk": {"price": 200}}}

        # No key is given
        array = {"products": {"desk": {"price": 100}}}
        array = Arr.set(array, None, {"price": 300})
        assert array == {"price": 300}

        # The key doesn't exist at the depth
        array = {"products": "desk"}
        Arr.set(array, "products.desk.price", 200)
        assert array == {"products": {"desk": {"price": 200}}}

        # No corresponding key exists
        array = {"products": {}}
        result = Arr.set(array, "products.desk.price", 200)
        assert result == {"products": {"desk": {"price": 200}}}

        array = {"products": {"desk": {"price": 100}}}
        Arr.set(array, "table", 500)
        assert array == {"products": {"desk": {"price": 100}}, "table": 500}

        array = {"products": {"desk": {"price": 100}}}
        Arr.set(array, "table.price", 350)
        assert array == {"products": {"desk": {"price": 100}}, "table": {"price": 350}}

        array = {}
        Arr.set(array, "products.desk.price", 200)
        assert array == {"products": {"desk": {"price": 200}}}

        # Override
        array = {"products": "table"}
        Arr.set(array, "products.desk.price", 300)
        assert array == {"products": {"desk": {"price": 300}}}

        array = {1: "test"}
        assert Arr.set(array, 1, "hAz") == {1: "hAz"}
