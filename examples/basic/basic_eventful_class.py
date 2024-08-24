"""
This example covers the basic setup of a synchronous event bus using
eventful classes.
"""
from events import Eventful, event_listener
from events.bus import EventBus


class Greeter(Eventful):

    @event_listener('greeting')
    def on_greeting(self, name: str):
        """
        Event listener which greets received names!
        """
        print(f'Hello, {name}!')


def main():
    # Create the event bus
    bus = EventBus()

    # Subscribe event listeners
    greeter = Greeter()
    bus.bind_eventful(greeter)

    # Publish events
    bus.emit('greeting', 'world')


if __name__ == '__main__':
    main()
