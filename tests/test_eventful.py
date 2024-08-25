import pytest

from events.bus import EventBus, AsyncEventBus
from events import Eventful, AsyncEventful, event_listener


class EmptyEventful(Eventful):
    pass


class SingleEventful(Eventful):
    @event_listener('event')
    def on_event(self): pass


class MultiSameEventful(Eventful):
    @event_listener('event')
    def on_event_a(self): pass
    @event_listener('event')
    def on_event_b(self): pass


class MultiDiffEventful(Eventful):
    @event_listener('event_a')
    def on_event_a(self): pass
    @event_listener('event_b')
    def on_event_b(self): pass


class TestEventful:

    # def test_emit(self):
    #     assert False

    def test_get_listeners(self):
        eventful = SingleEventful()
        listeners = eventful.get_listeners()
        assert listeners == [('event', eventful.on_event, None)]

    def test_get_listeners_empty(self):
        eventful = EmptyEventful()
        listeners = eventful.get_listeners()
        assert listeners == []

    def test_get_listeners_same(self):
        eventful = MultiSameEventful()
        listeners = eventful.get_listeners()
        assert listeners == [
            ('event', eventful.on_event_a, None),
            ('event', eventful.on_event_b, None),
        ]

    def test_get_listeners_unique(self):
        eventful = MultiDiffEventful()
        listeners = eventful.get_listeners()
        assert listeners == [
            ('event_a', eventful.on_event_a, None),
            ('event_b', eventful.on_event_b, None),
        ]

    def test_get_event_buses(self):
        bus = EventBus()
        eventful = EmptyEventful()
        eventful.add_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus])

    def test_get_event_buses_empty(self):
        eventful = EmptyEventful()
        buses = eventful.get_event_buses()
        assert buses == frozenset()

    def test_get_event_buses_multiple(self):
        bus_a = EventBus()
        bus_b = EventBus()
        eventful = EmptyEventful()
        eventful.add_event_bus(bus_a)
        eventful.add_event_bus(bus_b)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus_a, bus_b])

    def test_add_event_bus(self):
        bus = EventBus()
        eventful = EmptyEventful()

        buses = eventful.get_event_buses()
        assert buses == frozenset()

        eventful.add_event_bus(bus)
        assert eventful.get_event_buses() == frozenset([bus])

    def test_add_event_bus_multiple(self):
        bus_a = EventBus()
        bus_b = EventBus()
        eventful = EmptyEventful()

        buses = eventful.get_event_buses()
        assert buses == frozenset()

        eventful.add_event_bus(bus_a)
        eventful.add_event_bus(bus_b)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus_a, bus_b])

    def test_add_event_bus_duplicate(self):
        bus = EventBus()
        eventful = EmptyEventful()
        eventful.add_event_bus(bus)
        eventful.add_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus])

    def test_add_event_bus_async(self):
        bus = AsyncEventBus()
        eventful = EmptyEventful()
        with pytest.raises(TypeError):
            eventful.add_event_bus(bus)

    @pytest.mark.parametrize('bus', ['bus', None, 15, EventBus])
    def test_add_event_bus_wrong_type(self, bus):
        eventful = EmptyEventful()
        with pytest.raises(TypeError):
            eventful.add_event_bus(bus)

    def test_remove_event_bus(self):
        bus = EventBus()
        eventful = EmptyEventful()

        eventful.add_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus])

        eventful.remove_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset()

    def test_remove_event_bus_missing(self):
        bus = EventBus()
        eventful = EmptyEventful()
        eventful.remove_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset()

    @pytest.mark.parametrize('bus', ['bus', None, 15, EventBus])
    def test_remove_event_bus_wrong_type(self, bus):
        eventful = EmptyEventful()
        eventful.remove_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset()


class EmptyAsyncEventful(AsyncEventful):
    pass


class SingleAsyncEventful(AsyncEventful):
    @event_listener('event')
    async def on_event(self): pass


class MultiSameAsyncEventful(AsyncEventful):
    @event_listener('event')
    async def on_event_a(self): pass
    @event_listener('event')
    async def on_event_b(self): pass


class MultiDiffAsyncEventful(AsyncEventful):
    @event_listener('event_a')
    async def on_event_a(self): pass
    @event_listener('event_b')
    async def on_event_b(self): pass


class MultiMixedAsyncEventful(AsyncEventful):
    @event_listener('event_a')
    async def on_event_a(self): pass
    @event_listener('event_b')
    def on_event_b(self): pass


class TestAsyncEventful:

    # def test_emit(self):
    #     assert False

    def test_get_listeners(self):
        eventful = SingleAsyncEventful()
        listeners = eventful.get_listeners()
        assert listeners == [('event', eventful.on_event, None)]

    def test_get_listeners_empty(self):
        eventful = EmptyAsyncEventful()
        listeners = eventful.get_listeners()
        assert listeners == []

    def test_get_listeners_same(self):
        eventful = MultiSameAsyncEventful()
        listeners = eventful.get_listeners()
        assert listeners == [
            ('event', eventful.on_event_a, None),
            ('event', eventful.on_event_b, None),
        ]

    def test_get_listeners_unique(self):
        eventful = MultiDiffAsyncEventful()
        listeners = eventful.get_listeners()
        assert listeners == [
            ('event_a', eventful.on_event_a, None),
            ('event_b', eventful.on_event_b, None),
        ]

    def test_get_listeners_mixed(self):
        eventful = MultiMixedAsyncEventful()
        listeners = eventful.get_listeners()
        assert listeners == [
            ('event_a', eventful.on_event_a, None),
            ('event_b', eventful.on_event_b, None),
        ]

    def test_get_event_buses(self):
        bus = AsyncEventBus()
        eventful = EmptyAsyncEventful()
        eventful.add_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus])

    def test_get_event_buses_empty(self):
        eventful = EmptyAsyncEventful()
        buses = eventful.get_event_buses()
        assert buses == frozenset()

    def test_get_event_buses_multiple(self):
        bus_a = AsyncEventBus()
        bus_b = AsyncEventBus()
        eventful = EmptyAsyncEventful()
        eventful.add_event_bus(bus_a)
        eventful.add_event_bus(bus_b)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus_a, bus_b])

    def test_add_event_bus(self):
        bus = AsyncEventBus()
        eventful = EmptyAsyncEventful()

        buses = eventful.get_event_buses()
        assert buses == frozenset()

        eventful.add_event_bus(bus)
        assert eventful.get_event_buses() == frozenset([bus])

    def test_add_event_bus_multiple(self):
        bus_a = AsyncEventBus()
        bus_b = AsyncEventBus()
        eventful = EmptyAsyncEventful()

        buses = eventful.get_event_buses()
        assert buses == frozenset()

        eventful.add_event_bus(bus_a)
        eventful.add_event_bus(bus_b)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus_a, bus_b])

    def test_add_event_bus_duplicate(self):
        bus = AsyncEventBus()
        eventful = EmptyAsyncEventful()
        eventful.add_event_bus(bus)
        eventful.add_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus])

    def test_add_event_bus_sync(self):
        bus = EventBus()
        eventful = EmptyAsyncEventful()
        with pytest.raises(TypeError):
            eventful.add_event_bus(bus)

    @pytest.mark.parametrize('bus', ['bus', None, 15, AsyncEventBus])
    def test_add_event_bus_wrong_type(self, bus):
        eventful = EmptyAsyncEventful()
        with pytest.raises(TypeError):
            eventful.add_event_bus(bus)

    def test_remove_event_bus(self):
        bus = AsyncEventBus()
        eventful = EmptyAsyncEventful()

        eventful.add_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset([bus])

        eventful.remove_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset()

    def test_remove_event_bus_missing(self):
        bus = AsyncEventBus()
        eventful = EmptyAsyncEventful()
        eventful.remove_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset()

    @pytest.mark.parametrize('bus', ['bus', None, 15, AsyncEventBus])
    def test_remove_event_bus_wrong_type(self, bus):
        eventful = EmptyAsyncEventful()
        eventful.remove_event_bus(bus)
        buses = eventful.get_event_buses()
        assert buses == frozenset()
