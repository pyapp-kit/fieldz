from __future__ import annotations

import dataclasses
from types import MappingProxyType
from typing import Any, Callable, Generic, TypeVar

_T = TypeVar("_T")


@dataclasses.dataclass
class Field(Generic[_T]):
    name: str
    type: type[_T] | None = None
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
    metadata: MappingProxyType[Any, Any] = dataclasses.field(
        default_factory=lambda: MappingProxyType({})
    )
    kw_only: bool = False
    # extra
    frozen: bool = False
    native_field: Any | None = None


@dataclasses.dataclass
class DataclassParams:
    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False
