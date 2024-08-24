"""
This example covers the basic setup of a threaded event bus.
"""
import time
from threading import Lock, current_thread

from events import ThreadedEventBus

print_lock = Lock()


def greeting_factory():

    def on_sync_greeting(name: str, seconds: float):
        """
        Event listener which greets received names after a delay!
        """
        time.sleep(seconds)

        thread_name = current_thread().name

        with print_lock:
            print(f'[{thread_name}] Hello, {name}!')

    return on_sync_greeting


def main():
    # Create the event bus (and start it)
    with ThreadedEventBus() as bus:

        # Subscribe event listeners
        for _ in range(5):
            bus.add_event_callback('greeting', greeting_factory())

        # Publish events
        bus.emit('greeting', 'world', seconds=1)


if __name__ == '__main__':
    main()
