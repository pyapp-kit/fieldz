from __future__ import annotations

import dataclasses
import enum
import sys
from typing import Any, Callable, ClassVar, Generic, Literal, Mapping, TypeVar

_T = TypeVar("_T")

DC_KWARGS = {"frozen": True}
if sys.version_info >= (3, 10):
    DC_KWARGS["slots"] = True
    if sys.version_info >= (3, 10, 1):
        DC_KWARGS["weakref_slot"] = True


class _MISSING_TYPE(enum.Enum):
    MISSING = enum.auto()


@dataclasses.dataclass(**DC_KWARGS)
class Field(Generic[_T]):
    MISSING: ClassVar[Literal[_MISSING_TYPE.MISSING]] = _MISSING_TYPE.MISSING

    name: str
    type: type[_T] | None = None
    description: str | None = None
    default: _T | Literal[_MISSING_TYPE.MISSING] = MISSING
    default_factory: Callable[[], _T] | Literal[_MISSING_TYPE.MISSING] = MISSING
    repr: bool = True
    hash: bool | None = None
    init: bool = True
    compare: bool = True
    metadata: Mapping[Any, Any] = dataclasses.field(default_factory=dict)
    kw_only: bool = False
    # extra
    frozen: bool = False
    native_field: Any | None = dataclasses.field(default=None, compare=False)


@dataclasses.dataclass(**DC_KWARGS)
class DataclassParams:
    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False
