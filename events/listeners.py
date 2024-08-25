from __future__ import annotations

__all__ = (
    'EventListeners',
    'event_listener',
)

from bisect import insort
from itertools import groupby
from threading import Lock
from typing import TYPE_CHECKING

from ._utils import unwrap_func

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from typing import Any, Callable

    FuncT = Callable[..., Any]


class _EventListener:
    __slots__ = 'callback', 'priority'

    def __init__(self, callback: FuncT, priority: int) -> None:
        self.callback = callback
        self.priority = priority

    def __repr__(self) -> str:
        return f'<listener {self.callback.__name__} with priority {self.priority}>'

    def __eq__(self, other: _EventListener) -> bool:
        if isinstance(other, _EventListener):
            return self.callback == other.callback
        return False

    def __lt__(self, other: _EventListener) -> bool:
        if isinstance(other, _EventListener):
            return self.priority < other.priority
        raise TypeError(f'Cannot compare EventListener to {type(other).__name__}')


class EventListeners:
    __slots__ = (
        'default_priority',
        '_cached_listeners',
        '_sorted_listeners',
        '_listener_lock',
    )

    def __init__(self, default_priority: int) -> None:
        self.default_priority = default_priority
        self._cached_listeners = {}  # type: dict[str, Sequence[Iterable[FuncT]]]
        self._sorted_listeners = {}  # type: dict[str, list[_EventListener]]
        self._listener_lock = Lock()

    def priority(self, value: int | None) -> int:
        if value is None:
            value = self.default_priority
        if not isinstance(value, int):
            raise TypeError(f'Priority must be an int, not {type(value).__name__}')
        return value

    def get_event_callbacks(self, event: str) -> Sequence[Iterable[FuncT]]:
        """
        Retrieve callback functions grouped by priority for an event.

        The returned groups are ordered by increasing priority value.

        :param event: The event name to return callback functions for.
        :return: An ordered collection of grouped callback functions.
        """
        with self._listener_lock:
            callbacks = self._cached_listeners.get(event)
        return callbacks or tuple()

    def add_event_callback(self, event: str, callback: FuncT, priority: int | None) -> None:
        """
        Bind a callback function to an event with an optional execution priority.

        If a priority value is not provided, the class default will be used.

        :param event:    The event name to bind the callback function to.
        :param callback: The callback function to bind to the event name.
        :param priority: An optional invocation priority value to assign.
        """
        callback = unwrap_func(callback)
        priority = self.priority(priority)
        listener = _EventListener(callback, priority)

        # Acquire the lock to prevent concurrent modification
        with self._listener_lock:

            # Ensure the event exists within the sorted event listeners
            if event not in self._sorted_listeners:
                self._sorted_listeners[event] = []

            listeners = self._sorted_listeners[event]

            # Remove the older listener to replace its old priority value.
            if listener in listeners:
                listeners.remove(listener)

            # Utilize insertion sort since listeners are already sorted
            insort(listeners, listener)

            # Regenerate and cache the new prioritized groups for the event
            # to allow for rapid lookup later while the event loop is running.
            self._update_cache(event, listeners)

    def remove_event_callback(self, event: str, callback: FuncT) -> None:
        """
        Unbind a callback function from an event.

        :param event:    The event name to unbind the callback function from.
        :param callback: The callback function to unbind from the event name.
        """
        callback = unwrap_func(callback)
        listener = _EventListener(callback, priority=0)

        # Acquire the lock to prevent concurrent modification
        with self._listener_lock:

            if listeners := self._sorted_listeners.get(event):

                if listener in listeners:
                    listeners.remove(listener)

                    # Regenerate and recache the new prioritized groups for the
                    # event.
                    self._update_cache(event, listeners)

                # Remove the listener collections if no more listeners are
                # bound to the event.
                if not listeners:
                    del self._sorted_listeners[event]
                    del self._cached_listeners[event]

    def _update_cache(self, event: str, listeners: list[_EventListener]) -> None:
        """
        Group the event listener callback functions by ascending priority and
        cache them under the event name.

        Assuming events will be dispatched more frequently than the event listeners
        will be updated, this allows for a quicker lookup time within performance
        critical executors.

        :param event:     The event name to cache the newly grouped callbacks to.
        :param listeners: The collection of prioritized listeners for the event.
        """
        event_listeners = []  # type: list[Iterable[FuncT]]

        for priority, group in groupby(listeners, lambda listener: listener.priority):
            callbacks = tuple(map(lambda listener: listener.callback, group))
            event_listeners.append(callbacks)

        self._cached_listeners[event] = tuple(event_listeners)


def event_listener(event: str, priority: int = None) -> Callable[[FuncT], FuncT]:
    """
    Decorate a callback function within an Eventful class to bind the
    function to an event with an optional execution priority.

    If a priority value is not provided, the class default will be used.

    The callback function will be invoked when the event is emitted.

    :param event:    The event name to bind the callback function to.
    :param priority: An optional invocation priority value to assign.
    """

    if event is not None and not isinstance(event, str):
        raise TypeError(f'Event listener expects event to be str, but received {type(event).__name__}')

    if priority is not None and not isinstance(priority, int):
        raise TypeError(f'Event listener expects priority to be int, but received {type(priority).__name__}')

    def decorator(func: FuncT) -> FuncT:
        inner_func = unwrap_func(func)
        inner_func.__is_event_listener__ = True

        if not hasattr(inner_func, '__event_targets__'):
            inner_func.__event_targets__ = set()

        if hasattr(inner_func, '__event_targets__'):
            event_targets = inner_func.__event_targets__
            event_targets.add((event, priority))

        return func

    return decorator
