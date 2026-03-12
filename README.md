# fixed-point

* Fixed-Point is a pytest plugin designed to record and replay deterministic function calls, making your tests stable and reproducible.
* Flaky tests are the bane of every developer's existence. I prefer not to rely on retries, mocks that drift from reality, or fragile test setups to keep things green.
* To tackle this problem, Fixed-Point captures real function outputs and replays them faithfully, so your tests always land on the same answer — a fixed point.
* It boasts simplicity, making it exceptionally easy to adopt in any pytest project.
* Fixed-Point serves as a specialized testing tool, particularly tailored for pinning down the behavior of functions that talk to external services. If you encounter any cases not covered by the plugin, please don't hesitate to create an issue for further assistance.

## Installation

You can install pytest-fixedpoint using pip, the Python package manager:

```
pip install pytest-fixedpoint
```

## Getting Started

To start using fixed-point in your project, simply decorate the functions you want to pin down with `@recordable`:

```python
from fixedpoint import recordable

@recordable
def call_external_api(query):
    return external_service.search(query)

def test_search(fixedpoint):
    result = call_external_api("hello")
    assert result == expected
```

The first time you run with `--fixedpoint=record_once`, it captures real outputs. Every subsequent run replays them — no network calls, no flakiness.

## Async Support

`@recordable` works with `async` functions and methods out of the box — no extra setup needed:

```python
from fixedpoint import recordable

@recordable
async def fetch_user(user_id):
    return await external_service.get_user(user_id)

@recordable
async def search(query):
    return await external_service.search(query)

async def test_fetch_user(fixedpoint):
    user = await fetch_user(42)
    assert user["name"] == "Alice"
```

It also works with async methods on classes:

```python
from fixedpoint import recordable

class UserClient:
    @recordable
    async def get_user(self, user_id):
        return await self._session.get(f"/users/{user_id}")

    @recordable
    async def list_users(self):
        return await self._session.get("/users")

async def test_user_client(fixedpoint):
    client = UserClient()
    user = await client.get_user(42)
    assert user["name"] == "Alice"
```

The decorator detects whether the function is a coroutine and wraps it accordingly. Recording and replay work identically — the cassette format is the same for sync and async functions.

## Modes

Fixed-Point supports 4 operational modes via the `--fixedpoint` CLI option:

| Mode | Behavior |
|------|----------|
| `off` | Default. Plugin is disabled, functions execute normally. |
| `record_once` | Record new calls, replay existing ones. Ideal for initial setup. |
| `replay` | Replay only. Fails with `CassetteNotFoundError` if no recording exists. Perfect for CI. |
| `rewrite` | Always re-execute and overwrite recordings. Use when the real behavior has changed. |

```bash
# Record cassettes for the first time
pytest tests/ --fixedpoint=record_once

# Replay from cassettes (safe for CI)
pytest tests/ --fixedpoint=replay

# Force re-record everything
pytest tests/ --fixedpoint=rewrite

# Disable (default)
pytest tests/
```

## Cassettes

Recordings are stored as human-readable YAML files in `tests/cassettes/`:

```
tests/cassettes/
  test_module_name/
    test_function_name.yaml
```

A cassette file looks like:

```yaml
version: 1
calls:
  myapp.api.fetch_user:
    - args: [42]
      kwargs: {}
      return: {"name": "Alice", "age": 30}
```

Cassettes are committed to your repo so the whole team replays the same results.

## Supported Types

The serializer handles these types out of the box:

| Type | Serialized As |
|------|---------------|
| `None`, `bool`, `int`, `float`, `str` | Direct values |
| `bytes` | `{"__bytes__": "<base64>"}` |
| `tuple` | `{"__tuple__": [...]}` |
| `set` | `{"__set__": [...]}` |
| `list`, `dict` | Direct JSON arrays/objects |
| `dataclass` | `{"__dataclass__": "module.Class", ...fields}` |

## Error Handling

Fixed-Point raises clear errors when things don't match:

| Exception | When |
|-----------|------|
| `CassetteNotFoundError` | No cassette file found in `replay` mode |
| `CassetteMismatchError` | Recorded args don't match actual call, or too many calls |
| `SerializationError` | Unsupported type passed to a `@recordable` function |

When you see a `CassetteMismatchError`, the error message includes a hint:

> Run with `--fixedpoint=rewrite` to re-record

## Comparison

### vs VCR.py / responses / requests-mock

VCR-style tools record at the **HTTP layer** — every header, cookie, content-type, and redirect ends up in your cassette. This means:

* Cassettes are bloated with details you don't care about (auth tokens, timestamps, trace IDs).
* An unrelated header change breaks your tests even though the actual data hasn't changed.
* You're testing HTTP plumbing, not your application logic.

Fixed-Point records at the **function layer**. You choose exactly which functions to pin down with `@recordable`, and the cassette only contains the args and return values — nothing more.

### vs unittest.mock / monkeypatch

Mocking is powerful, but it comes at a cost:

* You have to **manually write** the return values. Guess wrong and your mock drifts from reality.
* As your code evolves, you spend more time maintaining mocks than writing actual tests.
* Mocks tell you nothing about what the real function actually returned — they only tell you what you *assumed* it would return.

Fixed-Point records **real outputs** on the first run. No guessing, no hand-crafting fixtures. When reality changes, just `--fixedpoint=rewrite` and you're back in sync.

### Summary

| | VCR.py | mock | fixed-point |
|---|--------|------|-------------|
| Records at | HTTP layer | N/A (manual) | Function layer |
| Setup effort | Low | High | Low |
| Cassette noise | High (headers, cookies, etc.) | N/A | Low (args + return only) |
| Stays in sync with reality | Fragile | Drifts over time | `rewrite` to refresh |

## Why fixed-point?

* In math, a fixed point is a value that stays the same no matter what function you throw at it. This project does the same for your tests — run them once, pin the result, replay forever.
* But honestly, I named it "fixed-point" because of my wife. She's my fixed point — always cute, always kind, and somehow always right. No matter how chaotic things get, she's the constant I can count on.
* So this one's for her. And if it makes your tests less flaky along the way, that's a nice bonus too.
