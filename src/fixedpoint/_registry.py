from __future__ import annotations

import asyncio
import functools
import warnings
from collections.abc import Callable
from typing import Any, TypeVar

_REGISTRY: dict[str, Callable] = {}
_active_interceptor: Any = None

F = TypeVar("F", bound=Callable)


def recordable(fn: F) -> F:
    key = f"{fn.__module__}.{fn.__qualname__}"
    if "<locals>" in key:
        warnings.warn(
            f"fixedpoint: {key} is a locally-defined function. "
            "Cassettes may break if the enclosing function is renamed.",
            stacklevel=2,
        )

    if asyncio.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            interceptor = _active_interceptor
            if interceptor is not None:
                return await interceptor.async_intercept(key, fn, args, kwargs)
            return await fn(*args, **kwargs)

        async_wrapper.__wrapped__ = fn  # type: ignore[attr-defined]
        async_wrapper.__fixedpoint_recordable__ = True  # type: ignore[attr-defined]
        async_wrapper.__fixedpoint_key__ = key  # type: ignore[attr-defined]
        _REGISTRY[key] = fn
        return async_wrapper  # type: ignore[return-value]

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        interceptor = _active_interceptor
        if interceptor is not None:
            return interceptor.intercept(key, fn, args, kwargs)
        return fn(*args, **kwargs)

    wrapper.__wrapped__ = fn  # type: ignore[attr-defined]
    wrapper.__fixedpoint_recordable__ = True  # type: ignore[attr-defined]
    wrapper.__fixedpoint_key__ = key  # type: ignore[attr-defined]
    _REGISTRY[key] = fn
    return wrapper  # type: ignore[return-value]


def get_registry() -> dict[str, Callable]:
    return _REGISTRY


def clear_registry() -> None:
    _REGISTRY.clear()


def set_active_interceptor(interceptor: Any) -> None:
    global _active_interceptor
    _active_interceptor = interceptor
