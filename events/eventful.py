from __future__ import annotations

__all__ = (
    'EventfulMeta',
    'AbstractEventful',
    'Eventful',
    'AsyncEventful',
)

import asyncio
from abc import ABC, ABCMeta
from typing import TYPE_CHECKING, Generic, TypeVar
from .event_bus import AbstractEventBus, AbstractAsyncEventBus
from ._utils import unwrap_func

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing_extensions import Self
    from typing import Any, Callable

    FuncT = Callable[..., Any]


EventBusT = TypeVar('EventBusT', bound=AbstractEventBus)


class EventfulMeta(ABCMeta):
    __event_listeners__: Iterable[tuple[str, str, int | None]]

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        new_cls = super().__new__(cls, *args, **kwargs)

        listener_funcs = {}  # type: dict[str, FuncT]

        for base in reversed(new_cls.__mro__):
            for func_name, func_value in base.__dict__.items():
                func_value = unwrap_func(func_value)

                if hasattr(func_value, '__is_event_listener__'):
                    listener_funcs[func_name] = func_value

                elif func_name in listener_funcs:
                    del listener_funcs[func_name]

        event_listeners = []  # type: list[tuple[str, str, int | None]]

        for func_name, func_value in listener_funcs.items():
            for event_name, priority in getattr(func_value, '__event_targets__', ()):
                event_listeners.append((event_name, func_name, priority))

        new_cls.__event_listeners__ = event_listeners

        return new_cls


class AbstractEventful(Generic[EventBusT], ABC, metaclass=EventfulMeta):
    __event_listeners__: Iterable[tuple[str, str, int | None]]
    __event_buses__: set[EventBusT] | None = None

    def get_listeners(self) -> Iterable[tuple[str, FuncT, int | None]]:
        """
        Get a list of all event listeners within this eventful class.

        :return: A list of tuples containing an event name, callback function, and priority.
        """
        return [(event, getattr(self, func_name), priority)
                for event, func_name, priority
                in self.__event_listeners__]

    def get_event_buses(self) -> frozenset[EventBusT]:
        """
        Get a frozen set of event buses bound to this instance.

        :return: The frozen set of event buses.
        """
        if event_buses := self.__event_buses__:
            return frozenset(event_buses)
        return frozenset()

    def add_event_bus(self, event_bus: EventBusT) -> None:
        """
        Bind an event bus to this eventful instance.

        :param event_bus: The event bus to bind.
        """
        if self.__event_buses__ is None:
            self.__event_buses__ = set()
        self.__event_buses__.add(event_bus)

    def remove_event_bus(self, event_bus: EventBusT) -> None:
        """
        Unbind an event bus from this eventful instance.

        :param event_bus: The event bus to unbind.
        """
        if event_buses := self.__event_buses__:
            event_buses.discard(event_bus)


class Eventful(AbstractEventful[AbstractEventBus]):
    __slots__ = ()

    def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event into all bound event buses to invoke all associated
        event listeners with the supplied arguments.

        :param event:  The event name to invoke listeners of.
        :param args:   The arguments to invoke event listeners with.
        :param kwargs: The keyword arguments to invoke event listeners with.
        """
        for event_bus in self.get_event_buses():
            event_bus.emit(event, *args, **kwargs)


class AsyncEventful(AbstractEventful[AbstractAsyncEventBus]):
    __slots__ = ()

    async def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event into all bound event buses to invoke all associated
        event listeners with the supplied arguments.

        :param event:  The event name to invoke listeners of.
        :param args:   The arguments to invoke event listeners with.
        :param kwargs: The keyword arguments to invoke event listeners with.
        """
        futures = [event_bus.emit(event, *args, **kwargs)
                   for event_bus in self.get_event_buses()]
        await asyncio.gather(*futures)
