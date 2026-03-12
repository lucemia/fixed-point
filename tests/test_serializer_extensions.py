"""Tests for Pydantic and Enum serialization support."""
from __future__ import annotations

import enum

from fixedpoint._serializer import deserialize_value, serialize_value


class Color(enum.Enum):
    """Test enum."""
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Status(enum.IntEnum):
    """Test int enum."""
    PENDING = 1
    ACTIVE = 2
    DONE = 3


def test_serialize_enum():
    """Test enum serialization."""
    result = serialize_value(Color.RED)
    assert result["__enum__"].endswith(".Color")
    assert result["value"] == "red"


def test_serialize_int_enum():
    """Test int enum serialization."""
    result = serialize_value(Status.ACTIVE)
    assert result["__enum__"].endswith(".Status")
    assert result["value"] == 2


def test_deserialize_enum():
    """Test enum deserialization."""
    # Use the actual module path from serialization
    serialized = serialize_value(Color.RED)
    result = deserialize_value(serialized)
    assert result == Color.RED
    assert isinstance(result, Color)


def test_deserialize_int_enum():
    """Test int enum deserialization."""
    # Use the actual module path from serialization
    serialized = serialize_value(Status.ACTIVE)
    result = deserialize_value(serialized)
    assert result == Status.ACTIVE
    assert isinstance(result, Status)


def test_enum_in_tuple():
    """Test enum inside tuple."""
    original = (Color.RED, Status.DONE, "test")
    serialized = serialize_value(original)
    deserialized = deserialize_value(serialized)
    assert deserialized == original


def test_enum_in_list():
    """Test enum inside list."""
    original = [Color.RED, Color.GREEN, Color.BLUE]
    serialized = serialize_value(original)
    deserialized = deserialize_value(serialized)
    assert deserialized == original


# Pydantic tests (optional, only if pydantic is installed)
try:
    from pydantic import BaseModel

    class Person(BaseModel):
        """Test Pydantic model."""
        name: str
        age: int
        email: str | None = None

    class MediaFile(BaseModel):
        """Test Pydantic model with enum."""
        type: Color
        title: str
        size: int

    def test_serialize_pydantic():
        """Test Pydantic model serialization."""
        person = Person(name="Alice", age=30, email="alice@example.com")
        result = serialize_value(person)

        assert result["__pydantic__"].endswith(".Person")
        assert result["data"] == {
            "name": "Alice",
            "age": 30,
            "email": "alice@example.com",
        }

    def test_deserialize_pydantic():
        """Test Pydantic model deserialization."""
        # Use actual serialization for correct module path
        person = Person(name="Bob", age=25, email=None)
        serialized = serialize_value(person)
        result = deserialize_value(serialized)

        assert isinstance(result, Person)
        assert result.name == "Bob"
        assert result.age == 25
        assert result.email is None

    def test_pydantic_with_enum():
        """Test Pydantic model with enum field."""
        media = MediaFile(type=Color.RED, title="Test Video", size=1024)
        serialized = serialize_value(media)

        # The enum should be serialized as a string by model_dump(mode='json')
        assert serialized["__pydantic__"].endswith(".MediaFile")
        assert serialized["data"] == {
            "type": "red",  # Enum value as string
            "title": "Test Video",
            "size": 1024,
        }

        deserialized = deserialize_value(serialized)
        assert isinstance(deserialized, MediaFile)
        assert deserialized.type == Color.RED
        assert deserialized.title == "Test Video"
        assert deserialized.size == 1024

    def test_pydantic_in_tuple():
        """Test Pydantic model inside tuple."""
        person = Person(name="Charlie", age=35)
        original = (person, "metadata", 123)

        serialized = serialize_value(original)
        deserialized = deserialize_value(serialized)

        assert isinstance(deserialized, tuple)
        assert len(deserialized) == 3
        assert isinstance(deserialized[0], Person)
        assert deserialized[0].name == "Charlie"
        assert deserialized[1] == "metadata"
        assert deserialized[2] == 123

    def test_roundtrip_pydantic_with_nested_enum():
        """Test full roundtrip with Pydantic and nested enum."""
        original = MediaFile(type=Color.BLUE, title="Document", size=2048)
        serialized = serialize_value(original)
        deserialized = deserialize_value(serialized)

        assert deserialized == original
        assert isinstance(deserialized, type(original))
        assert deserialized.type == original.type

except ImportError:
    # Pydantic not installed, skip these tests
    pass
