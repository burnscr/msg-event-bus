from __future__ import annotations

__all__ = (
    'AbstractEventful',
    'AbstractAsyncEventful',
)

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from events.abc.emiter import EventEmitter, AsyncEventEmitter

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any, Callable

    FuncT = Callable[..., Any]


EventEmitterT = TypeVar('EventEmitterT', bound=EventEmitter)
AsyncEventEmitterT = TypeVar('AsyncEventEmitterT', bound=AsyncEventEmitter)


class AbstractEventful(Generic[EventEmitterT], EventEmitter, ABC):
    __slots__ = ()

    @abstractmethod
    def get_listeners(self) -> Iterable[tuple[str, FuncT, int | None]]:
        raise NotImplementedError()

    @abstractmethod
    def get_event_buses(self) -> frozenset[EventEmitterT]:
        raise NotImplementedError()

    @abstractmethod
    def add_event_bus(self, event_bus: EventEmitterT) -> None:
        raise NotImplementedError()

    @abstractmethod
    def remove_event_bus(self, event_bus: EventEmitterT) -> None:
        raise NotImplementedError()


class AbstractAsyncEventful(Generic[AsyncEventEmitterT], AsyncEventEmitter, ABC):
    __slots__ = ()

    @abstractmethod
    def get_listeners(self) -> Iterable[tuple[str, FuncT, int | None]]:
        raise NotImplementedError()

    @abstractmethod
    def get_event_buses(self) -> frozenset[AsyncEventEmitterT]:
        raise NotImplementedError()

    @abstractmethod
    def add_event_bus(self, event_bus: AsyncEventEmitterT) -> None:
        raise NotImplementedError()

    @abstractmethod
    def remove_event_bus(self, event_bus: AsyncEventEmitterT) -> None:
        raise NotImplementedError()
