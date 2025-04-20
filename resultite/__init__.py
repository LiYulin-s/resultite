# resultite/__init__.py
from .core import (
    Result,
    T,
    U,
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

__all__ = [
    "Result",
    "T",
    "U",
    "run_catching",
    "async_run_catching",
    "get_or_throw",
    "get_or_none",
    "get_or_default",
    "get_or_else",
    "get_or_else_async",
    "map_result",
    "map_result_async",
]

# Optional: Define __version__
# __version__ = "0.1.0"