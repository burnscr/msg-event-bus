from __future__ import annotations

__all__ = 'AsyncEventBus',

import asyncio
from inspect import isawaitable
from typing import TYPE_CHECKING

from events.abc import AbstractAsyncEventBus

if TYPE_CHECKING:
    from typing import Any, Awaitable


class AsyncEventBus(AbstractAsyncEventBus):
    """
    Asynchronous event bus which invokes synchronous and asynchronous event
    listeners in First-In-Last-Out (FILO) order.
    """
    __slots__ = ()

    async def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event into the event bus to invoke all associated event
        listeners with the supplied arguments.

        :param event:  The event name to invoke listeners of.
        :param args:   The arguments to invoke event listeners with.
        :param kwargs: The keyword arguments to invoke event listeners with.
        """
        await asyncio.gather(
            self._dispatch_event('event', event, args, kwargs),
            self._dispatch_event(event, *args, **kwargs),
        )

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

                self.error_callback(event, error, args, kwargs)
