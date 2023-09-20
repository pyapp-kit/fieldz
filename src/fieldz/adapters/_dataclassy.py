from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, ClassVar, Protocol

from fieldz._types import DataclassParams, Field

if TYPE_CHECKING:
    from typing_extensions import TypedDict, TypeGuard

    class DataclassyParams(TypedDict):
        init: bool
        repr: bool
        eq: bool
        order: bool
        unsafe_hash: bool
        frozen: bool
        kw_only: bool
        match_args: bool
        hide_internals: bool
        iter: bool
        kwargs: bool
        slots: bool

    class DataclassyInstance(Protocol):
        __dataclass__: ClassVar[DataclassyParams]


def is_instance(obj: Any) -> TypeGuard[DataclassyInstance | type[DataclassyInstance]]:
    if TYPE_CHECKING:
        from dataclassy import functions
    else:
        functions = sys.modules.get("dataclassy.functions", None)

    return False if functions is None else functions.is_dataclass(obj)


def asdict(obj: Any) -> dict[str, Any]:
    import dataclassy

    return dataclassy.as_dict(obj)


def astuple(obj: Any) -> tuple[Any, ...]:
    import dataclassy

    return dataclassy.as_tuple(obj)


def replace(obj: Any, /, **changes: Any) -> Any:
    """Return a copy of obj with the specified changes."""
    import dataclassy

    return dataclassy.replace(obj, **changes)


def fields(obj: Any | type) -> tuple:
    import dataclassy

    defaults = getattr(obj, "__defaults__", None) or getattr(obj, "__dict__", {})
    fields = []
    for name, type_ in dataclassy.fields(obj).items():
        default = defaults.get(name, Field.MISSING)
        default_factory: Any = Field.MISSING
        # this is just how dataclassy does it... (you can assign a mutable default)
        # but, to match the other adapters, we perform a little checking to
        # normalize common cases to a "typical" default_factory
        if hasattr(default, "copy") and callable(default.copy):
            if default == []:
                default_factory = list
            elif default == {}:
                default_factory = dict
            elif default == ():
                default_factory = tuple
            elif default == set():
                default_factory = set
            else:
                # the general fallback case
                default_factory = default.copy
            default = Field.MISSING

        fields.append(
            Field(
                name=name,
                type=type_,
                default=default,
                default_factory=default_factory,
            )
        )
    return tuple(fields)


def params(obj: Any) -> DataclassParams:
    """Return parameters used to define the dataclass."""
    params: DataclassyParams | None = getattr(obj, "__dataclass__", None)

    if params is not None:
        return DataclassParams(
            init=params["init"],
            repr=params["repr"],
            eq=params["eq"],
            order=params["order"],
            unsafe_hash=params["unsafe_hash"],
            frozen=params["frozen"],
        )
    return DataclassParams()  # pragma: no cover
