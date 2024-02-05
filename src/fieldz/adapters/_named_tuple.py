from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from fieldz._types import DataclassParams, Field

if TYPE_CHECKING:
    from typing import Iterable

    from typing_extensions import Self, TypeGuard

    class NamedTupleInstance(tuple[Any, ...]):
        _field_defaults: ClassVar[dict[str, Any]]
        _fields: ClassVar[tuple[str, ...]]

        @classmethod
        def _make(cls, iterable: Iterable[Any]) -> Self: ...

        def _asdict(self) -> dict[str, Any]: ...

        def _replace(self, **kwargs: Any) -> Self: ...


def is_named_tuple(obj: Any) -> TypeGuard[NamedTupleInstance]:
    cls = obj if isinstance(obj, type) else type(obj)
    return (
        hasattr(cls, "_fields")
        and hasattr(cls, "_field_defaults")
        and hasattr(cls, "_make")
    )


is_instance = is_named_tuple


def asdict(obj: NamedTupleInstance) -> dict[str, Any]:
    return obj._asdict()


def astuple(obj: NamedTupleInstance) -> tuple[Any, ...]:
    return obj


def replace(obj: NamedTupleInstance, /, **changes: Any) -> NamedTupleInstance:
    """Return a copy of obj with the specified changes."""
    return obj._replace(**changes)


def fields(obj: NamedTupleInstance | type[NamedTupleInstance]) -> tuple[Field, ...]:
    """Return a tuple of fields for the class or instance."""
    annotations = getattr(obj, "__annotations__", {})
    defaults = getattr(obj, "_field_defaults", {})
    return tuple(
        Field(name=name, type=annotations.get(name, Any), default=defaults.get(name))
        for name in obj._fields
    )


def params(obj: Any) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    return DataclassParams()
