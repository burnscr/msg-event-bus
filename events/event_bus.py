from __future__ import annotations

__all__ = (
    'AbstractEventBus',
    'AbstractAsyncEventBus',
    'EventBus',
    'AsyncEventBus',
    'ThreadedEventBus',
)

import asyncio
import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from inspect import isawaitable, iscoroutinefunction
from queue import Queue
from threading import Lock, Thread
from typing import TYPE_CHECKING

from ._utils import Sentinel
from .listeners import EventListeners

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing_extensions import Self
    from typing import Any, Awaitable, Callable
    from .eventful import Eventful, AsyncEventful

    FuncT = Callable[..., Any]


DEFAULT_PRIORITY = 10_000


class AbstractEventBus(ABC):
    """
    Abstract base class for event buses.
    """
    __slots__ = (
        'on_dispatch_error',
        '_event_listeners',
    )

    def __init__(self, default_priority: int = DEFAULT_PRIORITY) -> None:
        """
        Create a new event bus to receive and dispatch events to callback functions.

        :param default_priority: The default priority value to assign to event listeners.
        """
        self.on_dispatch_error = self._on_dispatch_error
        self._event_listeners = EventListeners(default_priority)

    @property
    def default_priority(self) -> int:
        """
        The default invocation priority assigned to event listeners.
        """
        return self._event_listeners.default_priority

    # -- Event Dispatcher --

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

    # -- Event Listener Management --

    def get_event_callbacks(self, event: str) -> Iterable[Iterable[FuncT]]:
        """
        Retrieve callback functions grouped by priority for an event.

        The returned groups are ordered by increasing priority value.

        :param event: The event name to return callback functions for.
        :return: An ordered collection of grouped callback functions.
        """
        return self._event_listeners.get_event_callbacks(event)

    def add_event_callback(self, event: str, callback: FuncT, priority: int = None) -> None:
        """
        Bind a callback function to an event with an optional execution priority.

        If a priority value is not provided, the class default will be used.

        The callback function will be invoked when the event is emitted.

        :param event:    The event name to bind the callback function to.
        :param callback: The callback function to bind to the event name.
        :param priority: An optional invocation priority value to assign.
        """
        self._event_listeners.add_event_callback(event, callback, priority)

    def remove_event_callback(self, event: str, callback: FuncT) -> None:
        """
        Unbind a callback function from an event.

        The callback function will no longer be invoked when the event
        is emitted.

        :param event:    The event name to unbind the callback function from.
        :param callback: The callback function to unbind from the event name.
        """
        self._event_listeners.remove_event_callback(event, callback)

    def bind_eventful(self, eventful: Eventful) -> None:
        """
        Bind an eventful class instance to this event bus and subscribe
        all of its event listeners to their declared event names.

        :param eventful: The eventful class instance to bind.
        """
        eventful.add_event_bus(self)

        for event, callback, priority in eventful.get_listeners():
            self.add_event_callback(event, callback, priority)

    def unbind_eventful(self, eventful: Eventful) -> None:
        """
        Unbind an eventful class instance from this event bus and unsubscribe
        all of its event listeners from their declared event names.

        :param eventful: The eventful class instance to unbind.
        """
        for event, callback, priority in eventful.get_listeners():
            self.remove_event_callback(event, callback)

        eventful.remove_event_bus(self)

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


class AbstractAsyncEventBus(AbstractEventBus, ABC):
    """
    Abstract base class for asynchronous event buses.
    """
    __slots__ = ()

    @abstractmethod
    async def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError()

    def bind_eventful(self, eventful: AsyncEventful) -> None:
        eventful.add_event_bus(self)

        for event, callback, priority in eventful.get_listeners():
            self.add_event_callback(event, callback, priority)

    def unbind_eventful(self, eventful: AsyncEventful) -> None:
        for event, callback, priority in eventful.get_listeners():
            self.remove_event_callback(event, callback)

        eventful.remove_event_bus(self)


class EventBus(AbstractEventBus):
    """
    Synchronous event bus which invokes event listeners in First-In-Last-Out
    (FILO) order.
    """
    __slots__ = ()

    def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        self._dispatch_event('event', event, args, kwargs)
        self._dispatch_event(event, *args, **kwargs)

    def _dispatch_event(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        for callbacks in self.get_event_callbacks(event):
            for callback in callbacks:
                try:
                    callback(*args, **kwargs)
                except KeyboardInterrupt:
                    raise
                except Exception as error:
                    self.on_dispatch_error(event, error, args, kwargs)


class AsyncEventBus(AbstractAsyncEventBus):
    """
    Asynchronous event bus which invokes synchronous and asynchronous event
    listeners in First-In-Last-Out (FILO) order.
    """
    __slots__ = ()

    async def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        await self._dispatch_event('event', event, args, kwargs)
        await self._dispatch_event(event, *args, **kwargs)

    async def _dispatch_event(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        for callbacks in self.get_event_callbacks(event):
            futures = []  # type: list[Awaitable]
            errors = []   # type: list[Exception]

            # invoke all callback functions and collect all awaitable futures
            for callback in callbacks:
                try:
                    future = callback(*args, **kwargs)
                    if isawaitable(future):
                        futures.append(future)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    errors.append(e)

            # wait for all awaitable futures to complete
            if futures:
                results = await asyncio.gather(*futures, return_exceptions=True)
                errors += list(filter(None, results))

            # handle all uncaught exceptions
            for error in errors:
                if isinstance(error, KeyboardInterrupt):
                    raise

                self.on_dispatch_error(event, error, args, kwargs)


class ThreadedEventBus(AbstractEventBus):
    """
    Threaded event bus which invokes exclusively synchronous event
    listeners in First-In-First-Out (FIFO) order on separate threads.
    """
    __slots__ = (
        '_max_workers',
        '_dispatch_queue',
        '_dispatch_thread',
        '_running_lock',
        '_is_running',
    )

    def __init__(
        self,
        default_priority: int = DEFAULT_PRIORITY,
        max_workers: int = None,
    ) -> None:
        """
        Create a new threaded event bus to receive and dispatch events to callback
        functions.

        **Warning:**
        Event listeners are invoked from separate threads when events are emitted.

        :param default_priority: The default priority value to assign to event listeners.
        :param max_workers:      The maximum number of threads that can be used to dispatch events.
        """
        super().__init__(default_priority)

        self._max_workers = max_workers
        self._dispatch_queue = Queue()
        self._dispatch_thread = None  # type: Thread | None
        self._running_lock = Lock()
        self._is_running = False

    @property
    def running(self) -> bool:
        """
        Whether the event bus is currently running.
        """
        return self._is_running

    def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event into the event bus to invoke all associated event
        listeners with the supplied arguments.

        :param event:  The event name to invoke listeners of.
        :param args:   The arguments to invoke event listeners with.
        :param kwargs: The keyword arguments to invoke event listeners with.
        """
        with self._running_lock:
            if not self._is_running:
                return

            self._dispatch_queue.put_nowait((event, args, kwargs))

    def add_event_callback(self, event: str, /, callback: FuncT, priority: int = None) -> None:
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
            raise TypeError(f'ThreadedEventBus event listener {callback.__qualname__} cannot be a coroutine function.')

        super().add_event_callback(event, callback, priority)

    def start(self) -> None:
        """
        Start the event bus to process new events.

        :raise RuntimeError: If the event bus is already running.
        """
        with self._running_lock:
            if self._is_running:
                raise RuntimeError('Event bus is already running.')

            self._is_running = True

        self._start_dispatch_worker()

    def shutdown(self) -> None:
        """
        Stop the event bus from processing new events.

        :raise RuntimeError: If the event bus is not running.
        """
        with self._running_lock:
            if not self._is_running:
                raise RuntimeError('Event bus is already shutdown.')

            self._is_running = False

        self._dispatch_queue.put_nowait(Sentinel.SHUTDOWN)
        self._dispatch_thread.join()
        self._dispatch_thread = None

    def wait_for_idle(self) -> None:
        """
        Blocks until all emitted events have been processed.
        """
        self._dispatch_queue.join()

    def _start_dispatch_worker(self) -> None:
        """
        Start a new thread to manage the dispatch loop.
        """
        self._dispatch_thread = Thread(
            name='event-bus-loop',
            target=self._dispatch_loop,
            daemon=True,
        )
        self._dispatch_thread.start()

    def _dispatch_loop(self) -> None:
        with ThreadPoolExecutor(
            max_workers=self._max_workers,
            thread_name_prefix='event-bus-worker',
        ) as executor:
            while True:
                next_item = self._dispatch_queue.get()

                if next_item is Sentinel.SHUTDOWN:
                    self._dispatch_queue.task_done()
                    break

                event, args, kwargs = next_item

                self._dispatch_event(executor, 'event', event, args, kwargs)
                self._dispatch_event(executor, event, *args, **kwargs)

                self._dispatch_queue.task_done()

    def _dispatch_event(
        self,
        executor: ThreadPoolExecutor,
        event: str,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        for callbacks in self.get_event_callbacks(event):
            futures = {executor.submit(f, *args, **kwargs) for f in callbacks}
            for future in as_completed(futures):
                try:
                    future.result()
                except (KeyboardInterrupt, MemoryError):
                    raise
                except Exception as error:
                    self.on_dispatch_error(event, error, args, kwargs)

    def __enter__(self) -> Self:
        if not self._is_running:
            self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._is_running:
            self.shutdown()
