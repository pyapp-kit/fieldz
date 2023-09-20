from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import adapters

if TYPE_CHECKING:
    from ._types import DataclassParams, Field


def asdict(obj: Any) -> dict[str, Any]:
    """Return a dict representation of obj."""
    return get_adapter(obj).asdict(obj)


def astuple(obj: Any) -> tuple[Any, ...]:
    """Return a tuple representation of obj."""
    return get_adapter(obj).astuple(obj)


def replace(obj: Any, /, **changes: Any) -> Any:
    """Return a copy of obj with the specified changes."""
    return get_adapter(obj).replace(obj, **changes)


def fields(obj: Any | type[Any], *, parse_annotated: bool = True) -> tuple[Field, ...]:
    """Return a tuple of fields for the class or instance."""
    fields = get_adapter(obj).fields(obj)
    if parse_annotated:
        fields = tuple(field.parse_annotated() for field in fields)
    return fields


def params(obj: Any) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    return get_adapter(obj).params(obj)


# Order matters here. The first adapter to return True for is_instance will be used.
ADAPTERS: tuple[adapters.Adapter, ...] = (
    adapters._pydantic,
    adapters._attrs,
    adapters._msgspec,
    adapters._dataclassy,
    adapters._dataclasses,
    adapters._named_tuple,
    adapters._typed_dict,
)


def get_adapter(obj: Any) -> adapters.Adapter:
    """Return the module of the given object."""
    for mod in ADAPTERS:
        if mod.is_instance(obj):
            return mod
    raise TypeError(f"Unsupported dataclass type: {type(obj)}")  # pragma: no cover
