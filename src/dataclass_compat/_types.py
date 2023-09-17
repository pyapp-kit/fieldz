from __future__ import annotations

import dataclasses
import enum
import sys
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ClassVar,
    Generic,
    Literal,
    Mapping,
    TypeVar,
    get_args,
    get_origin,
)

_T = TypeVar("_T")

DC_KWARGS = {"frozen": True}
if sys.version_info >= (3, 10):
    DC_KWARGS["slots"] = True


class _MISSING_TYPE(enum.Enum):
    MISSING = enum.auto()


class Restrictions:
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None
    multiple_of: float | None = None
    min_length: int | None = None  # for str
    max_length: int | None = None  # for str
    pattern: str | None = None
    # min_items: int | None = None  # for sequences
    # max_items: int | None = None  # for sequences
    # unique_items: bool | None = None  # i.e. set
    # min_properties: int | None = None
    # max_properties: int | None = None
    # required: bool | None = None
    enum: list[Any] | None = None
    const: Any | None = None
    # format: str | None = None
    # nullable: bool | None = None
    deprecated: bool | None = None


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
    restrictions: Restrictions | None = None


@dataclasses.dataclass(**DC_KWARGS)
class DataclassParams:
    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False


def reduce_annotated(hint: Any) -> dict[str, Any]:
    """Convert an Annotated type to a dict of UiField kwargs."""
    # hint must be an Annotated[...] type
    if TYPE_CHECKING:
        import annotated_types
    else:
        annotated_types = sys.modules.get("annotated_types")
    base_metas: list[annotated_types.BaseMetadata] = []

    origin, *metadata = get_args(hint)
    # TODO: support pydantic.fields.FieldInfo?
    # TODO: support re.Pattern?
    kwargs = {}
    if annotated_types is not None:
        for item in metadata:
            # annotated_types >= 0.3.0 is supported
            if isinstance(item, annotated_types.BaseMetadata):
                base_metas.append(item)
            elif isinstance(item, annotated_types.GroupedMetadata):
                base_metas.extend(item)

    if base_metas:
        _annotated_kwargs = {}
        for i in base_metas:
            _annotated_kwargs.update(dataclasses.asdict(i))  # type: ignore
        if "max_exclusive" in _annotated_kwargs:
            _annotated_kwargs["max_items"] = _annotated_kwargs.pop("max_exclusive") - 1
        kwargs.update(_annotated_kwargs)

    kwargs.update({"type": origin, "_original_annotation": hint})
    return kwargs


def _is_annotated_type(hint: Any) -> bool:
    """Return True the field is an Annotated type."""
    return get_origin(hint) is Annotated
