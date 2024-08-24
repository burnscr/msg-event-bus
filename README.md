# msg-event-bus
A modern, easy to use, feature-rich, and async ready event bus library written in Python.

## Key Features

- Support for synchronous, asynchronous, and multithreaded event handling.
- Eventful mixin for class scoped grouping of event listeners.
- Abstract base classes for custom event handling with sensible defaults.

## Installation

**Python 3.8 or higher is required**

```
git clone https://github.com/burnscr/msg-event-bus
```

## Usage

### Simple Callback

```python
import events

def on_greeting(name):
    print(f'Hello, {name}!')

bus = events.EventBus()
bus.add_event_callback('greeting', on_greeting)
bus.emit('greeting', 'world')
```

### Eventful Class

```python
import events

class Greeter(events.Eventful):

    @events.event_listener('greeting')
    def on_greeting(self, name):
        print(f'Hello, {name}!')

        # also supports emitting new events
        self.emit('done')

bus = events.EventBus()
bus.bind_eventful(Greeter())
bus.emit('greeting', 'world')
```

### Callback Priority

```python
import events

bus = events.EventBus()

@bus.on('greeting', priority=2)
def informal_greeting(name):
    # this will be invoked last
    print(f'Hey {name}!')

@bus.on('greeting', priority=1)
def formal_greeting(name):
    # this will be invoked first
    print(f'Hello, {name}')

bus.emit('greeting', 'world')
```

Additional examples can be found in the [examples](examples) directory.
