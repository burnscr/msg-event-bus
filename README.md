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
from events.bus import EventBus

def on_greeting(name):
    print(f'Hello, {name}!')

bus = EventBus()
bus.add_event_callback('greeting', on_greeting)
bus.emit('greeting', 'world')
```

### Eventful Class

```python
from events.bus import EventBus
from events import Eventful, event_listener

class Greeter(Eventful):

    @event_listener('greeting')
    def on_greeting(self, name):
        print(f'Hello, {name}!')

        # also supports emitting new events
        self.emit('done')

bus = EventBus()
bus.bind_eventful(Greeter())
bus.emit('greeting', 'world')
```

### Callback Priority

Event listeners may declare a callback priority to influence invocation order.
Callbacks will be invoked in order of increasing priority value.

```python
from events.bus import EventBus

# Event buses may set a default priority for callbacks
bus = EventBus(default_priority=10)

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

Eventful classes may define a default priority value which is
implicitly applied to all event listeners within the class.

```python
from events.bus import EventBus
from events import Eventful, event_listener

# Greeter declares a default priority value of 1
class Greeter(Eventful, priority=1):

    # priority is explicitly set to 2
    @event_listener('greeting', priority=2)
    def informal_greeting(self, name):
        # this will be invoked last
        print(f'Hey {name}!')

    # priority is implicitly set to 1
    @event_listener('greeting')
    def formal_greeting(self, name):
        # this will be invoked first
        print(f'Hello, {name}')

bus = EventBus()
bus.bind_eventful(Greeter())
bus.emit('greeting', 'world')
```

Additional examples can be found in the [examples](examples) directory.
