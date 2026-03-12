from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CallRecord:
    args: Any
    kwargs: Any
    return_value: Any


@dataclass
class CassetteData:
    version: int = 1
    calls: dict[str, list[CallRecord]] = field(default_factory=dict)
