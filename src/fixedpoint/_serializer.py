from __future__ import annotations

import base64
import dataclasses
import enum
import importlib
from typing import Any


def serialize_value(value: Any) -> Any:
    # Check enum before primitives since IntEnum is also int
    if isinstance(value, enum.Enum):
        return {
            "__enum__": f"{type(value).__module__}.{type(value).__qualname__}",
            "value": value.value,
        }
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return {"__bytes__": base64.b64encode(value).decode("ascii")}
    if isinstance(value, tuple):
        return {"__tuple__": [serialize_value(v) for v in value]}
    if isinstance(value, set):
        return {"__set__": sorted(serialize_value(v) for v in value)}
    if isinstance(value, list):
        return [serialize_value(v) for v in value]
    if isinstance(value, dict):
        for k in value:
            if not isinstance(k, str):
                _raise(f"Dict keys must be strings, got {type(k).__name__}")
        return {k: serialize_value(v) for k, v in value.items()}

    # Check for Pydantic BaseModel (optional dependency)
    try:
        from pydantic import BaseModel
        if isinstance(value, BaseModel):
            cls = type(value)
            return {
                "__pydantic__": f"{cls.__module__}.{cls.__qualname__}",
                "data": serialize_value(value.model_dump(mode='json')),
            }
    except ImportError:
        pass

    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        cls = type(value)
        data: dict[str, Any] = {
            "__dataclass__": f"{cls.__module__}.{cls.__qualname__}",
        }
        for f in dataclasses.fields(value):
            data[f.name] = serialize_value(getattr(value, f.name))
        return data
    _raise(f"Cannot serialize type {type(value).__qualname__}")


def deserialize_value(data: Any) -> Any:
    if data is None or isinstance(data, (bool, int, float, str)):
        return data
    if isinstance(data, list):
        return [deserialize_value(v) for v in data]
    if isinstance(data, dict):
        if "__bytes__" in data:
            return base64.b64decode(data["__bytes__"])
        if "__enum__" in data:
            fqn = data["__enum__"]
            module_name, _, class_name = fqn.rpartition(".")
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            return cls(data["value"])
        if "__tuple__" in data:
            return tuple(deserialize_value(v) for v in data["__tuple__"])
        if "__set__" in data:
            return {deserialize_value(v) for v in data["__set__"]}
        if "__pydantic__" in data:
            fqn = data["__pydantic__"]
            module_name, _, class_name = fqn.rpartition(".")
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            model_data = deserialize_value(data["data"])
            return cls(**model_data)
        if "__dataclass__" in data:
            fqn = data["__dataclass__"]
            module_name, _, class_name = fqn.rpartition(".")
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            fields = {
                f.name: deserialize_value(data[f.name]) for f in dataclasses.fields(cls)
            }
            return cls(**fields)
        return {k: deserialize_value(v) for k, v in data.items()}
    _raise(f"Cannot deserialize type {type(data).__qualname__}")


def _raise(msg: str) -> None:
    from fixedpoint import SerializationError

    raise SerializationError(msg)
