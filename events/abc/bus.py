from __future__ import annotations

__all__ = (
    'DEFAULT_PRIORITY',
    'AbstractEventBus',
    'AbstractAsyncEventBus',
)

import logging
from abc import ABC, abstractmethod
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING

from events.abc.emiter import EventEmitter, AsyncEventEmitter
from events.abc.eventful import AbstractAsyncEventful, AbstractEventful
from events.listeners import EventListeners

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any, Callable

    FuncT = Callable[..., Any]


DEFAULT_PRIORITY = 10_000


class _BaseEventBus:
    __slots__ = (
        'error_callback',
        '__event_listeners',
    )

    def __init__(self, default_priority: int = DEFAULT_PRIORITY) -> None:
        """
        Create a new event bus to receive and dispatch events to callback functions.

        :param default_priority: The default priority value to assign to event listeners.
        """
        self.error_callback = self._on_dispatch_error
        self.__event_listeners = EventListeners(default_priority)

    @property
    def default_priority(self) -> int:
        """
        The default invocation priority assigned to event listeners.
        """
        return self.__event_listeners.default_priority

    def get_event_callbacks(self, event: str) -> Iterable[Iterable[FuncT]]:
        """
        Retrieve callback functions grouped by priority for an event.

        The returned groups are ordered by increasing priority value.

        :param event: The event name to return callback functions for.
        :return: An ordered collection of grouped callback functions.
        """
        return self.__event_listeners.get_event_callbacks(event)

    def add_event_callback(self, event: str, callback: FuncT, priority: int = None) -> None:
        """
        Bind a callback function to an event with an optional execution priority.

        If a priority value is not provided, the class default will be used.

        The callback function will be invoked when the event is emitted.

        :param event:    The event name to bind the callback function to.
        :param callback: The callback function to bind to the event name.
        :param priority: An optional invocation priority value to assign.
        """
        self.__event_listeners.add_event_callback(event, callback, priority)

    def remove_event_callback(self, event: str, callback: FuncT) -> None:
        """
        Unbind a callback function from an event.

        The callback function will no longer be invoked when the event
        is emitted.

        :param event:    The event name to unbind the callback function from.
        :param callback: The callback function to unbind from the event name.
        """
        self.__event_listeners.remove_event_callback(event, callback)

    def on(self, event: str, /, priority: int = None) -> Callable[[FuncT], FuncT]:
        """
        Decorate a callback function to bind it to an event with an optional
        execution priority.

        If a priority value is not provided, the class default will be used.

        The callback function will be invoked when the event is emitted.

        :param event:    The event name to bind the callback function to.
        :param priority: An optional invocation priority value to assign.
        """
        def decorator(func: FuncT) -> FuncT:
            self.add_event_callback(event, func, priority)

            return func
        return decorator

    # noinspection PyUnusedLocal
    @staticmethod
    def _on_dispatch_error(
        event: str,
        error: Exception,
        args: Any,
        kwargs: Any
    ) -> None:
        """
        Event handler invoked whenever an exception is raised when dispatching
        an event and invoking event listeners.

        :param event:  The event name that raised an exception.
        :param error:  The exception that was raised.
        :param args:   The arguments used to invoke the event callbacks.
        :param kwargs: The keyword arguments used to invoke the event callbacks.
        """
        logging.error(
            msg=f'An exception was raised while dispatching a {event!r} event',
            exc_info=error,
        )


class AbstractEventBus(EventEmitter, _BaseEventBus, ABC):
    """
    Abstract base class for event buses.
    """
    __slots__ = ()

    @abstractmethod
    def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event into the event bus to invoke all associated event
        listeners with the supplied arguments.

        :param event:  The event name to invoke listeners of.
        :param args:   The arguments to invoke event listeners with.
        :param kwargs: The keyword arguments to invoke event listeners with.
        """
        raise NotImplementedError()

    def add_event_callback(self, event: str, callback: FuncT, priority: int = None) -> None:
        """
        Bind a callback function to an event with an optional execution priority.

        If a priority value is not provided, the class default will be used.

        The callback function will be invoked when the event is emitted.

        :param event:    The event name to bind the callback function to.
        :param callback: The callback function to bind to the event name.
        :param priority: An optional invocation priority value to assign.
        :raise TypeError: If the callback is a coroutine function.
        """
        if iscoroutinefunction(callback):
            raise TypeError(f'Event callback {callback.__qualname__} cannot be a coroutine function.')

        super().add_event_callback(event, callback, priority)

    def bind_eventful(self, eventful: AbstractEventful) -> None:
        """
        Bind an eventful class instance to this event bus and subscribe
        all of its event listeners to their declared event names.

        :param eventful: The eventful class instance to bind.
        :raise TypeError: If provided argument is not an instance of Eventful.
        """
        if not isinstance(eventful, AbstractEventful):
            raise TypeError(
                f'{self.bind_eventful.__qualname__} expects a {AbstractEventful.__name__}'
                f' instance, but received {type(eventful).__name__} instead.'
            )

        eventful.add_event_bus(self)

        for event, callback, priority in eventful.get_listeners():
            self.add_event_callback(event, callback, priority)

    def unbind_eventful(self, eventful: AbstractEventful) -> None:
        """
        Unbind an eventful class instance from this event bus and unsubscribe
        all of its event listeners from their declared event names.

        :param eventful: The eventful class instance to unbind.
        :raise TypeError: If provided argument is not an instance of Eventful.
        """
        if not isinstance(eventful, AbstractEventful):
            raise TypeError(
                f'{self.unbind_eventful.__qualname__} expects a {AbstractEventful.__name__}'
                f' instance, but received {type(eventful).__name__} instead.'
            )

        for event, callback, priority in eventful.get_listeners():
            self.remove_event_callback(event, callback)

        eventful.remove_event_bus(self)


class AbstractAsyncEventBus(AsyncEventEmitter, _BaseEventBus, ABC):
    """
    Abstract base class for asynchronous event buses.
    """
    __slots__ = ()

    @abstractmethod
    async def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event into the event bus to invoke all associated event
        listeners with the supplied arguments.

        :param event:  The event name to invoke listeners of.
        :param args:   The arguments to invoke event listeners with.
        :param kwargs: The keyword arguments to invoke event listeners with.
        """
        raise NotImplementedError()

    def bind_eventful(self, eventful: AbstractAsyncEventful) -> None:
        """
        Bind an async eventful class instance to this event bus and subscribe
        all of its event listeners to their declared event names.

        :param eventful: The async eventful class instance to bind.
        :raise TypeError: If provided argument is not an instance of AsyncEventful.
        """
        if not isinstance(eventful, AbstractAsyncEventful):
            raise TypeError(
                f'{self.bind_eventful.__qualname__} expects a {AbstractAsyncEventful.__name__}'
                f' instance, but received {type(eventful).__name__} instead.'
            )

        eventful.add_event_bus(self)

        for event, callback, priority in eventful.get_listeners():
            self.add_event_callback(event, callback, priority)

    def unbind_eventful(self, eventful: AbstractAsyncEventful) -> None:
        """
        Unbind an async eventful class instance from this event bus and
        unsubscribe all of its event listeners from their declared event
        names.

        :param eventful: The async eventful class instance to unbind.
        :raise TypeError: If provided argument is not an instance of AsyncEventful.
        """
        if not isinstance(eventful, AbstractAsyncEventful):
            raise TypeError(
                f'{self.unbind_eventful.__qualname__} expects a {AbstractAsyncEventful.__name__}'
                f' instance, but received {type(eventful).__name__} instead.'
            )

        for event, callback, priority in eventful.get_listeners():
            self.remove_event_callback(event, callback)

        eventful.remove_event_bus(self)
