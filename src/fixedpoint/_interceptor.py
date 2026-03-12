from __future__ import annotations

from typing import Any

from fixedpoint._cassette import Cassette
from fixedpoint._registry import set_active_interceptor


class Interceptor:
    def __init__(self, cassette: Cassette, mode: str) -> None:
        self._cassette = cassette
        self._mode = mode

    def install(self) -> None:
        set_active_interceptor(self)

    def uninstall(self) -> None:
        set_active_interceptor(None)

    def intercept(self, key: str, original: Any, args: tuple, kwargs: dict) -> Any:
        mode = self._mode
        cassette = self._cassette

        if mode in ("replay", "record_once") and cassette.has_calls(key):
            return cassette.replay_call(key, args, kwargs)
        if mode in ("record_once", "rewrite"):
            result = original(*args, **kwargs)
            cassette.record_call(key, args, kwargs, result)
            return result
        if mode == "replay":
            from fixedpoint import CassetteNotFoundError

            raise CassetteNotFoundError(
                f"No cassette entry for {key} and mode is 'replay'.\n"
                f"  Hint: Run with --fixedpoint=record_once to create it."
            )
        return original(*args, **kwargs)
