import dataclasses
from typing import Callable

import pytest
from dataclass_compat import asdict, astuple, fields, params, replace


def _dataclassy_model() -> type:
    import dataclassy

    @dataclassy.dataclass
    class Model:
        a: int = 0
        b: str = "b"
        c: float = 0.0
        d: bool = False
        e: list[int] = []  # noqa

    return Model


def _dataclass_model() -> type:
    @dataclasses.dataclass
    class Model:
        a: int = 0
        b: str = "b"
        c: float = 0.0
        d: bool = False
        e: list[int] = dataclasses.field(default_factory=list)

    return Model


def _pydantic_model() -> type:
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        a: int = 0
        b: str = "b"
        c: float = 0.0
        d: bool = False
        e: list[int] = Field(default_factory=list)

    return Model


def _attrs_model() -> type:
    import attr

    @attr.define
    class Model:
        a: int = attr.field(default=0)
        b: str = attr.field(default="b")
        c: float = attr.field(default=0.0)
        d: bool = attr.field(default=False)
        e: list[int] = attr.field(default=attr.Factory(list))

    return Model


def _msgspec_model() -> type:
    import msgspec

    class Model(msgspec.Struct):
        a: int = msgspec.field(default=0)
        b: str = msgspec.field(default="b")
        c: float = msgspec.field(default=0.0)
        d: bool = msgspec.field(default=False)
        e: list[int] = msgspec.field(default_factory=list)

    return Model


@pytest.mark.parametrize(
    "builder",
    [
        _dataclass_model,
        _dataclassy_model,
        _pydantic_model,
        _attrs_model,
        _msgspec_model,
    ],
)
def test_adapters(builder: Callable) -> None:
    model = builder()
    obj = model()
    assert asdict(obj) == {"a": 0, "b": "b", "c": 0.0, "d": False, "e": []}
    assert astuple(obj) == (0, "b", 0.0, False, [])
    fields_ = fields(obj)
    assert [f.name for f in fields_] == ["a", "b", "c", "d", "e"]
    assert [f.type for f in fields_] == [int, str, float, bool, list[int]]
    assert [f.default for f in fields_] == [0, "b", 0.0, False, dataclasses.MISSING]
    assert [f.default_factory for f in fields_] == [dataclasses.MISSING] * 4 + [list]

    obj2 = replace(obj, a=1, b="b2", c=1.0, d=True, e=[1, 2, 3])
    assert asdict(obj2) == {"a": 1, "b": "b2", "c": 1.0, "d": True, "e": [1, 2, 3]}

    p = params(obj)
    assert p.eq is True
    assert p.order is False
    assert p.repr is True
    assert p.init is True
    assert p.unsafe_hash is False
    assert p.frozen is False
