import asyncio
import unittest
from typing import Any, Callable

from resultite.result import (
    Ok,
    Err,
    Result,
    resultify,
    async_resultify,
)


# ----------------------- helper functions ----------------------------------

def inc(x: int) -> int:
    return x + 1


def fail(x: int) -> int:  # noqa: D401 – explicit failure for testing
    raise ValueError("boom")


async def async_inc(x: int) -> int:
    await asyncio.sleep(0.01)
    return x + 1


async def async_fail(x: int) -> int:  # noqa: D401
    await asyncio.sleep(0.01)
    raise ValueError("boom-async")


# A function that may or may not raise – useful for @resultify tests

def maybe_raise(x: int) -> int:
    if x > 0:
        raise RuntimeError("positive is forbidden")
    return x


@resultify
def maybe_raise_wrapped(x: int) -> int:  # type: ignore[valid-type]
    return maybe_raise(x)


@async_resultify
async def async_maybe_raise_wrapped(x: int) -> int:  # type: ignore[valid-type]
    return await asyncio.sleep(0, result=maybe_raise(x))


# ----------------------- test suite ----------------------------------------


class TestResultAPI(unittest.IsolatedAsyncioTestCase):
    # --- fundamental predicates -----------------------------------------

    def test_is_ok_err_predicates(self):
        self.assertTrue(Ok(1).is_ok())
        self.assertFalse(Ok(1).is_err())
        self.assertTrue(Err(ValueError()).is_err())

    # --- unwrap / unwrap_or ---------------------------------------------

    def test_unwrap_success(self):
        self.assertEqual(Ok("hello").unwrap(), "hello")

    def test_unwrap_failure(self):
        err = Err(ValueError("bad"))
        with self.assertRaises(ValueError):
            err.unwrap()

    def test_unwrap_or(self):
        self.assertEqual(Ok(5).unwrap_or(0), 5)
        self.assertEqual(Err(ValueError()).unwrap_or(0), 0)

    # --- map ------------------------------------------------------------

    def test_map_on_ok(self):
        self.assertEqual(Ok(1).map(inc), Ok(2))

    def test_map_on_err(self):
        exc = ValueError("x")
        err_val: Result[int, ValueError] = Err(exc)
        self.assertEqual(err_val.map(inc), Err(exc))

    def test_map_function_raises(self):
        res = Ok(1).map(fail)
        self.assertTrue(res.is_err())

    # --- map_err --------------------------------------------------------

    def test_map_err_on_err(self):
        err = Err(ValueError("bad"))
        mapped = err.map_err(lambda e: RuntimeError(str(e)))
        self.assertTrue(mapped.is_err())
        # ensure type changed
        self.assertIsInstance(mapped, Err)
        if isinstance(mapped, Err):  # mypy friendliness
            self.assertIsInstance(mapped._error, RuntimeError)  # noqa: SLF001

    def test_map_err_noop_on_ok(self):
        self.assertEqual(Ok(2).map_err(lambda e: RuntimeError("unused")), Ok(2))

    # --- and_then (bind) -------------------------------------------------

    def test_and_then_success(self):
        res = Ok(2).and_then(lambda x: Ok(x * 10))
        self.assertEqual(res, Ok(20))

    def test_and_then_propagates_err(self):
        err = Err(ValueError("oops"))
        self.assertEqual(err.and_then(lambda x: Ok(x * 10)), err)

    def test_and_then_function_returns_err(self):
        res = Ok(2).and_then(lambda x: Err(ValueError("fail")))
        self.assertTrue(res.is_err())

    # --- async map / and_then ------------------------------------------

    async def test_map_async_ok(self):
        res = await Ok(3).map_async(async_inc)
        self.assertEqual(res, Ok(4))

    async def test_map_async_err(self):
        res = await Err(ValueError()).map_async(async_inc)
        self.assertTrue(res.is_err())

    async def test_and_then_async_ok(self):
        res = await Ok(5).and_then_async(lambda x: asyncio.sleep(0, result=Ok(x + 1)))
        self.assertEqual(res, Ok(6))

    async def test_and_then_async_err(self):
        res = await Err(ValueError()).and_then_async(lambda x: asyncio.sleep(0, result=Ok(x + 1)))
        self.assertTrue(res.is_err())

    # --- decorators: resultify / async_resultify ------------------------

    def test_resultify_decorator(self):
        self.assertEqual(maybe_raise_wrapped(0), Ok(0))
        self.assertTrue(maybe_raise_wrapped(1).is_err())

    async def test_async_resultify_decorator(self):
        self.assertEqual(await async_maybe_raise_wrapped(0), Ok(0))
        res = await async_maybe_raise_wrapped(1)
        self.assertTrue(res.is_err())


if __name__ == "__main__":
    unittest.main() 