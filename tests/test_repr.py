from typing import Any, Generic, Optional, TypeVar, Union

import fieldz
from fieldz._repr import PlainRepr
from typing_extensions import Annotated

T = TypeVar("T")


def func() -> None:
    pass


class Foo:
    pass


class ParamFoo(Generic[T]):
    pass


def test_PlainRepr() -> None:
    assert PlainRepr("str") == "str"
    assert PlainRepr.for_type(int) == "int"
    assert PlainRepr.for_type(...) == "..."
    assert PlainRepr.for_type(None) == "None"
    assert PlainRepr.for_type(Optional[int]) == "Optional[int]"
    assert PlainRepr.for_type(Union[int, str]) == "Union[int, str]"
    assert PlainRepr.for_type(Optional[int], modern_union=True) == "int | None"

    assert PlainRepr.for_type(func) == "func"
    assert PlainRepr.for_type(Foo()) == "Foo"
    assert PlainRepr.for_type(ParamFoo[int]) == "ParamFoo[int]"
    assert PlainRepr.for_type(Annotated[int, Foo()]) == "Annotated[int, Foo]"
    assert PlainRepr.for_type(Any) == "Any"


def test_rich_reprs() -> None:
    assert not list(fieldz.Constraints().__rich_repr__())
    assert list(fieldz.Constraints(ge=1).__rich_repr__()) == [("ge", 1)]

    assert ("name", "hi") in fieldz.Field(name="hi").__rich_repr__()
    assert "native_field" not in dict(
        fieldz.Field(name="hi", repr=False).__rich_repr__()
    )
