from __future__ import annotations

import dataclasses
import re
import sys
from typing import TYPE_CHECKING, Any, Iterator, cast, overload

from fieldz._types import (
    Constraints,
    DataclassParams,
    Field,
    _is_annotated_type,
    _parse_annotatedtypes_meta,
)

if TYPE_CHECKING:
    import pydantic
    import pydantic.fields
    from pydantic.v1 import BaseModel as PydanticV1BaseModel
    from typing_extensions import TypeGuard


@overload
def is_pydantic_model(obj: type) -> TypeGuard[type[pydantic.BaseModel]]: ...


@overload
def is_pydantic_model(obj: object) -> TypeGuard[pydantic.BaseModel]: ...


def is_pydantic_model(obj: Any) -> bool:
    """Return True if obj is a pydantic.BaseModel subclass or instance."""
    pydantic = sys.modules.get("pydantic", None)
    pydantic_v1 = sys.modules.get("pydantic.v1", None)
    cls = obj if isinstance(obj, type) else type(obj)
    if pydantic is not None and issubclass(cls, pydantic.BaseModel):
        return True
    elif pydantic_v1 is not None and issubclass(cls, pydantic_v1.BaseModel):
        return True
    elif hasattr(cls, "__pydantic_model__") or hasattr(cls, "__pydantic_fields__"):
        return True
    return False


is_instance = is_pydantic_model


def asdict(obj: pydantic.BaseModel) -> dict[str, Any]:
    # sourcery skip: reintroduce-else

    if hasattr(obj, "__dataclass_params__"):
        return dataclasses.asdict(obj)

    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj.dict()


def astuple(obj: pydantic.BaseModel) -> tuple[Any, ...]:
    return tuple(asdict(obj).values())


def replace(obj: pydantic.BaseModel, /, **changes: Any) -> Any:
    """Return a copy of obj with the specified changes."""
    if hasattr(obj, "__dataclass_params__"):
        return dataclasses.replace(obj, **changes)

    if hasattr(obj, "model_copy"):
        return obj.model_copy(update=changes)
    return obj.copy(update=changes)


def _fields_v1(obj: PydanticV1BaseModel | type[PydanticV1BaseModel]) -> Iterator[Field]:
    try:
        from pydantic.v1.fields import Undefined
    except ImportError:
        from pydantic.fields import Undefined  # type: ignore

    annotations = {key: field.annotation for key, field in obj.__fields__.items()}
    for name, modelfield in obj.__fields__.items():
        factory = (
            modelfield.default_factory
            if callable(modelfield.default_factory)
            else Field.MISSING
        )
        default = (
            Field.MISSING
            if factory is not Field.MISSING
            or modelfield.default in (Undefined, Ellipsis)
            else modelfield.default
        )
        # backport from pydantic2
        _extra_dict = modelfield.field_info.extra.copy()
        if "json_schema_extra" in _extra_dict:
            _extra_dict.update(_extra_dict.pop("json_schema_extra"))

        yield Field(
            name=name,
            type=annotations.get(name),  # rather than outer_type_
            default=default,
            default_factory=(factory if callable(factory) else Field.MISSING),
            native_field=modelfield,
            description=modelfield.field_info.description,
            metadata=_extra_dict,
            constraints=_constraints_v1(modelfield),
        )


def _constraints_v1(modelfield: Any) -> Constraints | None:
    kwargs = {}
    if not hasattr(modelfield.type_, "__mro__"):
        return None
    # check if the type is a pydantic constrained type
    for subt in modelfield.type_.__mro__:
        if (subt.__module__ or "").startswith("pydantic.types"):
            keys = (
                "gt",
                "ge",
                "lt",
                "le",
                "multiple_of",
                "max_digits",
                "decimal_places",
                "min_length",
                "max_length",
            )
            kwargs.update({key: getattr(modelfield.type_, key, None) for key in keys})
            if regex := getattr(modelfield.type_, "regex", None):
                if isinstance(regex, re.Pattern):
                    regex = regex.pattern
                kwargs["pattern"] = regex
    return Constraints(**kwargs) if kwargs else None


def _fields_v2(obj: pydantic.BaseModel | type[pydantic.BaseModel]) -> Iterator[Field]:
    from pydantic_core import PydanticUndefined

    if hasattr(obj, "__pydantic_fields__"):  # v2 dataclass
        _fields = obj.__pydantic_fields__.items()
    else:
        _fields = obj.model_fields.items()

    annotations = getattr(obj, "__annotations__", {})
    for name, finfo in _fields:
        factory = (
            finfo.default_factory if callable(finfo.default_factory) else Field.MISSING
        )
        default = (
            Field.MISSING
            if finfo.default in (PydanticUndefined, Ellipsis)
            else finfo.default
        )
        extra = finfo.json_schema_extra

        annotated_type = annotations.get(name)
        if not _is_annotated_type(annotated_type):
            annotated_type = None

        c = _parse_annotatedtypes_meta(finfo.metadata)
        constraints = Constraints(**c) if c else None

        yield Field(
            name=name,
            type=finfo.annotation,
            default=default,
            default_factory=factory,
            native_field=finfo,
            description=finfo.description,
            metadata=extra if isinstance(extra, dict) else {},
            annotated_type=annotated_type,
            constraints=constraints,
        )


def fields(
    obj: pydantic.BaseModel
    | PydanticV1BaseModel
    | type[pydantic.BaseModel]
    | type[PydanticV1BaseModel],
) -> tuple[Field, ...]:
    if hasattr(obj, "model_fields") or hasattr(obj, "__pydantic_fields__"):
        obj = cast("pydantic.BaseModel | type[pydantic.BaseModel]", obj)
        return tuple(_fields_v2(obj))
    if hasattr(obj, "__pydantic_model__"):
        obj = obj.__pydantic_model__  # v1 dataclass
    obj = cast("PydanticV1BaseModel | type[PydanticV1BaseModel]", obj)
    return tuple(_fields_v1(obj))


def params(obj: pydantic.BaseModel) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    if hasattr(obj, "__dataclass_params__"):
        p = obj.__dataclass_params__
        return DataclassParams(
            frozen=p.frozen,
            init=p.init,
            repr=p.repr,
            eq=p.eq,
            order=p.order,
            unsafe_hash=p.unsafe_hash,
        )
    if hasattr(obj, "model_config"):
        cfg_dict: pydantic.ConfigDict = obj.model_config
        return DataclassParams(
            # unsafe_hash=not cfg.get("frozen", False),
            frozen=cfg_dict.get("frozen", False)
        )
    else:
        cfg = obj.__config__  # type: ignore
        return DataclassParams(frozen=cfg.allow_mutation is False)
    return DataclassParams()  # pragma: no cover
