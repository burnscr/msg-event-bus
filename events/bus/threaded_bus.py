from __future__ import annotations

__all__ = 'ThreadedEventBus',

from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Lock, Thread
from typing import TYPE_CHECKING

from events.abc import AbstractEventBus, DEFAULT_PRIORITY
from events._utils import Sentinel

if TYPE_CHECKING:
    from typing_extensions import Self
    from typing import Any


class ThreadedEventBus(AbstractEventBus):
    """
    Threaded event bus which invokes event listeners in First-In-First-Out
    (FIFO) order on separate threads.
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
                    self.error_callback(event, error, args, kwargs)

    def __enter__(self) -> Self:
        if not self._is_running:
            self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._is_running:
            self.shutdown()
