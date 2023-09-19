import annotated_types as at
from dataclass_compat import fields
from pydantic import BaseModel, Field, conint, constr
from typing_extensions import Annotated

PATTERN = r"^[a-z]+$"
try:
    e_constr = constr(regex=r"^[a-z]+$")
    f_field = Field(default="abc", regex=PATTERN)
except TypeError:  # pydantic v2
    e_constr = constr(pattern=r"^[a-z]+$")  # type: ignore
    f_field = Field(default="abc", pattern=PATTERN)


def test_pydantic_constraints() -> None:
    class M(BaseModel):
        a: int = Field(default=50, ge=42, le=100)
        b: Annotated[int, Field(ge=42, le=100)] = 50
        c: Annotated[int, at.Ge(42), at.Le(100)] = 50
        d: conint(ge=42, le=100) = 50  # type: ignore
        e: e_constr = "abc"  # type: ignore
        f: str = f_field

    for f in fields(M):
        assert f.constraints
        if f.name in {"e", "f"}:
            assert f.constraints.pattern == PATTERN
        else:
            assert f.constraints.ge == 42
            assert f.constraints.le == 100
            assert f.default == 50
            assert f.default == 50
