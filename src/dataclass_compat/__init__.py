"""Utilities for providing compatibility with many dataclass-like libraries"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dataclass-compat")
except PackageNotFoundError:
    __version__ = "uninstalled"
__author__ = "Talley Lambert"
__email__ = "talley.lambert@gmail.com"
