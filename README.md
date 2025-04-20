s# **Resultite**
**Minimalist Result Type Handling with Pure Python Typing**

Tired of boilerplate classes just to represent success or failure? Looking for Rust-like `Result` expressiveness **without** adopting a whole new type system or custom classes?

**Resultite** offers a clean, lightweight approach using Python's native `Union[T, Exception]` type hint pattern. Capture function outcomes transparently, handle errors gracefully, and chain operations—all with standard Python functions and type safety. It's the Pythonic way to handle results.

---

## ✨ Features

- ✅ **Purely Type-Based:** Uses `typing.Union[T, Exception]` (aliased as `Result[T]`) – no custom classes needed.
- ✅ **Type-Safe:** Leverages Python's type hinting for robust error handling patterns.
- ✅ **Sync & Async:** Seamlessly works with both synchronous and asynchronous functions.
- ✅ **Composable:** Functions designed for easy chaining and transformation of results.
- ✅ **Minimal & Lightweight:** No external dependencies beyond standard Python.
- ✅ **Easy Handling:** Utility functions to extract values, provide defaults, map results, or raise errors.
- ✅ **Testable:** Simple functional units make testing straightforward.
- ✅ **Pythonic Philosophy:** Embraces Python's built-in features over introducing complex abstractions.

---

## 📦 Installation

```bash
pip install resultite
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install resultite
```

---

## 🔧 Usage

**Basic Sync Example:**

```python
from resultite import run_catching, get_or_throw, get_or_default, Result

def might_fail(data: str) -> int:
    if not data:
        raise ValueError("Input cannot be empty")
    return int(data) * 2

# Capture the outcome
result: Result[int] = run_catching(might_fail, "10") # -> 20
error_result: Result[int] = run_catching(might_fail, "") # -> ValueError("Input cannot be empty")

# Handle the result
try:
    value = get_or_throw(error_result) # Raises ValueError
except ValueError as e:
    print(f"Caught expected error: {e}")

# Provide a default
safe_value = get_or_default(error_result, -1) # -> -1
print(f"Safe value: {safe_value}")

# Get None on error
maybe_value = get_or_none(result) # -> 20
maybe_error = get_or_none(error_result) # -> None
```

**Async Example:**

```python
import asyncio
from resultite import async_run_catching, map_result_async, get_or_else_async

async def fetch_data(url: str) -> dict:
    # In a real scenario, this would use a library like aiohttp
    await asyncio.sleep(0.1)
    if "error" in url:
        raise ConnectionError("Failed to connect")
    return {"data": url}

async def process_data(data: dict) -> str:
    await asyncio.sleep(0.1)
    return data.get("data", "default").upper()

async def main():
    result: Result[dict] = await async_run_catching(fetch_data, "http://example.com")
    # -> {"data": "http://example.com"}

    error_result: Result[dict] = await async_run_catching(fetch_data, "http://error.com")
    # -> ConnectionError("Failed to connect")

    # Map the successful result asynchronously
    processed_result: Result[str] = await map_result_async(result, process_data)
    # -> "HTTP://EXAMPLE.COM"

    # Handle error result with an async fallback
    final_value = await get_or_else_async(
        processed_result,
        lambda e: f"Async fallback for error: {e}" # Fallback if process_data failed
    )
    print(f"Processed value: {final_value}") # -> Processed value: HTTP://EXAMPLE.COM

    final_error_value = await get_or_else_async(
        error_result, # Original fetch error
        lambda e: f"Async fallback for error: {e}"
    )
    # -> Async fallback for error: Failed to connect
    print(f"Processed error value: {final_error_value}")

asyncio.run(main())
```

---

## 🔁 API Overview

The core type is `Result[T] = Union[T, Exception]`.

| Function | Description | Sync/Async |
|----------|-------------|------------|
| `run_catching(func, *args, **kwargs)` | Executes `func(*args, **kwargs)` and returns `Result[T]`. | Sync |
| `async_run_catching(func, *args, **kwargs)` | Awaits `func(*args, **kwargs)` and returns `Result[T]`. | Async |
| `get_or_throw(result)` | Returns `T` if `result` is `T`, otherwise raises the `Exception`. | Sync |
| `get_or_none(result)` | Returns `T` if `result` is `T`, otherwise returns `None`. | Sync |
| `get_or_default(result, default)` | Returns `T` if `result` is `T`, otherwise returns `default`. | Sync |
| `get_or_else(result, func)` | Returns `T` if `result` is `T`, otherwise calls `func(exception)` to get a fallback `T`. | Sync |
| `get_or_else_async(result, func)` | Returns `T` if `result` is `T`, otherwise awaits `func(exception)` to get a fallback `T`. | Async |
| `map_result(result, func)` | If `result` is `T`, returns `run_catching(func, result)`. If `result` is `Exception`, returns the exception. Output is `Result[U]`. | Sync |
| `map_result_async(result, func)` | If `result` is `T`, returns `await async_run_catching(func, result)`. If `result` is `Exception`, returns the exception. Output is `Result[U]`. | Async |

---

## ✅ Testing

Tests use Python's built-in `unittest` module.

First, install test dependencies (e.g., if you need specific libraries for test functions):

```bash
# Using pip
pip install .[test]

# Using uv
uv pip install .[test]
```
*(Note: Add a `[test]` extra in your `pyproject.toml` if you have test-specific dependencies).*

Then, run tests:

```bash
# Discover and run tests using unittest's discovery
python -m unittest discover tests

# Or use pytest (it can run unittest tests)
pytest
```

---

## 🧪 Design Philosophy

> No DSLs. No magic classes. No frameworks.
> Just Python's strengths, applied cleanly.

Resultite embraces Python's existing type system to provide a robust yet minimal way to handle function outcomes. It avoids introducing new abstractions often seen elsewhere, focusing instead on simple, composable functions that operate on the standard `Union[T, Exception]` pattern. Inspired by the clarity of `Result` patterns, but executed with Pythonic simplicity and pragmatism.

---

## ❤️ Credits

Crafted with a love for minimalism and functional programming principles in Python.

---

## 📄 License

MIT License