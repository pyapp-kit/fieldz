import annotated_types as at
from dataclass_compat import fields
from pydantic import BaseModel, Field, conint, constr
from typing_extensions import Annotated

try:
    constr_ = constr(regex=r"^[a-z]+$")
except TypeError:
    constr_ = constr(pattern=r"^[a-z]+$")  # type: ignore


def test_pydantic_constraints() -> None:
    class M(BaseModel):
        a: int = Field(default=50, ge=42, le=100)
        b: Annotated[int, Field(ge=42, le=100)] = 50
        c: Annotated[int, at.Ge(42), at.Le(100)] = 50
        d: conint(ge=42, le=100) = 50  # type: ignore
        e: constr_ = "abc"  # type: ignore

    for f in fields(M):
        assert f.constraints
        if f.name == "e":
            assert f.constraints.pattern == r"^[a-z]+$"
        else:
            assert f.constraints.ge == 42
            assert f.constraints.le == 100
            assert f.default == 50
            assert f.default == 50
