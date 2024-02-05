"""Adapter modules for fieldz."""

from . import (
    _attrs,
    _dataclasses,
    _dataclassy,
    _msgspec,
    _named_tuple,
    _pydantic,
    _typed_dict,
)
from .protocol import Adapter

__all__ = [
    "Adapter",
    "_attrs",
    "_dataclasses",
    "_dataclassy",
    "_msgspec",
    "_named_tuple",
    "_pydantic",
    "_typed_dict",
]
