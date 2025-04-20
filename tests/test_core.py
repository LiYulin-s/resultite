# tests/test_core.py
import asyncio
import unittest

# Import from the resultite package
# If your project root is in PYTHONPATH, this will work.
# Otherwise, you might need to adjust PYTHONPATH or install the package (e.g., pip install -e .)
from resultite import (
    Result, # For type hinting if needed in tests
    run_catching,
    async_run_catching,
    get_or_throw,
    get_or_none,
    get_or_default,
    get_or_else,
    get_or_else_async,
    map_result,
    map_result_async,
)

# Helper functions for testing
def sync_ok(x: int) -> int:
    return x * 2

def sync_fail(x: int) -> int:
    if x > 0:
        raise ValueError("Input must be non-positive")
    return x

async def async_ok(x: int) -> int:
    await asyncio.sleep(0.01)
    return x * 2

async def async_fail(x: int) -> int:
    await asyncio.sleep(0.01)
    if x > 0:
        raise ValueError("Input must be non-positive (async)")
    return x

def fallback_sync(e: Exception) -> int:
    return -1

async def fallback_async(e: Exception) -> int:
    await asyncio.sleep(0.01)
    return -2


class TestResultUtils(unittest.IsolatedAsyncioTestCase):

    # --- Test run_catching ---
    def test_run_catching_success(self):
        res = run_catching(sync_ok, 5)
        self.assertEqual(res, 10)
        res_kwargs = run_catching(lambda **kwargs: kwargs['a'] + kwargs['b'], a=1, b=2)
        self.assertEqual(res_kwargs, 3)


    def test_run_catching_failure(self):
        res = run_catching(sync_fail, 5)
        self.assertIsInstance(res, ValueError)
        self.assertEqual(str(res), "Input must be non-positive")

    # --- Test async_run_catching ---
    async def test_async_run_catching_success(self):
        res = await async_run_catching(async_ok, 5)
        self.assertEqual(res, 10)
        res_kwargs = await async_run_catching(lambda **kwargs: asyncio.sleep(0.01, result=kwargs['a']+kwargs['b']), a=1, b=2)
        self.assertEqual(res_kwargs, 3)

    async def test_async_run_catching_failure(self):
        res = await async_run_catching(async_fail, 5)
        self.assertIsInstance(res, ValueError)
        self.assertEqual(str(res), "Input must be non-positive (async)")

    # --- Test get_or_throw ---
    def test_get_or_throw_success(self):
        self.assertEqual(get_or_throw(10), 10)

    def test_get_or_throw_failure(self):
        err = ValueError("test")
        with self.assertRaises(ValueError) as cm:
            get_or_throw(err)
        self.assertIs(cm.exception, err)

    # --- Test get_or_none ---
    def test_get_or_none_success(self):
        self.assertEqual(get_or_none(10), 10)

    def test_get_or_none_failure(self):
        self.assertIsNone(get_or_none(ValueError("test")))

    # --- Test get_or_default ---
    def test_get_or_default_success(self):
        self.assertEqual(get_or_default(10, -1), 10)

    def test_get_or_default_failure(self):
        self.assertEqual(get_or_default(ValueError("test"), -1), -1)

    # --- Test get_or_else ---
    def test_get_or_else_success(self):
        self.assertEqual(get_or_else(10, fallback_sync), 10)

    def test_get_or_else_failure(self):
        err = ValueError("test")
        self.assertEqual(get_or_else(err, fallback_sync), -1)

    # --- Test get_or_else_async ---
    async def test_get_or_else_async_success(self):
        self.assertEqual(await get_or_else_async(10, fallback_async), 10)

    async def test_get_or_else_async_failure(self):
        err = ValueError("test")
        self.assertEqual(await get_or_else_async(err, fallback_async), -2)

    # --- Test map_result ---
    def test_map_result_success_success(self):
        # Explicitly type hint the successful input for clarity in test
        successful_input: Result[int] = 10
        res = map_result(successful_input, lambda x: f"Value: {x}")
        self.assertEqual(res, "Value: 10")

    def test_map_result_success_fail(self):
        successful_input: Result[int] = 10
        res = map_result(successful_input, lambda x: sync_fail(x)) # sync_fail raises for > 0
        self.assertIsInstance(res, ValueError)
        self.assertEqual(str(res), "Input must be non-positive")

    def test_map_result_failure(self):
        err = TypeError("Original error")
        # Explicitly type hint the error input for clarity in test
        error_input: Result[int] = err
        res = map_result(error_input, lambda x: f"Value: {x}")
        self.assertIs(res, err) # Should pass the original error through

    # --- Test map_result_async ---
    async def test_map_result_async_success_success(self):
        successful_input: Result[int] = 10
        res = await map_result_async(successful_input, lambda x: async_ok(x))
        self.assertEqual(res, 20)

    async def test_map_result_async_success_fail(self):
        successful_input: Result[int] = 10
        res = await map_result_async(successful_input, lambda x: async_fail(x)) # async_fail raises for > 0
        self.assertIsInstance(res, ValueError)
        self.assertEqual(str(res), "Input must be non-positive (async)")

    async def test_map_result_async_failure(self):
        err = TypeError("Original error")
        error_input: Result[int] = err
        res = await map_result_async(error_input, lambda x: async_ok(x))
        self.assertIs(res, err) # Should pass the original error through

if __name__ == "__main__":
    # This allows running tests directly from this file: python tests/test_core.py
    # For discovery, you'd run from the project root: python -m unittest discover tests
    unittest.main()