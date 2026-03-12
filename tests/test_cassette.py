import pytest
import yaml

from fixedpoint import CassetteMismatchError
from fixedpoint._cassette import Cassette


class TestCassette:
    def test_record_and_save(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.func", (1, 2), {}, 3)
        c.save()

        raw = yaml.safe_load(path.read_text())
        assert raw["version"] == 1
        assert "mod.func" in raw["calls"]
        assert raw["calls"]["mod.func"][0]["return"] == 3

    def test_load_and_replay(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.func", (10,), {"k": "v"}, 42)
        c.save()

        loaded = Cassette.load(path)
        result = loaded.replay_call("mod.func", (10,), {"k": "v"})
        assert result == 42

    def test_sequential_replay(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.func", (1,), {}, "first")
        c.record_call("mod.func", (2,), {}, "second")
        c.save()

        loaded = Cassette.load(path)
        assert loaded.replay_call("mod.func", (1,), {}) == "first"
        assert loaded.replay_call("mod.func", (2,), {}) == "second"

    def test_too_many_calls_raises(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.func", (1,), {}, "only")
        c.save()

        loaded = Cassette.load(path)
        loaded.replay_call("mod.func", (1,), {})
        with pytest.raises(CassetteMismatchError, match="Too many calls"):
            loaded.replay_call("mod.func", (1,), {})

    def test_argument_mismatch_raises(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.func", (1,), {}, 42)
        c.save()

        loaded = Cassette.load(path)
        with pytest.raises(CassetteMismatchError, match="Argument mismatch"):
            loaded.replay_call("mod.func", (999,), {})

    def test_no_recorded_calls_raises(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.other", (1,), {}, 1)
        c.save()

        loaded = Cassette.load(path)
        with pytest.raises(CassetteMismatchError, match="No recorded calls"):
            loaded.replay_call("mod.func", (1,), {})

    def test_has_calls(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.func", (1,), {}, 42)
        c.save()

        loaded = Cassette.load(path)
        assert loaded.has_calls("mod.func") is True
        assert loaded.has_calls("mod.other") is False

    def test_has_calls_exhausted(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.func", (1,), {}, 42)
        c.save()

        loaded = Cassette.load(path)
        assert loaded.has_calls("mod.func") is True
        loaded.replay_call("mod.func", (1,), {})
        assert loaded.has_calls("mod.func") is False

    def test_creates_parent_directories(self, tmp_path):
        path = tmp_path / "deep" / "nested" / "test.yaml"
        c = Cassette(path)
        c.record_call("mod.func", (), {}, 1)
        c.save()
        assert path.exists()

    def test_no_save_when_not_dirty(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.save()
        assert not path.exists()

    def test_complex_values(self, tmp_path):
        path = tmp_path / "test.yaml"
        c = Cassette(path)
        c.record_call(
            "mod.func",
            ([1, 2], {"key": "val"}),
            {"opt": True},
            {"result": [1, 2, 3]},
        )
        c.save()

        loaded = Cassette.load(path)
        result = loaded.replay_call("mod.func", ([1, 2], {"key": "val"}), {"opt": True})
        assert result == {"result": [1, 2, 3]}
