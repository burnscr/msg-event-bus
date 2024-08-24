"""
This example covers the basic setup of an asynchronous event bus.
"""
import asyncio

from events.bus import AsyncEventBus


async def on_async_greeting(name: str):
    """
    Event listener which greets received names!
    """
    await asyncio.sleep(0.1)
    print(f'Hello, {name}! (async)')


# Synchronous event listeners can also be used

def on_sync_greeting(name: str):
    """
    Event listener which greets received names!
    """
    print(f'Hello, {name}! (sync)')


async def main():
    # Create the event bus
    bus = AsyncEventBus()

    # Subscribe event listeners
    bus.add_event_callback('greeting', on_async_greeting)
    bus.add_event_callback('greeting', on_sync_greeting)

    # Publish events
    await bus.emit('greeting', 'world')


if __name__ == '__main__':
    asyncio.run(main())
