"""Utilities for providing compatibility with many dataclass-like libraries."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fieldz")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

__all__ = [
    "Adapter",
    "asdict",
    "astuple",
    "Constraints",
    "DataclassParams",
    "Field",
    "fields",
    "get_adapter",
    "params",
    "replace",
]

from ._functions import asdict, astuple, fields, get_adapter, params, replace
from ._types import Constraints, DataclassParams, Field
from .adapters import Adapter
