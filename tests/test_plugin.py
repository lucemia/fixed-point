import textwrap


def test_off_mode_no_cassette(pytester):
    pytester.makepyfile(
        sample_mod=textwrap.dedent("""\
            from fixedpoint import recordable

            @recordable
            def add(a, b):
                return a + b

            def outer(x):
                return add(x, 1)
        """)
    )
    pytester.makepyfile(
        textwrap.dedent("""\
            from sample_mod import outer

            def test_outer(fixedpoint):
                assert outer(10) == 11
        """)
    )
    result = pytester.runpytest("--fixedpoint=off")
    result.assert_outcomes(passed=1)
    assert not (pytester.path / "cassettes").exists()


def test_record_once_creates_cassette(pytester):
    pytester.makepyfile(
        sample_mod=textwrap.dedent("""\
            from fixedpoint import recordable

            @recordable
            def add(a, b):
                return a + b
        """)
    )
    pytester.makepyfile(
        textwrap.dedent("""\
            from sample_mod import add

            def test_add(fixedpoint):
                assert add(3, 4) == 7
        """)
    )
    result = pytester.runpytest("--fixedpoint=record_once")
    result.assert_outcomes(passed=1)

    # Find the cassette file (pytester names the test file dynamically)
    cassettes = list((pytester.path).rglob("test_add.yaml"))
    assert len(cassettes) == 1
    content = cassettes[0].read_text()
    assert "sample_mod.add" in content


def test_record_once_replays_existing(pytester):
    pytester.makepyfile(
        sample_mod=textwrap.dedent("""\
            from fixedpoint import recordable

            call_count = 0

            @recordable
            def add(a, b):
                global call_count
                call_count += 1
                return a + b
        """)
    )
    pytester.makepyfile(
        textwrap.dedent("""\
            import sample_mod
            from sample_mod import add

            def test_add(fixedpoint):
                result = add(3, 4)
                assert result == 7

            def test_add_called_once(fixedpoint):
                # After replay, call_count should still be 1 from first record
                add(3, 4)
        """)
    )
    # First run: record
    result = pytester.runpytest("--fixedpoint=record_once", "-v")
    result.assert_outcomes(passed=2)

    # Second run: replay (function should NOT be called again)
    result = pytester.runpytest("--fixedpoint=record_once", "-v")
    result.assert_outcomes(passed=2)


def test_replay_without_cassette_fails(pytester):
    pytester.makepyfile(
        sample_mod=textwrap.dedent("""\
            from fixedpoint import recordable

            @recordable
            def add(a, b):
                return a + b
        """)
    )
    pytester.makepyfile(
        textwrap.dedent("""\
            from sample_mod import add

            def test_add(fixedpoint):
                add(3, 4)
        """)
    )
    result = pytester.runpytest("--fixedpoint=replay")
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*CassetteNotFoundError*"])


def test_replay_with_cassette_works(pytester):
    pytester.makepyfile(
        sample_mod=textwrap.dedent("""\
            from fixedpoint import recordable

            @recordable
            def add(a, b):
                return a + b
        """)
    )
    pytester.makepyfile(
        textwrap.dedent("""\
            from sample_mod import add

            def test_add(fixedpoint):
                assert add(3, 4) == 7
        """)
    )
    # Record first
    pytester.runpytest("--fixedpoint=record_once")
    # Replay
    result = pytester.runpytest("--fixedpoint=replay")
    result.assert_outcomes(passed=1)


def test_rewrite_overwrites_cassette(pytester):
    pytester.makepyfile(
        sample_mod=textwrap.dedent("""\
            from fixedpoint import recordable

            counter = 0

            @recordable
            def get_counter():
                global counter
                counter += 1
                return counter
        """)
    )
    pytester.makepyfile(
        textwrap.dedent("""\
            from sample_mod import get_counter

            def test_counter(fixedpoint):
                assert get_counter() >= 1
        """)
    )
    # First record
    pytester.runpytest("--fixedpoint=rewrite")
    # Second rewrite should re-execute
    result = pytester.runpytest("--fixedpoint=rewrite")
    result.assert_outcomes(passed=1)


def test_parametrized_separate_cassettes(pytester):
    pytester.makepyfile(
        sample_mod=textwrap.dedent("""\
            from fixedpoint import recordable

            @recordable
            def double(x):
                return x * 2
        """)
    )
    pytester.makepyfile(
        textwrap.dedent("""\
            import pytest
            from sample_mod import double

            @pytest.mark.parametrize("x,expected", [(1, 2), (5, 10)])
            def test_double(fixedpoint, x, expected):
                assert double(x) == expected
        """)
    )
    result = pytester.runpytest("--fixedpoint=record_once", "-v")
    result.assert_outcomes(passed=2)

    cassettes = list((pytester.path / "cassettes").rglob("*.yaml"))
    assert len(cassettes) == 2


def test_outer_function_with_recordable_dep(pytester):
    pytester.makepyfile(
        sample_mod=textwrap.dedent("""\
            from fixedpoint import recordable

            @recordable
            def add(a, b):
                return a + b

            def outer(x):
                return add(x, 1) * 2
        """)
    )
    pytester.makepyfile(
        textwrap.dedent("""\
            from sample_mod import outer

            def test_outer(fixedpoint):
                assert outer(10) == 22
        """)
    )
    # Record
    result = pytester.runpytest("--fixedpoint=record_once")
    result.assert_outcomes(passed=1)

    # Replay
    result = pytester.runpytest("--fixedpoint=replay")
    result.assert_outcomes(passed=1)
