from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, overload

from fieldz._types import DataclassParams, Field

if TYPE_CHECKING:
    import msgspec
    from typing_extensions import TypeGuard


@overload
def is_msgspec_struct(obj: type) -> TypeGuard[type[msgspec.Struct]]: ...


@overload
def is_msgspec_struct(obj: object) -> TypeGuard[msgspec.Struct]: ...


def is_msgspec_struct(obj: Any) -> bool:
    """Return True if the class is a `msgspec.Struct`."""
    msgspec = sys.modules.get("msgspec", None)
    cls = obj if isinstance(obj, type) else type(obj)
    return msgspec is not None and issubclass(cls, msgspec.Struct)


is_instance = is_msgspec_struct


def asdict(obj: msgspec.Struct) -> dict[str, Any]:
    import msgspec.structs

    return msgspec.structs.asdict(obj)


def astuple(obj: msgspec.Struct) -> tuple[Any, ...]:
    import msgspec.structs

    return msgspec.structs.astuple(obj)


def replace(obj: msgspec.Struct, /, **changes: Any) -> Any:
    """Return a copy of obj with the specified changes."""
    import msgspec.structs

    return msgspec.structs.replace(obj, **changes)


def fields(obj: msgspec.Struct | type[msgspec.Struct]) -> tuple:
    import msgspec

    return tuple(
        Field(
            name=f.name,
            type=f.type,
            default=(Field.MISSING if f.default is msgspec.NODEFAULT else f.default),
            default_factory=(
                Field.MISSING
                if f.default_factory is msgspec.NODEFAULT
                else f.default_factory
            ),
            native_field=f,
        )
        for f in msgspec.structs.fields(obj)
    )


def params(obj: msgspec.Struct) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    cfg: msgspec.structs.StructConfig | None = getattr(obj, "__struct_config__", None)
    if cfg is None:
        return DataclassParams()  # pragma: no cover

    # this will be covered in msgspec > 0.13.1
    return DataclassParams(
        frozen=cfg.frozen, eq=cfg.eq, order=cfg.order, init=True, repr=True
    )
