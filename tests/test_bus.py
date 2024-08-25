import pytest

# noinspection PyProtectedMember
from events.abc.bus import (
    DEFAULT_PRIORITY,
    _BaseEventBus as BaseEventBus,
    AbstractEventBus,
    AbstractAsyncEventBus,
)
from events import Eventful, AsyncEventful, event_listener


class DummyAbstractEventBus(AbstractEventBus):
    def emit(self, event, /, *args, **kwargs): pass


class DummyAbstractAsyncEventBus(AbstractAsyncEventBus):
    async def emit(self, event, /, *args, **kwargs): pass


def callback_a(): pass


def callback_b(): pass


async def async_callback(): pass


@pytest.fixture
def base_event_bus():
    return BaseEventBus()


@pytest.fixture
def abstract_event_bus():
    return DummyAbstractEventBus()


@pytest.fixture
def abstract_async_event_bus():
    return DummyAbstractAsyncEventBus()


class TestBaseEventBus:

    def test_default_priority(self, base_event_bus: BaseEventBus):
        assert base_event_bus.default_priority == DEFAULT_PRIORITY

    def test_get_event_callbacks(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('event', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_get_event_callbacks_empty(self, base_event_bus: BaseEventBus):
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_get_event_callbacks_same_priority(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('event', callback_a, priority=1)
        base_event_bus.add_event_callback('event', callback_b, priority=1)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a, callback_b),)

    def test_get_event_callbacks_diff_priority(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('event', callback_a, priority=2)
        base_event_bus.add_event_callback('event', callback_b, priority=1)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_b,), (callback_a,))

    def test_get_event_callbacks_duplicate(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('event', callback_a)
        base_event_bus.add_event_callback('event', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_get_event_callbacks_multi_events(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('event', callback_a)
        base_event_bus.add_event_callback('other', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_get_event_callbacks_diff_event(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('other', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_get_event_callbacks_removed(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('event', callback_a)
        base_event_bus.remove_event_callback('event', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_get_event_callbacks_wrong_type(self, base_event_bus: BaseEventBus):
        # noinspection PyTypeChecker
        callbacks = base_event_bus.get_event_callbacks(15)
        assert callbacks == ()

    def test_add_event_callback(self, base_event_bus: BaseEventBus):
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ()

        base_event_bus.add_event_callback('event', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_add_event_callback_new_priority(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('event', callback_a, priority=1)
        base_event_bus.add_event_callback('event', callback_b, priority=2)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a,), (callback_b,))

        base_event_bus.add_event_callback('event', callback_a, priority=2)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_b, callback_a),)

        base_event_bus.add_event_callback('event', callback_b, priority=1)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_b,), (callback_a,))

    def test_remove_event_callback(self, base_event_bus: BaseEventBus):
        base_event_bus.add_event_callback('event', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

        base_event_bus.remove_event_callback('event', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_remove_event_callback_missing(self, base_event_bus: BaseEventBus):
        base_event_bus.remove_event_callback('event', callback_a)
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_remove_event_callback_wrong_type(self, base_event_bus: BaseEventBus):
        # noinspection PyTypeChecker
        base_event_bus.remove_event_callback('event', 'callback')
        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_on(self, base_event_bus: BaseEventBus):
        @base_event_bus.on('event')
        def callback():
            pass

        callbacks = base_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback,),)


class TestAbstractEventBus:

    def test_add_event_callback(self, abstract_event_bus: AbstractEventBus):
        abstract_event_bus.add_event_callback('event', callback_a)
        callbacks = abstract_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_add_event_callback_async(self, abstract_event_bus: AbstractEventBus):
        with pytest.raises(TypeError):
            abstract_event_bus.add_event_callback('event', async_callback)

    def test_bind_eventful(self, abstract_event_bus: AbstractEventBus):
        class DummyEventful(Eventful):
            @event_listener('event')
            def callback(self): pass

        eventful = DummyEventful()
        abstract_event_bus.bind_eventful(eventful)
        assert abstract_event_bus in eventful.get_event_buses()

        callbacks = abstract_event_bus.get_event_callbacks('event')
        assert callbacks == ((eventful.callback,),)

    def test_bind_eventful_empty(self, abstract_event_bus: AbstractEventBus):
        class DummyEventful(Eventful):
            pass

        eventful = DummyEventful()
        abstract_event_bus.bind_eventful(eventful)
        assert abstract_event_bus in eventful.get_event_buses()

        callbacks = abstract_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_bind_eventful_async(self, abstract_event_bus: AbstractEventBus):
        class DummyAsyncEventful(AsyncEventful):
            pass

        eventful = DummyAsyncEventful()
        with pytest.raises(TypeError):
            abstract_event_bus.bind_eventful(eventful)

    def test_bind_eventful_async_callback(self, abstract_event_bus: AbstractEventBus):
        class DummyEventful(Eventful):
            @event_listener('event')
            async def callback(self): pass

        eventful = DummyEventful()
        with pytest.raises(TypeError):
            abstract_event_bus.bind_eventful(eventful)

    def test_bind_eventful_multi_callback(self, abstract_event_bus: AbstractEventBus):
        class DummyEventful(Eventful):
            @event_listener('event')
            def callback_a(self): pass

            @event_listener('event')
            def callback_b(self): pass

        eventful = DummyEventful()
        abstract_event_bus.bind_eventful(eventful)
        assert abstract_event_bus in eventful.get_event_buses()

        callbacks = abstract_event_bus.get_event_callbacks('event')
        assert callbacks == ((eventful.callback_a, eventful.callback_b),)

    def test_unbind_eventful(self, abstract_event_bus: AbstractEventBus):
        class DummyEventful(Eventful):
            @event_listener('event')
            def callback(self): pass

        eventful = DummyEventful()
        abstract_event_bus.bind_eventful(eventful)
        assert abstract_event_bus in eventful.get_event_buses()

        abstract_event_bus.unbind_eventful(eventful)
        assert abstract_event_bus not in eventful.get_event_buses()

        callbacks = abstract_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_unbind_eventful_missing(self, abstract_event_bus: AbstractEventBus):
        class DummyEventful(Eventful):
            pass

        eventful = DummyEventful()
        abstract_event_bus.unbind_eventful(eventful)
        assert abstract_event_bus not in eventful.get_event_buses()

        callbacks = abstract_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_unbind_eventful_async(self, abstract_event_bus: AbstractEventBus):
        class DummyAsyncEventful(AsyncEventful):
            pass

        eventful = DummyAsyncEventful()
        with pytest.raises(TypeError):
            abstract_event_bus.unbind_eventful(eventful)

    def test_unbind_eventful_wrong_type(self, abstract_event_bus: AbstractEventBus):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            abstract_event_bus.unbind_eventful('eventful')


class TestAbstractAsyncEventBus:

    def test_add_event_callback_async(self, abstract_async_event_bus: AbstractAsyncEventBus):
        abstract_async_event_bus.add_event_callback('event', async_callback)
        callbacks = abstract_async_event_bus.get_event_callbacks('event')
        assert callbacks == ((async_callback,),)

    def test_add_event_callback_sync(self, abstract_async_event_bus: AbstractAsyncEventBus):
        abstract_async_event_bus.add_event_callback('event', callback_a)
        callbacks = abstract_async_event_bus.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_bind_eventful(self, abstract_async_event_bus: AbstractAsyncEventBus):
        class DummyAsyncEventful(AsyncEventful):
            @event_listener('event')
            async def callback(self): pass

        eventful = DummyAsyncEventful()
        abstract_async_event_bus.bind_eventful(eventful)
        assert abstract_async_event_bus in eventful.get_event_buses()

        callbacks = abstract_async_event_bus.get_event_callbacks('event')
        assert callbacks == ((eventful.callback,),)

    def test_bind_eventful_empty(self, abstract_async_event_bus: AbstractAsyncEventBus):
        class DummyAsyncEventful(AsyncEventful):
            pass

        eventful = DummyAsyncEventful()
        abstract_async_event_bus.bind_eventful(eventful)
        assert abstract_async_event_bus in eventful.get_event_buses()

        callbacks = abstract_async_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_bind_eventful_sync(self, abstract_async_event_bus: AbstractAsyncEventBus):
        class DummyEventful(Eventful):
            pass

        eventful = DummyEventful()
        with pytest.raises(TypeError):
            abstract_async_event_bus.bind_eventful(eventful)

    def test_bind_eventful_sync_callback(self, abstract_async_event_bus: AbstractAsyncEventBus):
        class DummyAsyncEventful(AsyncEventful):
            @event_listener('event')
            def callback(self): pass

        eventful = DummyAsyncEventful()
        abstract_async_event_bus.bind_eventful(eventful)
        assert abstract_async_event_bus in eventful.get_event_buses()

        callbacks = abstract_async_event_bus.get_event_callbacks('event')
        assert callbacks == ((eventful.callback,),)

    def test_bind_eventful_multi_callback(self, abstract_async_event_bus: AbstractAsyncEventBus):
        class DummyAsyncEventful(AsyncEventful):
            @event_listener('event')
            async def callback_a(self): pass
            @event_listener('event')
            async def callback_b(self): pass

        eventful = DummyAsyncEventful()
        abstract_async_event_bus.bind_eventful(eventful)
        assert abstract_async_event_bus in eventful.get_event_buses()

        callbacks = abstract_async_event_bus.get_event_callbacks('event')
        assert callbacks == ((eventful.callback_a, eventful.callback_b),)

    def test_unbind_eventful(self, abstract_async_event_bus: AbstractAsyncEventBus):
        class DummyAsyncEventful(AsyncEventful):
            @event_listener('event')
            async def callback(self): pass

        eventful = DummyAsyncEventful()
        abstract_async_event_bus.bind_eventful(eventful)
        assert abstract_async_event_bus in eventful.get_event_buses()

        abstract_async_event_bus.unbind_eventful(eventful)
        assert abstract_async_event_bus not in eventful.get_event_buses()

        callbacks = abstract_async_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_unbind_eventful_missing(self, abstract_async_event_bus: AbstractAsyncEventBus):
        class DummyAsyncEventful(AsyncEventful):
            pass

        eventful = DummyAsyncEventful()
        abstract_async_event_bus.unbind_eventful(eventful)
        assert abstract_async_event_bus not in eventful.get_event_buses()

        callbacks = abstract_async_event_bus.get_event_callbacks('event')
        assert callbacks == ()

    def test_unbind_eventful_sync(self, abstract_async_event_bus: AbstractAsyncEventBus):
        class DummyEventful(Eventful):
            pass

        eventful = DummyEventful()
        with pytest.raises(TypeError):
            abstract_async_event_bus.unbind_eventful(eventful)

    def test_unbind_eventful_wrong_type(self, abstract_async_event_bus: AbstractAsyncEventBus):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            abstract_async_event_bus.unbind_eventful('eventful')
