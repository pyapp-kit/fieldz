import sys
from typing import Any, Generic, Literal, NewType, Optional, TypeVar, Union

import pytest
from typing_extensions import Annotated

import fieldz
from fieldz._repr import PlainRepr

T = TypeVar("T")

NewInt = NewType("NewInt", int)


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
    assert PlainRepr.for_type(Literal[1, "2", (1, 2)]) == "Literal[1, '2', (1, 2)]"

    assert PlainRepr.for_type(func) == "func"
    assert PlainRepr.for_type(Foo()) == "Foo"
    # in python <=3.9 the module appears to be in the qualname for Parametrized generics
    assert "ParamFoo[int]" in PlainRepr.for_type(ParamFoo[int])
    assert PlainRepr.for_type(Any) == "Any"
    assert PlainRepr.for_type(Annotated[int, None]) == "Annotated[int, None]"

    # test TypeVar and NewInt cases directly as their representation must be handled
    # separately
    assert PlainRepr.for_type(T) == "T"
    assert PlainRepr.for_type(NewInt) == "NewInt"


@pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason="requires Python 3.12 or newer to support typing syntactic sugar",
)
def test_PlainRepr_with_syntactic_sugar() -> None:
    # Test cases using the typing syntactic sugar of python >= 3.12

    # Create a namespace dictionary to capture the exec'd variables
    namespace = {}
    exec("type ExampleAlias = str | int", namespace)
    ExampleAlias = namespace["ExampleAlias"]
    assert PlainRepr.for_type(ExampleAlias) == "ExampleAlias"
    assert (
        PlainRepr.for_type(ExampleAlias | tuple[ExampleAlias, ...])
        == "Union[ExampleAlias, tuple[ExampleAlias, ...]]"
    )
    assert (
        PlainRepr.for_type(ExampleAlias | tuple[ExampleAlias, ...], modern_union=True)
        == "ExampleAlias | tuple[ExampleAlias, ...]"
    )
    assert (
        PlainRepr.for_type(Annotated[ExampleAlias, None])
        == "Annotated[ExampleAlias, None]"
    )
    assert PlainRepr.for_type(dict[str, ExampleAlias]) == "dict[str, ExampleAlias]"


def test_rich_reprs() -> None:
    assert not list(fieldz.Constraints().__rich_repr__())
    assert list(fieldz.Constraints(ge=1).__rich_repr__()) == [("ge", 1)]

    assert ("name", "hi") in fieldz.Field(name="hi").__rich_repr__()
    assert "native_field" not in dict(
        fieldz.Field(name="hi", repr=False).__rich_repr__()
    )
