from __future__ import annotations

__all__ = 'EventBus',

from typing import TYPE_CHECKING

from events.abc import AbstractEventBus

if TYPE_CHECKING:
    from typing import Any


class EventBus(AbstractEventBus):
    """
    Synchronous event bus which invokes event listeners in First-In-Last-Out
    (FILO) order.
    """
    __slots__ = ()

    def emit(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event into the event bus to invoke all associated event
        listeners with the supplied arguments.

        :param event:  The event name to invoke listeners of.
        :param args:   The arguments to invoke event listeners with.
        :param kwargs: The keyword arguments to invoke event listeners with.
        """
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
                    self.error_callback(event, error, args, kwargs)
