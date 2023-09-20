"""Adapter modules for fieldz."""

from typing import Tuple

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

# Order matters here. The first adapter to return True for is_instance will be used.
ADAPTER_MODULES: Tuple[Adapter, ...] = (
    _pydantic,
    _attrs,
    _msgspec,
    _dataclassy,
    _dataclasses,
    _named_tuple,
    _typed_dict,
)

__all__ = ["ADAPTER_MODULES", "Adapter"]
