import dataclasses
from typing import Callable, List, NamedTuple, Optional, TypedDict, Any

import pytest
from fieldz import Field, asdict, astuple, fields, params, replace
from fieldz.adapters._named_tuple import is_named_tuple

def _dataclass_model() -> type:
    @dataclasses.dataclass
    class Model:
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = dataclasses.field(default_factory=list)
        f: Any = ()

    return Model


def _named_tuple() -> type:
    class Model(NamedTuple):
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = []  # noqa
        f: Any = ()

    return Model

def _pydantic_v1_model() -> type:
    from pydantic.v1 import BaseModel, Field

    class Model(BaseModel):
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = Field(default_factory=list)
        f: Any = ()

    return Model

def _pydantic_model() -> type:
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = Field(default_factory=list)
        f: Any = ()

    return Model


def _pydantic_dataclass() -> type:
    from pydantic.dataclasses import dataclass

    @dataclass
    class Model:
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = dataclasses.field(default_factory=list)
        f: Any = ()

    return Model


def _sqlmodel() -> type:
    pytest.importorskip("sqlmodel")
    from sqlmodel import Field, SQLModel

    class Model(SQLModel):
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = Field(default_factory=list)
        f: Any = ()

    return Model


def _attrs_model() -> type:
    import attr

    @attr.define
    class Model:
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = attr.field(default=attr.Factory(list))
        f: Any = ()

    return Model


def _msgspec_model() -> type:
    import msgspec

    class Model(msgspec.Struct):
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = msgspec.field(default_factory=list)
        f: Any = ()

    return Model


def _dataclassy_model() -> type:
    import dataclassy

    @dataclassy.dataclass
    class Model:
        a: int = 0
        b: Optional[str] = None
        c: float = 0.0
        d: bool = False
        e: List[int] = []  # noqa
        f: Any = ()

    return Model


def _django_model() -> type:
    from django.db import models

    class Model(models.Model):
        a: int = models.IntegerField(default=0)
        b: str = models.CharField(default="b", max_length=255)
        c: float = models.FloatField(default=0.0)
        d: bool = models.BooleanField(default=False)
        e: List[int] = models.JSONField(default=list)
        f: Any = ()

    return Model


@pytest.mark.parametrize(
    "builder",
    [
        _dataclass_model,
        _named_tuple,
        _dataclassy_model,
        _pydantic_model,
        _pydantic_model,
        _attrs_model,
        _msgspec_model,
        _sqlmodel,
        _pydantic_dataclass,
        # _django_model,
    ],
)
def test_adapters(builder: Callable) -> None:
    model = builder()
    obj = model()
    assert asdict(obj) == {"a": 0, "b": None, "c": 0.0, "d": False, "e": [], "f": ()}
    assert astuple(obj) == (0, None, 0.0, False, [], ())
    fields_ = fields(obj)
    assert [f.name for f in fields_] == ["a", "b", "c", "d", "e", "f"]
    assert [f.type for f in fields_] == [int, Optional[str], float, bool, List[int], Any]
    assert [f.frozen for f in fields_] == [False] * 6
    if is_named_tuple(obj):
        assert [f.default for f in fields_] == [0, None, 0.0, False, [], ()]
    else:
        # namedtuples don't have default_factory
        assert [f.default for f in fields_] == [
            0,
            None,
            0.0,
            False,
            Field.MISSING,
            ()
        ]
        assert [f.default_factory for f in fields_] == [
            *[Field.MISSING] * 4,
            list,
            Field.MISSING
        ]

    obj2 = replace(obj, a=1, b="b2", c=1.0, d=True, e=[1, 2, 3], f={})
    assert asdict(obj2) == {"a": 1, "b": "b2", "c": 1.0, "d": True, "e": [1, 2, 3], "f": {}}

    p = params(obj)
    assert p.eq is True
    assert p.order is False
    assert p.repr is True
    assert p.init is True
    assert p.unsafe_hash is False
    assert p.frozen is False


def test_typed_dict() -> None:
    class Model(TypedDict):
        a: int
        b: Optional[str]
        c: float
        d: bool
        e: List[int]

    assert fields(Model) == (
        Field(name="a", type=int),
        Field(name="b", type=Optional[str]),
        Field(name="c", type=float),
        Field(name="d", type=bool),
        Field(name="e", type=List[int]),
    )
