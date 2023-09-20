from __future__ import annotations

import dataclasses
import enum
import sys
import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Literal,
    Mapping,
    TypeVar,
)

# python 3.8's `get_origin` is not Annotated-aware
from typing_extensions import Annotated, get_args, get_origin

from fieldz._repr import PlainRepr

if TYPE_CHECKING:
    import builtins

    from typing_extensions import Self

_T = TypeVar("_T")

DC_KWARGS = {"frozen": True}
if sys.version_info >= (3, 10):
    DC_KWARGS["slots"] = True


class _MISSING_TYPE(enum.Enum):
    MISSING = "MISSING"

    def __repr__(self) -> str:
        return self.value


@dataclasses.dataclass(**DC_KWARGS)
class DataclassParams:
    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False


@dataclasses.dataclass(**DC_KWARGS)
class Constraints:
    gt: int | float | None = None
    ge: int | float | None = None
    lt: int | float | None = None
    le: int | float | None = None
    multiple_of: int | float | None = None
    min_length: int | None = None  # for str
    max_length: int | None = None  # for str
    max_digits: int | None = None  # for decimal
    decimal_places: int | None = None  # for decimal
    pattern: str | None = None
    deprecated: bool | None = None
    tz: bool | None = None
    predicate: Callable[[Any], bool] | None = None
    # enum: list[Any] | None = None
    # const: Any | None = None

    def __rich_repr__(self) -> Iterable[tuple[str, Any]]:
        for name, val in dataclasses.asdict(self).items():
            if val is not None:
                yield name, val


@dataclasses.dataclass(**DC_KWARGS)
class Field(Generic[_T]):
    MISSING: ClassVar[Literal[_MISSING_TYPE.MISSING]] = _MISSING_TYPE.MISSING

    name: str
    type: type[_T] | None = None
    description: str | None = None
    title: str | None = None
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
    native_field: Any | None = dataclasses.field(
        default=None, compare=False, repr=False
    )
    constraints: Constraints | None = None

    # populated during parse_annotated
    annotated_type: builtins.type[_T] | None = dataclasses.field(
        default=None, repr=False, compare=False
    )

    def __rich_repr__(self) -> Iterable[tuple[str, Any]]:
        for f in dataclasses.fields(self):
            if not f.repr:
                continue
            val = getattr(self, f.name)
            if f.name == "type":
                val = PlainRepr.for_type(val)
            elif f.name in {"default_factory", "default"} and val is Field.MISSING:
                continue
            yield f.name, val

    def parse_annotated(self) -> Self:
        """Extract info from Annotated type if present, and return new field.

        If `self.type` is not a `typing.Annotated` type, return self unchanged.
        """
        if not _is_annotated_type(self.type):
            return self

        kwargs, constraints = _parse_annotated_hint(self.type)

        for key in ("default", "name"):
            if (val := getattr(self, key)) not in (Field.MISSING, None) and kwargs.get(
                key
            ) not in (Field.MISSING, None):
                warnings.warn(  # pragma: no cover
                    f"Cannot set {key!r} in both type annotation and field. Overriding "
                    f"{key!r}={kwargs[key]!r} with {val!r}.",
                    stacklevel=2,
                )

        if self.constraints is not None:
            kwargs["constraints"] = dataclasses.replace(self.constraints, **constraints)
        elif constraints:
            kwargs["constraints"] = Constraints(**constraints)

        return dataclasses.replace(self, **kwargs)


def _parse_annotated_hint(hint: Any) -> tuple[dict, dict]:
    """Convert an Annotated type to a dict of Field kwargs."""
    # hint should have been checked to be an Annotated[...] type
    origin, *metadata = get_args(hint)
    kwargs: dict[str, Any] = {"type": origin, "annotated_type": hint}
    constraints: dict[str, Any] = {}

    # deal with annotated_types
    constraints.update(_parse_annotatedtypes_meta(metadata))

    # deal with msgspec
    m_kwargs, m_constraints = _parse_msgspec_meta(metadata)
    kwargs.update(m_kwargs)
    constraints.update(m_constraints)

    # TODO: support pydantic.fields.FieldInfo?
    # TODO: support re.Pattern?
    # TODO: support msgspec
    return kwargs, constraints


# At the moment, all of our constraint names match msgspec.Meta attributes
# (we are a superset of msgspec.Meta)
CONSTRAINT_NAMES = {f.name for f in dataclasses.fields(Constraints)}
FIELD_NAMES = {f.name for f in dataclasses.fields(Field)}


def _parse_annotatedtypes_meta(metadata: list[Any]) -> dict[str, Any]:
    """Extract constraints from annotated_types metadata."""
    if TYPE_CHECKING:
        import annotated_types as at
    else:
        at = sys.modules.get("annotated_types")
        if at is None:
            return {}  # pragma: no cover

    a_kwargs = {}
    for item in metadata:
        # annotated_types >= 0.3.0 is supported
        if isinstance(item, (at.BaseMetadata, at.GroupedMetadata)):
            values = {k: getattr(item, k) for k in CONSTRAINT_NAMES if hasattr(item, k)}
            a_kwargs.update(values)
            # annotated types calls the value of a Predicate "func"
            if hasattr(item, "func"):
                a_kwargs["predicate"] = item.func

            # these were changed in v0.4.0
            if hasattr(item, "min_inclusive"):  # pragma: no cover
                a_kwargs["min_length"] = item.min_inclusive
            if hasattr(item, "max_exclusive"):  # pragma: no cover
                a_kwargs["max_length"] = item.max_exclusive - 1
    return a_kwargs


def _parse_msgspec_meta(metadata: list[Any]) -> tuple[dict, dict]:
    """Extract constraints from msgspec.Meta metadata."""
    if TYPE_CHECKING:
        import msgspec
    else:
        msgspec = sys.modules.get("msgspec")
        if msgspec is None:
            return {}, {}

    field_kwargs = {}
    constraints = {}
    for item in metadata:
        if isinstance(item, msgspec.Meta):
            constraints.update(
                {
                    k: val
                    for k in CONSTRAINT_NAMES
                    if (val := getattr(item, k, None)) is not None
                }
            )
            field_kwargs.update(
                {
                    k: val
                    for k in FIELD_NAMES
                    if (val := getattr(item, k, None)) is not None
                }
            )

    return field_kwargs, constraints


def _is_annotated_type(hint: Any) -> bool:
    """Whether the field is an Annotated type."""
    return get_origin(hint) is Annotated


def _is_classvar(a_type: Any) -> bool:
    return a_type is ClassVar or get_origin(a_type) is ClassVar


def _is_initvar(a_type: Any) -> bool:
    return a_type is dataclasses.InitVar or type(a_type) is dataclasses.InitVar
