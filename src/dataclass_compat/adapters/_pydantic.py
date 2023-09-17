from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, overload

from dataclass_compat._types import DataclassParams, Field

if TYPE_CHECKING:
    import pydantic
    from typing_extensions import TypeGuard


@overload
def is_pydantic_model(obj: type) -> TypeGuard[type[pydantic.BaseModel]]:
    ...


@overload
def is_pydantic_model(obj: object) -> TypeGuard[pydantic.BaseModel]:
    ...


def is_pydantic_model(obj: Any) -> bool:
    """Return True if obj is a pydantic.BaseModel subclass or instance."""
    pydantic = sys.modules.get("pydantic", None)
    cls = obj if isinstance(obj, type) else type(obj)
    if pydantic is not None and issubclass(cls, pydantic.BaseModel):
        return True
    elif hasattr(cls, "__pydantic_model__") or hasattr(cls, "__pydantic_fields__"):
        return True
    return False


is_instance = is_pydantic_model


def asdict(obj: pydantic.BaseModel) -> dict[str, Any]:
    # sourcery skip: reintroduce-else
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj.dict()


def astuple(obj: pydantic.BaseModel) -> tuple[Any, ...]:
    return tuple(asdict(obj).values())


def replace(obj: pydantic.BaseModel, /, **changes: Any) -> Any:
    """Return a copy of obj with the specified changes."""
    if hasattr(obj, "model_copy"):
        return obj.model_copy(update=changes)
    return obj.copy(update=changes)


def fields(obj: pydantic.BaseModel | type[pydantic.BaseModel]) -> tuple[Field, ...]:
    fields: list[Field] = []
    if hasattr(obj, "__pydantic_model__"):
        obj = obj.__pydantic_model__

    if hasattr(obj, "model_fields"):
        from pydantic_core import PydanticUndefined

        for name, finfo in obj.model_fields.items():
            factory = (
                finfo.default_factory
                if callable(finfo.default_factory)
                else Field.MISSING
            )
            default = (
                Field.MISSING
                if finfo.default in (PydanticUndefined, Ellipsis)
                else finfo.default
            )
            extra = finfo.json_schema_extra
            field = Field(
                name=name,
                type=finfo.annotation,
                default=default,
                default_factory=factory,  # type: ignore
                native_field=finfo,
                description=finfo.description,
                metadata=extra if isinstance(extra, dict) else {},
            )
            fields.append(field)
    else:
        from pydantic.fields import Undefined  # type: ignore

        annotations = getattr(obj, "__annotations__", {})
        for name, modelfield in obj.__fields__.items():  # type: ignore
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
            _extra_dict = modelfield.field_info.extra.copy()  # type: ignore
            if "json_schema_extra" in _extra_dict:
                _extra_dict.update(_extra_dict.pop("json_schema_extra"))

            field = Field(
                name=name,
                type=annotations.get(name),  # rather than outer_type_
                default=default,
                default_factory=(factory if callable(factory) else Field.MISSING),
                native_field=modelfield,
                description=modelfield.field_info.description,  # type: ignore
                metadata=_extra_dict,
            )
            fields.append(field)

    return tuple(fields)


def params(obj: pydantic.BaseModel) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    if hasattr(obj, "model_config"):
        cfg_dict: pydantic.ConfigDict = obj.model_config
        return DataclassParams(
            # unsafe_hash=not cfg.get("frozen", False),
            frozen=cfg_dict.get("frozen", False)
        )
    else:
        cfg = obj.__config__  # type: ignore
        return DataclassParams(frozen=cfg.allow_mutation is False)
    return DataclassParams()
