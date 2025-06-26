# resultite/__init__.py
# ---- Legacy functional helpers (Union-based) --------------------------------
from .core import (
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

# ---- New, richer API -------------------------------------------------------
from .result import Result, Ok, Err, resultify, async_resultify

__all__ = [
    "Result",
    "Ok",
    "Err",
    "resultify",
    "async_resultify",
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