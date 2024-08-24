from __future__ import annotations

__all__ = (
    'EventEmitter',
    'AsyncEventEmitter',
)

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class EventEmitter(ABC):
    """
    Abstract base class for classes that emit events.
    """
    __slots__ = ()

    @abstractmethod
    def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError()


class AsyncEventEmitter(ABC):
    """
    Abstract base class for classes that emit asynchronous events.
    """
    __slots__ = ()

    @abstractmethod
    async def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError()
