from dataclasses import dataclass
from typing import List

import annotated_types as at
from dataclass_compat import fields
from typing_extensions import Annotated


def test_annotated_types() -> None:
    @dataclass
    class MyClass:
        age: Annotated[int, at.Gt(18)]
        span: Annotated[float, at.Interval(ge=0, le=10)]
        even: Annotated[int, at.MultipleOf(2)]
        # note that annotated types will NOT iterate min_length=0
        my_list: Annotated[List[int], at.Len(1, 10)]
        lower_name: Annotated[str, at.Predicate(str.islower)]
        # TODO: determine how to handle nested Annotated types
        # factors: List[Annotated[str, at.Predicate(str.islower)]]
        with_tz: Annotated[str, at.Timezone(...)]
        unannotated: int = 0

    fields_ = {f.name: f for f in fields(MyClass)}
    assert fields_["age"].constraints.gt == 18
    assert fields_["span"].constraints.ge == 0
    assert fields_["span"].constraints.le == 10
    assert fields_["even"].constraints.multiple_of == 2
    assert fields_["my_list"].constraints.min_length == 1
    assert fields_["my_list"].constraints.max_length == 10
    assert fields_["lower_name"].constraints.predicate == str.islower
    assert fields_["lower_name"].constraints.predicate == str.islower


def test_msgspec_constraints() -> None:
    from msgspec import Meta, Struct

    # TODO: determine how to handle nested Annotated types
    # UnixName = Annotated[
    #     str, Meta(min_length=1, max_length=32, pattern="^[a-z_][a-z0-9_-]*$")
    # ]
    # groups: Annotated[set[UnixName], Meta(max_length=16)] = set()  # type: ignore

    class MyClass(Struct):
        age: Annotated[int, Meta(gt=18)]
        span: Annotated[float, Meta(ge=0, le=10)]
        even: Annotated[int, Meta(multiple_of=2)]
        my_list: Annotated[List[int], Meta(min_length=1, max_length=10)]
        # msgspec puts title and description in the Meta object
        with_title: Annotated[str, Meta(title="Title", description="Description")]
        with_tz: Annotated[int, Meta(tz=True)]

    fields_ = {f.name: f for f in fields(MyClass)}
    assert fields_["age"].constraints.gt == 18
    assert fields_["span"].constraints.ge == 0
    assert fields_["span"].constraints.le == 10
    assert fields_["even"].constraints.multiple_of == 2
    assert fields_["my_list"].constraints.min_length == 1
    assert fields_["my_list"].constraints.max_length == 10
    assert fields_["with_title"].title == "Title"
    assert fields_["with_title"].description == "Description"
    assert fields_["with_tz"].constraints.tz is True
