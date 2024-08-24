"""
This example covers the basic setup of an asynchronous event bus using
asynchronous eventful classes.
"""
import asyncio

from events import AsyncEventful, event_listener
from events.bus import AsyncEventBus


class Greeter(AsyncEventful):

    @event_listener('greeting')
    async def on_async_greeting(self, name: str):
        """
        Event listener which greets received names!
        """
        await asyncio.sleep(0.1)
        print(f'Hello, {name}! (async)')

    # Synchronous event listeners can also be used

    @event_listener('greeting')
    def on_sync_greeting(self, name: str):
        """
        Event listener which greets received names!
        """
        print(f'Hello, {name}! (sync)')


async def main():
    # Create the event bus
    bus = AsyncEventBus()

    # Subscribe event listeners
    greeter = Greeter()
    bus.bind_eventful(greeter)

    # Publish events
    await bus.emit('greeting', 'world')


if __name__ == '__main__':
    asyncio.run(main())
