from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from fixedpoint._serializer import deserialize_value, serialize_value
from fixedpoint._types import CallRecord, CassetteData


class Cassette:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._data = CassetteData()
        self._replay_counters: dict[str, int] = {}
        self._dirty = False

    @classmethod
    def load(cls, path: Path) -> Cassette:
        c = cls(path)
        raw = yaml.safe_load(path.read_text())
        if not isinstance(raw, dict):
            _raise_mismatch(f"Invalid cassette format in {path}")
        version = raw.get("version", 1)
        c._data.version = version
        for func_key, entries in raw.get("calls", {}).items():
            records = []
            for entry in entries:
                records.append(
                    CallRecord(
                        args=entry["args"],
                        kwargs=entry.get("kwargs", {}),
                        return_value=entry["return"],
                    )
                )
            c._data.calls[func_key] = records
        return c

    def has_calls(self, func_key: str) -> bool:
        calls = self._data.calls.get(func_key)
        if not calls:
            return False
        idx = self._replay_counters.get(func_key, 0)
        return idx < len(calls)

    def record_call(
        self, func_key: str, args: tuple, kwargs: dict, return_value: Any
    ) -> None:
        record = CallRecord(
            args=serialize_value(args),
            kwargs=serialize_value(kwargs),
            return_value=serialize_value(return_value),
        )
        self._data.calls.setdefault(func_key, []).append(record)
        self._dirty = True

    def replay_call(
        self, func_key: str, args: tuple, kwargs: dict
    ) -> Any:
        calls = self._data.calls.get(func_key)
        if not calls:
            _raise_mismatch(f"No recorded calls for {func_key}")
        idx = self._replay_counters.get(func_key, 0)
        if idx >= len(calls):
            _raise_mismatch(
                f"Too many calls to {func_key}: expected {len(calls)}, "
                f"got call #{idx + 1}"
            )
        record = calls[idx]
        serialized_args = serialize_value(args)
        serialized_kwargs = serialize_value(kwargs)
        if serialized_args != record.args or serialized_kwargs != record.kwargs:
            _raise_mismatch(
                f"Argument mismatch for {func_key} call #{idx + 1}.\n"
                f"  Expected args={record.args} kwargs={record.kwargs}\n"
                f"  Got      args={serialized_args} kwargs={serialized_kwargs}\n"
                f"  Hint: Run with --fixedpoint=rewrite to re-record."
            )
        self._replay_counters[func_key] = idx + 1
        return deserialize_value(record.return_value)

    def save(self) -> None:
        if not self._dirty:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        raw: dict = {
            "version": self._data.version,
            "calls": {
                key: [
                    {
                        "args": r.args,
                        "kwargs": r.kwargs,
                        "return": r.return_value,
                    }
                    for r in records
                ]
                for key, records in self._data.calls.items()
            },
        }
        self._path.write_text(
            yaml.dump(raw, default_flow_style=False, sort_keys=False)
        )


def _raise_mismatch(msg: str) -> None:
    from fixedpoint import CassetteMismatchError

    raise CassetteMismatchError(msg)
