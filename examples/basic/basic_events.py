"""
This example covers the basic setup of a synchronous event bus.
"""
from events.bus import EventBus


def on_greeting(name: str):
    """
    Event listener which greets received names!
    """
    print(f'Hello, {name}!')


def main():
    # Create the event bus
    bus = EventBus()

    # Subscribe event listeners
    bus.add_event_callback('greeting', on_greeting)

    # Publish events
    bus.emit('greeting', 'world')


if __name__ == '__main__':
    main()
