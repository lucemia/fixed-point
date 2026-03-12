from dataclasses import dataclass

import pytest

from fixedpoint import SerializationError
from fixedpoint._serializer import deserialize_value, serialize_value


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Inner:
    value: int


@dataclass
class Outer:
    name: str
    inner: Inner


class TestSerializeRoundTrip:
    @pytest.mark.parametrize(
        "value",
        [None, True, False, 0, 42, -1, 3.14, "", "hello", "unicode: \u4e16\u754c"],
    )
    def test_primitives(self, value):
        assert deserialize_value(serialize_value(value)) == value

    def test_bytes(self):
        val = b"\x00\x01\xff"
        serialized = serialize_value(val)
        assert "__bytes__" in serialized
        assert deserialize_value(serialized) == val

    def test_list(self):
        val = [1, "two", 3.0, None]
        assert deserialize_value(serialize_value(val)) == val

    def test_nested_list(self):
        val = [[1, 2], [3, [4, 5]]]
        assert deserialize_value(serialize_value(val)) == val

    def test_tuple(self):
        val = (1, "two", 3.0)
        serialized = serialize_value(val)
        assert "__tuple__" in serialized
        assert deserialize_value(serialized) == val

    def test_set(self):
        val = {1, 2, 3}
        serialized = serialize_value(val)
        assert "__set__" in serialized
        assert deserialize_value(serialized) == val

    def test_dict(self):
        val = {"a": 1, "b": [2, 3], "c": {"nested": True}}
        assert deserialize_value(serialize_value(val)) == val

    def test_empty_containers(self):
        for val in [[], (), set(), {}]:
            result = deserialize_value(serialize_value(val))
            assert result == val

    def test_dataclass(self):
        val = Point(1.0, 2.0)
        serialized = serialize_value(val)
        assert "__dataclass__" in serialized
        result = deserialize_value(serialized)
        assert result == val
        assert isinstance(result, Point)

    def test_nested_dataclass(self):
        val = Outer(name="test", inner=Inner(value=42))
        assert deserialize_value(serialize_value(val)) == val

    def test_mixed_nested(self):
        val = {"items": [1, (2, 3)], "data": b"\xff"}
        result = deserialize_value(serialize_value(val))
        assert result == val


class TestSerializeErrors:
    def test_unsupported_type(self):
        with pytest.raises(SerializationError, match="Cannot serialize"):
            serialize_value(lambda: None)

    def test_non_string_dict_key(self):
        with pytest.raises(SerializationError, match="Dict keys must be strings"):
            serialize_value({1: "value"})

    def test_custom_class(self):
        class Foo:
            pass

        with pytest.raises(SerializationError):
            serialize_value(Foo())
