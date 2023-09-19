# dataclass-compat

[![License](https://img.shields.io/pypi/l/dataclass-compat.svg?color=green)](https://github.com/pyapp-kit/dataclass-compat/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/dataclass-compat.svg?color=green)](https://pypi.org/project/dataclass-compat)
[![Python Version](https://img.shields.io/pypi/pyversions/dataclass-compat.svg?color=green)](https://python.org)
[![CI](https://github.com/pyapp-kit/dataclass-compat/actions/workflows/ci.yml/badge.svg)](https://github.com/pyapp-kit/dataclass-compat/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/pyapp-kit/dataclass-compat/branch/main/graph/badge.svg)](https://codecov.io/gh/pyapp-kit/dataclass-compat)

Unified API for working with multiple dataclass-like libraries

## Dataclass patterns

There are many libraries that implement a similar dataclass-like pattern!

### [`dataclasses.dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass)

```python
import dataclasses

@dataclasses.dataclass
class SomeDataclass:
    a: int = 0
    b: str = "b"
    c: list[int] = dataclasses.field(default_factory=list)
```

### [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/)

```python
import pydantic

class SomePydanticModel(pydantic.BaseModel):
    a: int = 0
    b: str = "b"
    c: list[int] = pydantic.Field(default_factory=list)
```

### [`attrs.define`](https://www.attrs.org/en/stable/overview.html)

```python
import attr

@attr.define
class SomeAttrsModel:
    a: int = 0
    b: str = "b"
    c: list[int] = attr.field(default=attr.Factory(list))
```

### [`msgspec.Struct`](https://jcristharif.com/msgspec/)

```python
import msgspec

class SomeMsgspecStruct(msgspec.Struct):
    a: int = 0
    b: str = "b"
    c: list[int] = msgspec.field(default_factory=list)
```

etc...

## Unified API

These are all awesome libraries, and each has its own strengths and weaknesses.
Sometimes, however, you just want to be able to query basic information about a
dataclass-like object, such as getting field names or types, or converting it to
a dictionary.

`dataclass-compat` provides a unified API for these operations (following or
extending the API from `dataclasses` when possible).

```python
def fields(obj: Any) -> tuple[Field, ...]:
    """Return a tuple of dataclass_compat.Field objects for the object."""

def replace(obj: Any, /, **changes: Any) -> Any:
    """Return a copy of obj with the specified changes."""

def asdict(obj: Any) -> dict[str, Any]:
    """Return a dict representation of obj."""

def astuple(obj: Any) -> tuple[Any, ...]:
    """Return a tuple representation of obj."""

def params(obj: Any) -> DataclassParams:
    """Return parameters used to define the dataclass."""
```

The `dataclass_compat.Field` and `dataclass_compat.DataclassParam` objects are
simple dataclasses that match the protocols of `dataclasses.Field` and the
(private) `dataclasses._DataclassParams` objects, respectively. The field object
also adds a `native_field` attribute that is the original field object from the
underlying library.

### Example

```python
from dataclass_compat import Field, fields

standardized_fields = (
    Field(name="a", type=int, default=0),
    Field(name="b", type=str, default="b"),
    Field(name="c", type=list[int], default_factory=list),
)

assert (
    fields(SomeDataclass)
    == fields(SomePydanticModel)
    == fields(SomeAttrsModel)
    == fields(SomeMsgspecStruct)
    == standardized_fields
)
```

### Supported libraries

- [x] [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- [x] [`collections.namedtuple`](https://docs.python.org/3/library/collections.html#collections.namedtuple)
- [x] [`pydantic`](https://docs.pydantic.dev/latest/) (v1 and v2)
- [x] [`attrs`](https://www.attrs.org/en/stable/overview.html)
- [x] [`msgspec`](https://jcristharif.com/msgspec/)
- [x] [`dataclassy`](https://github.com/biqqles/dataclassy)
- [x] [`sqlmodel`](https://sqlmodel.tiangolo.com) (it's just pydantic)

... maybe someday?

- [ ] [`pyfields`](https://smarie.github.io/python-pyfields/)
- [ ] [`marshmallow`](https://marshmallow.readthedocs.io/en/stable/quickstart.html)
- [ ] [`sqlalchemy`](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [ ] [`django`](https://docs.djangoproject.com/en/dev/topics/db/models/)
- [ ] [`peewee`](http://docs.peewee-orm.com/en/latest/peewee/models.html#models)
- [ ] [`pyrsistent`](https://github.com/tobgu/pyrsistent/)
- [ ] [`recordclass`](https://pypi.org/project/recordclass/)
