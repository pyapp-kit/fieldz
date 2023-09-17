"""Utilities for providing compatibility with many dataclass-like libraries."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dataclass-compat")
except PackageNotFoundError:
    __version__ = "uninstalled"

__all__ = [
    "Field",
    "DataclassParams",
    "fields",
    "asdict",
    "astuple",
    "replace",
    "params",
    "Adapter",
    "get_adapter",
]

from ._functions import asdict, astuple, fields, get_adapter, params, replace
from ._types import DataclassParams, Field
from .adapters import Adapter
