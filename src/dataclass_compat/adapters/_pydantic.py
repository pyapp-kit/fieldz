from __future__ import annotations

import sys
from dataclasses import MISSING
from typing import TYPE_CHECKING, Any, Callable, overload

from dataclass_compat._types import DataclassParams, Field

if TYPE_CHECKING:
    import dataclasses

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
    return pydantic is not None and issubclass(cls, pydantic.BaseModel)


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
    fields = []
    if hasattr(obj, "model_fields"):
        from pydantic_core import PydanticUndefined

        for name, finfo in obj.model_fields.items():
            factory: Callable | dataclasses._MISSING_TYPE = (
                finfo.default_factory if callable(finfo.default_factory) else MISSING
            )
            default = MISSING if finfo.default is PydanticUndefined else finfo.default
            field = Field(
                name=name,
                type=finfo.annotation,
                default=default,
                default_factory=factory,
            )
            fields.append(field)
    else:
        from pydantic.fields import Undefined  # type: ignore

        for name, modelfield in obj.__fields__.items():  # type: ignore
            factory = (
                modelfield.default_factory
                if callable(modelfield.default_factory)
                else MISSING
            )
            default = (
                MISSING
                if (factory is not MISSING or modelfield.default is Undefined)
                else modelfield.default
            )
            field = Field(
                name=name,
                type=modelfield.outer_type_,  # type: ignore
                default=default,
                default_factory=factory,
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
