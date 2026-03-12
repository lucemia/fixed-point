from fixedpoint._cassette import Cassette
from fixedpoint._interceptor import Interceptor
from fixedpoint._registry import _active_interceptor

from tests.sample_app import math_funcs


class TestInterceptor:
    def test_record_mode(self, tmp_path):
        path = tmp_path / "test.yaml"
        cassette = Cassette(path)
        interceptor = Interceptor(cassette, "rewrite")
        interceptor.install()
        try:
            result = math_funcs.add(3, 4)
            assert result == 7
        finally:
            interceptor.uninstall()

        cassette.save()
        loaded = Cassette.load(path)
        assert loaded.has_calls("tests.sample_app.math_funcs.add")

    def test_replay_mode(self, tmp_path):
        path = tmp_path / "test.yaml"
        cassette = Cassette(path)
        cassette.record_call("tests.sample_app.math_funcs.add", (3, 4), {}, 999)
        cassette.save()

        loaded = Cassette.load(path)
        interceptor = Interceptor(loaded, "replay")
        interceptor.install()
        try:
            result = math_funcs.add(3, 4)
            assert result == 999  # replayed, not computed
        finally:
            interceptor.uninstall()

    def test_uninstall_clears_interceptor(self, tmp_path):
        from fixedpoint import _registry

        path = tmp_path / "test.yaml"
        cassette = Cassette(path)
        interceptor = Interceptor(cassette, "rewrite")

        interceptor.install()
        assert _registry._active_interceptor is interceptor
        interceptor.uninstall()
        assert _registry._active_interceptor is None

    def test_no_interception_when_uninstalled(self, tmp_path):
        # Without interceptor, functions work normally
        result = math_funcs.add(3, 4)
        assert result == 7

    def test_record_once_replays_existing(self, tmp_path):
        path = tmp_path / "test.yaml"
        cassette = Cassette(path)
        cassette.record_call("tests.sample_app.math_funcs.add", (3, 4), {}, 999)
        cassette.save()

        loaded = Cassette.load(path)
        interceptor = Interceptor(loaded, "record_once")
        interceptor.install()
        try:
            result = math_funcs.add(3, 4)
            assert result == 999
        finally:
            interceptor.uninstall()

    def test_record_once_records_new(self, tmp_path):
        path = tmp_path / "test.yaml"
        cassette = Cassette(path)
        interceptor = Interceptor(cassette, "record_once")
        interceptor.install()
        try:
            result = math_funcs.multiply(5, 6)
            assert result == 30
        finally:
            interceptor.uninstall()

        cassette.save()
        loaded = Cassette.load(path)
        assert loaded.has_calls("tests.sample_app.math_funcs.multiply")
