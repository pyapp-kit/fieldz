"""Utilities for providing compatibility with many dataclass-like libraries."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fieldz")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

__all__ = [
    "Adapter",
    "Constraints",
    "DataclassParams",
    "Field",
    "asdict",
    "astuple",
    "display_as_type",
    "fields",
    "get_adapter",
    "params",
    "replace",
]

from ._functions import asdict, astuple, fields, get_adapter, params, replace
from ._repr import display_as_type
from ._types import Constraints, DataclassParams, Field
from .adapters import Adapter
