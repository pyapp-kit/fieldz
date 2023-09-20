from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, ClassVar, Protocol

from fieldz._types import DataclassParams, Field

if TYPE_CHECKING:

    class _DataclassParams(Protocol):
        init: bool
        repr: bool
        eq: bool
        order: bool
        unsafe_hash: bool
        frozen: bool

    class DataclassInstance(Protocol):
        __dataclass_fields__: ClassVar[dict[str, dataclasses.Field[Any]]]
        __dataclass_params__: _DataclassParams


def is_instance(obj: Any) -> bool:
    return bool(dataclasses.is_dataclass(obj))


def asdict(obj: Any) -> dict[str, Any]:
    return dataclasses.asdict(obj)


def astuple(obj: Any) -> tuple[Any, ...]:
    return dataclasses.astuple(obj)


def replace(obj: Any, /, **changes: Any) -> Any:
    """Return a copy of obj with the specified changes."""
    return dataclasses.replace(obj, **changes)


def fields(obj: Any | type[Any]) -> tuple[Field, ...]:
    """Return a tuple of fields for the class or instance."""
    return tuple(
        Field(
            name=f.name,
            type=f.type,
            default=(
                f.default if f.default is not dataclasses.MISSING else Field.MISSING
            ),
            default_factory=(
                f.default_factory if callable(f.default_factory) else Field.MISSING
            ),
            init=f.init,
            repr=f.repr,
            hash=f.hash,
            compare=f.compare,
            metadata=f.metadata,
            native_field=f,
        )
        for f in dataclasses.fields(obj)
    )


def params(obj: Any) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    params: _DataclassParams | None = getattr(obj, "__dataclass_params__", None)
    if params is not None:
        return DataclassParams(
            init=params.init,
            repr=params.repr,
            eq=params.eq,
            order=params.order,
            unsafe_hash=params.unsafe_hash,
            frozen=params.frozen,
        )
    return DataclassParams()  # pragma: no cover
