"""
This example covers the basic setup of a threaded event bus using
eventful classes.
"""
import time
from threading import Lock, current_thread

from events.bus import ThreadedEventBus
from events import Eventful, event_listener

print_lock = Lock()


class Greeter(Eventful):

    @event_listener('greeting')
    def on_sync_greeting(self, name: str, seconds: float):
        """
        Event listener which greets received names after a delay!
        """
        time.sleep(seconds)

        thread_name = current_thread().name

        with print_lock:
            print(f'[{thread_name}] Hello, {name}!')


def main():
    # Create the event bus
    with ThreadedEventBus() as bus:

        # Subscribe event listeners
        for _ in range(5):
            bus.bind_eventful(Greeter())

        # Publish events
        bus.emit('greeting', 'world', seconds=1)


if __name__ == '__main__':
    main()
