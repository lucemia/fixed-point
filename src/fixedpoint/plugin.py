from __future__ import annotations

from pathlib import Path

import pytest

from fixedpoint._cassette import Cassette
from fixedpoint._interceptor import Interceptor


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("fixedpoint", "FixedPoint recording/replay")
    group.addoption(
        "--fixedpoint",
        dest="fixedpoint_mode",
        default="off",
        choices=["off", "replay", "record_once", "rewrite"],
        help="FixedPoint mode: off, replay, record_once, rewrite",
    )


@pytest.fixture
def fixedpoint(request: pytest.FixtureRequest):  # noqa: ANN201
    mode = request.config.getoption("fixedpoint_mode")
    if mode == "off":
        yield
        return

    cassette_dir = _get_cassette_dir(request)
    cassette_name = _get_cassette_name(request)
    cassette_path = cassette_dir / f"{cassette_name}.yaml"

    if mode == "replay":
        if not cassette_path.exists():
            from fixedpoint import CassetteNotFoundError

            raise CassetteNotFoundError(
                f"Cassette not found: {cassette_path}\n"
                f"  Hint: Run with --fixedpoint=record_once to create it."
            )
        cassette = Cassette.load(cassette_path)
    elif mode == "record_once":
        if cassette_path.exists():
            cassette = Cassette.load(cassette_path)
        else:
            cassette = Cassette(cassette_path)
    else:  # rewrite
        cassette = Cassette(cassette_path)

    interceptor = Interceptor(cassette, mode)
    interceptor.install()
    try:
        yield cassette
    finally:
        interceptor.uninstall()
        if mode in ("record_once", "rewrite"):
            cassette.save()


def _get_cassette_dir(request: pytest.FixtureRequest) -> Path:
    test_file = Path(request.fspath)
    module_name = test_file.stem
    return test_file.parent / "cassettes" / module_name


def _get_cassette_name(request: pytest.FixtureRequest) -> str:
    name = request.node.name
    for ch in r'[]/\:*?"<>|':
        name = name.replace(ch, "_")
    return name
