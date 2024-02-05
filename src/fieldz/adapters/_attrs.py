from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, cast, overload

from fieldz._types import DataclassParams, Field

if TYPE_CHECKING:
    import attrs
    from typing_extensions import TypeGuard

    class AttrsInstance(Protocol):
        __attrs_attrs__: ClassVar[tuple[attrs.Attribute, ...]]


@overload
def is_attrs_class(obj: type) -> TypeGuard[type[AttrsInstance]]: ...


@overload
def is_attrs_class(obj: object) -> TypeGuard[AttrsInstance]: ...


def is_attrs_class(obj: object) -> bool:
    """Return True if the class is an attrs class."""
    attr = sys.modules.get("attr", None)
    cls = obj if isinstance(obj, type) else type(obj)
    return attr.has(cls) if attr is not None else False  # type: ignore [no-any-return]


is_instance = is_attrs_class


def asdict(obj: AttrsInstance) -> dict[str, Any]:
    import attrs

    return attrs.asdict(obj)


def astuple(obj: AttrsInstance) -> tuple[Any, ...]:
    import attrs

    return attrs.astuple(obj)


def replace(obj: AttrsInstance, /, **changes: Any) -> AttrsInstance:
    """Return a copy of obj with the specified changes."""
    import attrs

    return attrs.evolve(obj, **changes)  # type: ignore [misc]


def fields(class_or_instance: Any | type) -> tuple[Field, ...]:
    import attrs

    cls = (
        class_or_instance
        if isinstance(class_or_instance, type)
        else type(class_or_instance)
    )
    fields: list[Field] = []
    for f in attrs.fields(cls):
        f = cast(attrs.Attribute, f)
        default = Field.MISSING if f.default is attrs.NOTHING else f.default
        default_factory = Field.MISSING
        if isinstance(default, attrs.Factory):  # type: ignore [arg-type]
            default_factory, default = default.factory, Field.MISSING
        fields.append(
            Field(
                name=f.name,
                type=f.type,
                default=default,
                default_factory=default_factory,
                repr=f.repr,
                init=f.init,
                compare=f.eq,
                kw_only=f.kw_only,
                hash=f.hash,
                native_field=f,
                metadata=f.metadata,
            )
        )

    return tuple(fields)


def params(obj: AttrsInstance) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    cls = obj if isinstance(obj, type) else type(obj)

    return DataclassParams(
        frozen=getattr(cls.__setattr__, "__name__", None) == "_frozen_setattrs"
    )
