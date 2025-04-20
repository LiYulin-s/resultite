from typing import TypeVar, Callable, Awaitable, Union, Any, Optional

# --- Core Types ---

T = TypeVar('T')
U = TypeVar('U')

Result = Union[T, Exception]
"""Represents a result that is either a value of type T or an Exception."""


# --- Execution Wrappers ---

def run_catching(func: Callable[..., T], *args: Any, **kwargs: Any) -> Result[T]:
    """
    Executes a synchronous function, catching any exceptions.

    Args:
        func: The synchronous function to execute.
        *args: Positional arguments to pass to func.
        **kwargs: Keyword arguments to pass to func.

    Returns:
        The result of the function if successful, or the Exception object
        if an error occurs.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return e


async def async_run_catching(func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> Result[T]:
    """
    Executes an asynchronous function, catching any exceptions.

    Args:
        func: The asynchronous function to execute.
        *args: Positional arguments to pass to func.
        **kwargs: Keyword arguments to pass to func.

    Returns:
        The awaited result of the function if successful, or the Exception
        object if an error occurs during execution or awaiting.
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        return e


# --- Result Handling: Extracting Values ---

def get_or_throw(result: Result[T]) -> T:
    """
    Returns the value if it's not an exception, otherwise raises the exception.

    Args:
        result: The Result object (value or exception).

    Returns:
        The contained value if 'result' is not an Exception.

    Raises:
        Exception: If 'result' contains an exception object.
    """
    if isinstance(result, Exception):
        raise result
    return result  # Type checker knows this must be T


def get_or_none(result: Result[T]) -> Optional[T]:
    """
    Returns the value if it's not an exception, otherwise returns None.

    Args:
        result: The Result object (value or exception).

    Returns:
        The contained value if 'result' is not an Exception, otherwise None.
    """
    if isinstance(result, Exception):
        return None
    return result


def get_or_default(result: Result[T], default: T) -> T:
    """
    Returns the value if it's not an exception, otherwise returns the default value.

    Args:
        result: The Result object (value or exception).
        default: The default value to return if 'result' contains an exception.

    Returns:
        The contained value if 'result' is not an Exception, otherwise 'default'.
    """
    if isinstance(result, Exception):
        return default
    return result


def get_or_else(result: Result[T], func: Callable[[Exception], T]) -> T:
    """
    Returns the value if it's not an exception, otherwise calls 'func' with
    the exception to compute a fallback value.

    Args:
        result: The Result object (value or exception).
        func: A synchronous function that takes the Exception as input and
              returns a fallback value of type T. Only called if 'result'
              is an Exception.

    Returns:
        The contained value if 'result' is not an Exception, or the result
        of calling 'func(exception)' if it is.
    """
    if isinstance(result, Exception):
        return func(result)
    return result


async def get_or_else_async(result: Result[T], func: Callable[[Exception], Awaitable[T]]) -> T:
    """
    Returns the value if it's not an exception, otherwise awaits 'func' with
    the exception to compute a fallback value.

    Args:
        result: The Result object (value or exception).
        func: An asynchronous function that takes the Exception as input and
              returns an awaitable yielding a fallback value of type T.
              Only awaited if 'result' is an Exception.

    Returns:
        The contained value if 'result' is not an Exception, or the awaited
        result of calling 'func(exception)' if it is.
    """
    if isinstance(result, Exception):
        return await func(result)
    return result


# --- Result Handling: Mapping/Chaining ---

def map_result(result: Result[T], func: Callable[[T], U]) -> Result[U]:
    """
    If 'result' contains a value, applies 'func' to it. If 'func' executes
    successfully, returns its result. If 'result' was an exception or 'func'
    raises an exception, returns the corresponding exception.

    Args:
        result: The input Result object (value T or exception).
        func: A synchronous function to apply to the value T if present.

    Returns:
        A Result[U] containing the result of func(value), the original
        exception, or any exception raised by func.
    """
    if isinstance(result, Exception):
        return result
    try:
        # We know result is of type T here
        return func(result)
    except Exception as e:
        return e


async def map_result_async(result: Result[T], func: Callable[[T], Awaitable[U]]) -> Result[U]:
    """
    If 'result' contains a value, awaits 'func' with it. If 'func' awaits
    successfully, returns its result. If 'result' was an exception or 'func'
    raises an exception, returns the corresponding exception.

    Args:
        result: The input Result object (value T or exception).
        func: An asynchronous function to await with the value T if present.

    Returns:
        A Result[U] containing the awaited result of func(value), the original
        exception, or any exception raised by func.
    """
    if isinstance(result, Exception):
        return result
    try:
        # We know result is of type T here
        return await func(result)
    except Exception as e:
        return e
