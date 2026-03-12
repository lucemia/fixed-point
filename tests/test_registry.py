import asyncio
import warnings

from fixedpoint._registry import clear_registry, get_registry, recordable


class TestRecordable:
    def setup_method(self):
        clear_registry()

    def test_registers_function(self):
        @recordable
        def my_func(x):
            return x

        reg = get_registry()
        assert my_func.__fixedpoint_key__ in reg

    def test_wraps_function(self):
        def original(x):
            return x

        decorated = recordable(original)
        assert decorated.__wrapped__ is original
        assert decorated.__name__ == "original"

    def test_sets_sentinel_attribute(self):
        @recordable
        def my_func():
            pass

        assert hasattr(my_func, "__fixedpoint_recordable__")
        assert my_func.__fixedpoint_recordable__ is True

    def test_function_still_works(self):
        @recordable
        def add(a, b):
            return a + b

        assert add(2, 3) == 5

    def test_warns_on_local_function(self):
        def make_func():
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                @recordable
                def inner():
                    pass

                assert len(w) == 1
                assert "locally-defined" in str(w[0].message)
            return inner

        make_func()


class TestRecordableAsync:
    def setup_method(self):
        clear_registry()

    def test_registers_async_function(self):
        @recordable
        async def my_func(x):
            return x

        reg = get_registry()
        assert my_func.__fixedpoint_key__ in reg

    def test_wraps_async_function(self):
        async def original(x):
            return x

        decorated = recordable(original)
        assert decorated.__wrapped__ is original
        assert decorated.__name__ == "original"

    def test_sets_sentinel_attribute(self):
        @recordable
        async def my_func():
            pass

        assert my_func.__fixedpoint_recordable__ is True

    def test_async_function_still_works(self):
        @recordable
        async def add(a, b):
            return a + b

        assert asyncio.run(add(2, 3)) == 5

    def test_decorated_is_coroutine_function(self):
        @recordable
        async def my_func():
            pass

        assert asyncio.iscoroutinefunction(my_func)
