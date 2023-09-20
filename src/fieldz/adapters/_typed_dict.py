from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fieldz._types import DataclassParams, Field, _is_classvar

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


def is_typed_dict(obj: Any) -> TypeGuard[dict]:
    # NOTE: this will ONLY work on TypedDict subclasses, not instances
    # because at runtime, TypedDict instances are simply dicts, and there's no way
    # to tell if a dict is an instance of a TypedDict subclass

    # in python 3.8 the only difference between a TypedDict subclass and a dict is:
    # - __dict__
    # - __weakref__
    # - __module__
    # - __total__
    # - __annotations_
    # ... here we choose to check for __total__ and __annotations__
    # (since most things will have __dict__, __module__, __weakref__)
    # later versions also have __required_keys__ and __optional_keys__
    return (
        isinstance(obj, type)
        and issubclass(obj, dict)
        and hasattr(obj, "__annotations__")
        and hasattr(obj, "__total__")
    )


is_instance = is_typed_dict


def asdict(obj: dict) -> dict[str, Any]:
    return obj


def astuple(obj: dict) -> tuple[Any, ...]:
    return tuple(obj.values())


def replace(obj: dict, /, **changes: Any) -> dict:
    """Return a copy of obj with the specified changes."""
    return {**obj, **changes}


def fields(obj: dict | type[dict]) -> tuple[Field, ...]:
    """Return a tuple of fields for the class or instance."""
    return tuple(
        Field(name=name, type=hint)
        for name, hint in getattr(obj, "__annotations__", {}).items()
        if not _is_classvar(hint)
    )


def params(obj: dict) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    return DataclassParams()
