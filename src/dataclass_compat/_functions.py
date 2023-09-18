from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .adapters import ADAPTER_MODULES, Adapter

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


def get_adapter(obj: Any) -> Adapter:
    """Return the module of the given object."""
    for mod in ADAPTER_MODULES:
        if mod.is_instance(obj):
            return mod
    raise TypeError(f"Unsupported dataclass type: {type(obj)}")  # pragma: no cover
