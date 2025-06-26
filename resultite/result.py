from __future__ import annotations

"""resultite.result
====================

A more expressive, method-chaining friendly ``Result`` implementation inspired by
functional languages such as Rust, Scala and F#.

It *augments* the original minimalist implementation found in
:pyfile:`resultite.core` – it **does not** replace it.  The two styles can live
side-by-side inside the same package so that existing code depending on the
old Union-based API continues to run unchanged, while new code can benefit from
the richer API provided here.

The public surface is kept deliberately small:

* ``Result[T, E]`` – abstract base class for *Ok* / *Err* values.
* ``Ok(value)``     – wraps a successful value.
* ``Err(exc)``      – wraps an :class:`Exception` instance.
* ``resultify`` / ``async_resultify`` – convenience decorators turning a
  function that might raise into one that returns a :class:`Result`.

All heavy lifting happens on the two concrete subclasses.  Most methods are
implemented twice – a synchronous version as well as an ``async`` one – to
mirror the dual sync/async nature already present in :pymod:`resultite.core`.

The implementation purposefully avoids *any* external dependencies and only
relies on the standard library.
"""

from typing import (  # noqa: D401 – we want to expose these in __all__
    TypeVar,
    Generic,
    Callable,
    Awaitable,
    Any,
    final,
)

T = TypeVar("T")  # Success type
U = TypeVar("U")  # Success type after a mapping
E = TypeVar("E", bound=Exception)  # Error type (must derive from Exception)
F = TypeVar("F", bound=Exception)  # Error type after a mapping

__all__ = [
    "Result",
    "Ok",
    "Err",
    "resultify",
    "async_resultify",
]


class Result(Generic[T, E]):
    """A container holding either a successful value (*Ok*) or an error (*Err*).

    Instances of :class:`Result` are *immutable* – they never change their type
    once created.  This guarantees that a value that is ``Ok`` now will never
    silently turn into an ``Err`` later (and vice-versa).

    The base class offers helper *query*-methods such as :pymeth:`is_ok` or
    :pymeth:`is_err` while deferring all *value* operations to the concrete
    subclasses.
    """

    # Prevent direct instantiation of the base class – it is purely abstract.
    def __init__(self) -> None:
        if self.__class__ is Result:
            raise TypeError(
                "Cannot instantiate abstract class 'Result' directly.  Use Ok() "
                "or Err() instead."
            )

    # ---------------------------------------------------------------------
    # Query helpers – these do *not* inspect internal state of subclasses but
    # rely on `isinstance` checks.  This makes the implementation tiny and the
    # *contracts* of the methods crystal clear.
    # ---------------------------------------------------------------------

    def is_ok(self) -> bool:  # noqa: D401 – deliberate short name
        """Return *True* if this is an :class:`Ok` value."""

        return isinstance(self, Ok)

    def is_err(self) -> bool:  # noqa: D401 – deliberate short name
        """Return *True* if this is an :class:`Err` value."""

        return isinstance(self, Err)

    # ------------------------------------------------------------------
    # Value extraction helpers – must be provided by subclasses.
    # ------------------------------------------------------------------

    def unwrap(self) -> T:  # pragma: no cover – abstract method
        """Return the success value or raise the error contained in *Err*."""

        raise NotImplementedError

    def unwrap_or(self, default: T) -> T:  # pragma: no cover
        """Return the success value or *default* when this is an :class:`Err`."""

        raise NotImplementedError

    # ------------------------------------------------------------------
    # Mapping helpers – implemented differently for Ok / Err.
    # ------------------------------------------------------------------

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":  # noqa: D401
        """Map a function over the success value – subclass specific."""

        raise NotImplementedError

    def map_err(self, func: Callable[[E], F]) -> "Result[T, F]":  # noqa: D401
        """Map a function over the *error* – subclass specific."""

        raise NotImplementedError

    def and_then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":  # noqa: D401
        """Chain a function returning a :class:`Result` – subclass specific."""

        raise NotImplementedError

    # ------------------------------------------------------------------
    # Async versions – forward to subclass implementation.
    # ------------------------------------------------------------------

    async def map_async(self, func: Callable[[T], Awaitable[U]]) -> "Result[U, E]":  # noqa: D401
        raise NotImplementedError

    async def and_then_async(
        self, func: Callable[[T], Awaitable["Result[U, E]"]]
    ) -> "Result[U, E]":  # noqa: D401
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Equality helpers – subclasses inherit these definitions but override
    # `__eq__` for *value* comparisons.  Here we only implement rich comparison
    # with other types to *co-operate* with subclass overrides.
    # ------------------------------------------------------------------

    def __ne__(self, other: object) -> bool:  # type: ignore[override]
        return not self.__eq__(other)  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Success branch – Ok
# ---------------------------------------------------------------------------


@final
class Ok(Result[T, E]):
    """Wrap a successful *value* inside a :class:`Result`."""

    __slots__ = ("_value",)

    def __init__(self, value: T):
        # Bypass base-class check by *not* calling super().__init__() – we do
        # not want the *abstract* constructor raising TypeError.
        object.__setattr__(self, "_value", value)

    # -------------- built-ins ------------------------------------------------

    def __repr__(self) -> str:  # noqa: D401 – useful debug output
        return f"Ok({self._value!r})"

    def __eq__(self, other: object) -> bool:  # noqa: D401 – see base comment
        return isinstance(other, Ok) and self._value == other._value  # type: ignore[attr-defined]

    # ------------- extraction ----------------------------------------------

    def unwrap(self) -> T:  # noqa: D401
        return self._value

    def unwrap_or(self, default: T) -> T:  # noqa: D401 – default ignored
        return self._value

    # ------------- mapping --------------------------------------------------

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":  # noqa: D401
        try:
            return Ok(func(self._value))
        except Exception as exc:  # noqa: BLE001 – we *want* to capture broadly
            return Err(exc)  # type: ignore[arg-type]

    def map_err(self, func: Callable[[E], F]) -> "Result[T, F]":  # noqa: D401
        # Nothing to map – error branch ignored.
        return Ok(self._value)  # type: ignore[type-var]

    def and_then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":  # noqa: D401
        try:
            return func(self._value)
        except Exception as exc:  # noqa: BLE001
            return Err(exc)  # type: ignore[arg-type]

    # ---------------- async variants ----------------------------------------

    async def map_async(self, func: Callable[[T], Awaitable[U]]) -> "Result[U, E]":  # noqa: D401
        try:
            return Ok(await func(self._value))
        except Exception as exc:  # noqa: BLE001
            return Err(exc)  # type: ignore[arg-type]

    async def and_then_async(
        self, func: Callable[[T], Awaitable["Result[U, E]"]]
    ) -> "Result[U, E]":  # noqa: D401
        try:
            return await func(self._value)
        except Exception as exc:  # noqa: BLE001
            return Err(exc)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Failure branch – Err
# ---------------------------------------------------------------------------


@final
class Err(Result[T, E]):
    """Wrap an *Exception* inside a :class:`Result`."""

    __slots__ = ("_error",)

    def __init__(self, error: E):
        if not isinstance(error, Exception):
            raise TypeError("Err expects an Exception instance.")
        object.__setattr__(self, "_error", error)

    # -------------- built-ins ------------------------------------------------

    def __repr__(self) -> str:  # noqa: D401 – debug output
        return f"Err({self._error!r})"

    def __eq__(self, other: object) -> bool:  # noqa: D401
        return isinstance(other, Err) and self._error == other._error  # type: ignore[attr-defined]

    # ------------- extraction ----------------------------------------------

    def unwrap(self) -> T:  # noqa: D401
        # `self._error` is guaranteed to be an Exception instance.  The static
        # analyser cannot always prove this, hence the explicit ``type: ignore``.
        raise self._error  # type: ignore[misc]

    def unwrap_or(self, default: T) -> T:  # noqa: D401
        return default

    # ------------- mapping --------------------------------------------------

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":  # noqa: D401
        # Successful value is absent – pass error through.
        return Err(self._error)  # type: ignore[type-var]

    def map_err(self, func: Callable[[E], F]) -> "Result[T, F]":  # noqa: D401
        try:
            return Err(func(self._error))
        except Exception as exc:  # noqa: BLE001
            return Err(exc)  # type: ignore[arg-type]

    def and_then(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":  # noqa: D401
        # Already failed – propagate.
        return Err(self._error)  # type: ignore[type-var]

    # ---------------- async variants ----------------------------------------

    async def map_async(self, func: Callable[[T], Awaitable[U]]) -> "Result[U, E]":  # noqa: D401
        return Err(self._error)  # type: ignore[type-var]

    async def and_then_async(
        self, func: Callable[[T], Awaitable["Result[U, E]"]]
    ) -> "Result[U, E]":  # noqa: D401
        return Err(self._error)  # type: ignore[type-var]


# ---------------------------------------------------------------------------
# Decorators – resultify / async_resultify
# ---------------------------------------------------------------------------


def resultify(func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """Decorator turning *func* into one returning :class:`Result`.

    The decorated function behaves *exactly* the same as the original one with
    the only difference being that – instead of *raising* – any exception will
    be captured and returned as :class:`Err`.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Result[T, Exception]:  # type: ignore[type-var]
        try:
            return Ok(func(*args, **kwargs))
        except Exception as exc:  # noqa: BLE001
            return Err(exc)

    # Preserve introspection metadata.
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__.copy()
    return wrapper  # type: ignore[return-value]


def async_resultify(
    func: Callable[..., Awaitable[T]]
) -> Callable[..., Awaitable[Result[T, Exception]]]:
    """Async counterpart of :func:`resultify`."""

    async def wrapper(*args: Any, **kwargs: Any) -> Result[T, Exception]:  # type: ignore[type-var]
        try:
            return Ok(await func(*args, **kwargs))
        except Exception as exc:  # noqa: BLE001
            return Err(exc)

    wrapper.__name__ = func.__name__  # type: ignore[attr-defined]
    wrapper.__qualname__ = func.__qualname__  # type: ignore[attr-defined]
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__.copy()
    return wrapper  # type: ignore[return-value] 