from __future__ import annotations

import sys
import types
import typing
from typing import Any

import typing_extensions

try:
    from typing import _TypingBase  # type: ignore[attr-defined]
except ImportError:
    from typing import _Final as _TypingBase  # type: ignore[attr-defined]

typing_base = _TypingBase

if sys.version_info < (3, 9):
    # python < 3.9 does not have GenericAlias (list[int], tuple[str, ...] and so on)
    TypingGenericAlias = ()
else:
    from typing import GenericAlias as TypingGenericAlias  # type: ignore

if sys.version_info < (3, 10):

    def origin_is_union(tp: type[Any] | None) -> bool:
        return tp is typing.Union

    WithArgsTypes = (TypingGenericAlias,)

else:

    def origin_is_union(tp: type[Any] | None) -> bool:
        return tp is typing.Union or tp is types.UnionType  # type: ignore

    WithArgsTypes = (typing._GenericAlias, types.GenericAlias, types.UnionType)  # type: ignore[attr-defined]


class PlainRepr(str):
    """String class where repr doesn't include quotes.

    Useful with Representation when you want to return a string
    representation of something that is valid (or pseudo-valid) python.
    """

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def for_type(cls, tp: Any, *, modern_union: bool = False) -> PlainRepr:
        """Return a PlainRepr for a type."""
        return PlainRepr(display_as_type(tp, modern_union=modern_union))


def display_as_type(obj: Any, *, modern_union: bool = False) -> str:
    """Pretty representation of a type.

    Should be as close as possible to the original type definition string.
    Takes some logic from `typing._type_repr`.
    """
    if isinstance(obj, types.FunctionType):
        return obj.__name__
    elif obj is ...:
        return "..."
    elif obj in (None, type(None)):
        return "None"

    if not isinstance(obj, (typing_base, WithArgsTypes, type)):
        obj = obj.__class__

    if origin_is_union(typing_extensions.get_origin(obj)):
        args = [display_as_type(x) for x in typing_extensions.get_args(obj)]
        if modern_union:
            return " | ".join(args)
        if len(args) == 2 and "None" in args:
            args.remove("None")
            return f"Optional[{args[0]}]"
        return f"Union[{', '.join(args)}]"
    elif isinstance(obj, WithArgsTypes):
        argstr = ", ".join(map(display_as_type, typing_extensions.get_args(obj)))
        return f"{obj.__qualname__}[{argstr}]"
    elif isinstance(obj, type):
        return obj.__qualname__
    else:  # pragma: no cover
        return repr(obj).replace("typing.", "").replace("typing_extensions.", "")
