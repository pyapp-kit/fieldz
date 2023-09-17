from __future__ import annotations

import dataclasses
from typing import Any, Callable, ClassVar, Generic, Mapping, TypeVar

_T = TypeVar("_T")


@dataclasses.dataclass
class Field(Generic[_T]):
    name: str
    type: type[_T] | None = None
    description: str | None = None
    default: _T | dataclasses._MISSING_TYPE = dataclasses.field(
        default_factory=lambda: dataclasses.MISSING
    )
    default_factory: Callable[[], _T] | dataclasses._MISSING_TYPE = dataclasses.field(
        default_factory=lambda: dataclasses.MISSING
    )
    repr: bool = True
    hash: bool | None = None
    init: bool = True
    compare: bool = True
    metadata: Mapping[Any, Any] = dataclasses.field(default_factory=dict)
    kw_only: bool = False
    # extra
    frozen: bool = False
    native_field: Any | None = dataclasses.field(
        default=None, compare=False, hash=False
    )

    MISSING: ClassVar[dataclasses._MISSING_TYPE] = dataclasses.MISSING


@dataclasses.dataclass
class DataclassParams:
    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False
