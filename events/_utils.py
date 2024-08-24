from __future__ import annotations

__all__ = (
    'Sentinel',
    'unwrap_func',
)

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable

    FuncT = Callable[..., Any]


class Sentinel(Enum):
    SHUTDOWN = auto()


def unwrap_func(f: FuncT) -> FuncT:
    if isinstance(f, staticmethod):
        f = f.__func__
    return f
