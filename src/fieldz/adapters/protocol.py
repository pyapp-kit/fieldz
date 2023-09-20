from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from fieldz._types import DataclassParams, Field


#  MISSING, replace
_T = TypeVar("_T")


DataclassLike: TypeAlias = Any
_DataclassType = TypeVar("_DataclassType", bound=DataclassLike)


class Adapter(Protocol, Generic[_DataclassType]):
    """Protocol that adapter modules need to implement."""

    # @overload
    # def is_instance(self, obj: _DataclassType) -> Literal[True]:
    #     ...

    # @overload
    # def is_instance(self, obj: type) -> TypeGuard[type[_DataclassType]]:
    #     ...

    # @overload
    # def is_instance(
    #     self, obj: object
    # ) -> TypeGuard[_DataclassType | type[_DataclassType]]:
    #     ...

    def is_instance(self, obj: DataclassLike) -> bool:
        """Return true if obj is a a recognized instance for this adapter."""

    def asdict(self, obj: DataclassLike) -> dict[str, Any]:
        """Return a dict representation of obj."""

    def astuple(self, obj: DataclassLike) -> tuple[Any, ...]:
        """Return a tuple representation of obj."""

    def replace(self, obj: _DataclassType, /, **changes: Any) -> _DataclassType:
        """Return a copy of obj with the specified changes."""

    def fields(self, obj: DataclassLike | type[DataclassLike]) -> tuple[Field, ...]:
        """Return a tuple of fields for the class or instance."""

    def params(self, obj: DataclassLike) -> DataclassParams:
        """Return parameters used to define the dataclass."""
