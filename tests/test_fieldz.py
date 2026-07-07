import dataclasses
import sys
from collections.abc import Callable
from typing import Any, NamedTuple, Optional, TypedDict

import pytest

from fieldz import Field, asdict, astuple, fields, params, replace
from fieldz.adapters._named_tuple import is_named_tuple

PY314 = sys.version_info >= (3, 14)


def _dataclass_model() -> type:
    @dataclasses.dataclass
    class Model:
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = dataclasses.field(default_factory=list)
        f: Any = ()

    return Model


def _named_tuple() -> type:
    class Model(NamedTuple):
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = []  # noqa: RUF012
        f: Any = ()

    return Model


def _pydantic_v1_model_str() -> type:
    from pydantic.v1 import BaseModel, Field

    class Model(BaseModel):
        required: "int"
        a: "int" = 0
        b: "str | None" = None
        c: "float" = 0.0
        d: "bool" = False
        e: "list[int]" = Field(default_factory=list)
        f: "Any" = ()

    return Model


def _pydantic_v1_model() -> type:
    from pydantic.v1 import BaseModel, Field

    class Model(BaseModel):
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = Field(default_factory=list)
        f: Any = ()

    return Model


def _pydantic_model() -> type:
    from pydantic import BaseModel, Field

    class Model(BaseModel):
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = Field(default_factory=list)
        f: Any = ()

    return Model


def _pydantic_dataclass() -> type:
    from pydantic.dataclasses import dataclass

    @dataclass
    class Model:
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = dataclasses.field(default_factory=list)
        f: Any = ()

    return Model


def _sqlmodel() -> type:
    pytest.importorskip("sqlmodel")
    from sqlmodel import Field, SQLModel

    class Model(SQLModel):
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = Field(default_factory=list)
        f: Any = ()

    return Model


def _attrs_model() -> type:
    import attr

    @attr.define
    class Model:
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = attr.field(default=attr.Factory(list))
        f: Any = ()

    return Model


def _msgspec_model() -> type:
    import msgspec

    class Model(msgspec.Struct):
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = msgspec.field(default_factory=list)
        f: Any = ()

    return Model


def _dataclassy_model() -> type:
    import dataclassy

    @dataclassy.dataclass
    class Model:
        required: int
        a: int = 0
        b: str | None = None
        c: float = 0.0
        d: bool = False
        e: list[int] = []  # noqa: RUF012
        f: Any = ()

    return Model


def _django_model() -> type:
    from django.db import models

    class Model(models.Model):
        required: int = models.IntegerField()
        a: int = models.IntegerField(default=0)
        b: str = models.CharField(default="b", max_length=255)
        c: float = models.FloatField(default=0.0)
        d: bool = models.BooleanField(default=False)
        e: list[int] = models.JSONField(default=list)
        f: Any = ()

    return Model


@pytest.mark.parametrize(
    "builder",
    [
        _dataclass_model,
        _named_tuple,
        pytest.param(
            _dataclassy_model,
            marks=pytest.mark.skipif(PY314, reason="dataclassy broken on 3.14"),
        ),
        _pydantic_model,
        pytest.param(
            _pydantic_v1_model,
            marks=pytest.mark.skipif(
                PY314, reason="pydantic v1 incompatible with 3.14"
            ),
        ),
        pytest.param(
            _pydantic_v1_model_str,
            marks=pytest.mark.skipif(
                PY314, reason="pydantic v1 incompatible with 3.14"
            ),
        ),
        _attrs_model,
        _msgspec_model,
        _sqlmodel,
        _pydantic_dataclass,
        # _django_model,
    ],
)
def test_adapters(builder: Callable) -> None:
    model = builder()
    obj = model(required=0)
    assert asdict(obj) == {
        "required": 0,
        "a": 0,
        "b": None,
        "c": 0.0,
        "d": False,
        "e": [],
        "f": (),
    }
    assert astuple(obj) == (0, 0, None, 0.0, False, [], ())
    fields_ = fields(obj)
    assert [f.name for f in fields_] == ["required", "a", "b", "c", "d", "e", "f"]
    assert [f.type for f in fields_] == [
        int,
        int,
        str | None,
        float,
        bool,
        list[int],
        Any,
    ]
    assert [f.frozen for f in fields_] == [False] * 7
    if is_named_tuple(obj):
        assert [f.default for f in fields_] == [None, 0, None, 0.0, False, [], ()]
    else:
        # namedtuples don't have default_factory
        assert [f.default for f in fields_] == [
            Field.MISSING,
            0,
            None,
            0.0,
            False,
            Field.MISSING,
            (),
        ]
        assert [f.default_factory for f in fields_] == [
            *[Field.MISSING] * 5,
            list,
            Field.MISSING,
        ]

    obj2 = replace(obj, required=-1, a=1, b="b2", c=1.0, d=True, e=[1, 2, 3], f={})
    assert asdict(obj2) == {
        "required": -1,
        "a": 1,
        "b": "b2",
        "c": 1.0,
        "d": True,
        "e": [1, 2, 3],
        "f": {},
    }

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
        b: str | None
        c: float
        d: bool
        e: list[int]

    assert fields(Model) == (
        Field(name="a", type=int),
        Field(name="b", type=Optional[str]),  # noqa: UP045
        Field(name="c", type=float),
        Field(name="d", type=bool),
        Field(name="e", type=list[int]),
    )


def test_missing_has_no_doc() -> None:
    """MISSING.__doc__ should be None, not inherited enum doc. gh-41."""
    assert Field.MISSING.__doc__ is None
    assert getattr(Field.MISSING, "__doc__", None) is None
