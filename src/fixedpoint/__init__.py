from fixedpoint._registry import recordable

__version__ = "0.1.0"


class FixedPointError(Exception):
    pass


class CassetteNotFoundError(FixedPointError):
    pass


class CassetteMismatchError(FixedPointError):
    pass


class SerializationError(FixedPointError):
    pass


__all__ = [
    "recordable",
    "FixedPointError",
    "CassetteNotFoundError",
    "CassetteMismatchError",
    "SerializationError",
]
