import pytest

# noinspection PyProtectedMember
from events.listeners import (
    _EventListener as EventListener,
    EventListeners,
)


def callback_a(): pass
def callback_b(): pass


@pytest.fixture
def default_priority():
    return 10


@pytest.fixture
def listeners(default_priority: int):
    return EventListeners(default_priority)


class TestEventListener:

    def test_equals_same_callback_same_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_a, priority=0)
        assert a == b

    def test_equals_same_callback_different_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_a, priority=1)
        assert a == b

    def test_equals_different_callback_same_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_b, priority=0)
        assert a != b

    def test_equals_different_callback_different_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_b, priority=1)
        assert a != b

    def test_equals_wrong_type(self):
        a = EventListener(callback_a, priority=0)
        b = 'string'
        assert a != b

    def test_compare_same_callback_same_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_a, priority=0)
        assert not a < b, f'{a!r} less than {b!r}'

    def test_compare_same_callback_higher_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_a, priority=1)
        assert a < b

    def test_compare_same_callback_lower_priority(self):
        a = EventListener(callback_a, priority=1)
        b = EventListener(callback_a, priority=0)
        assert not a < b, f'{a!r} less than {b!r}'

    def test_compare_different_callback_same_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_b, priority=0)
        assert not a < b, f'{a!r} less than {b!r}'

    def test_compare_different_callback_higher_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_b, priority=1)
        assert a < b

    def test_compare_different_callback_lower_priority(self):
        a = EventListener(callback_a, priority=1)
        b = EventListener(callback_b, priority=0)
        assert not a < b, f'{a!r} less than {b!r}'

    def test_compare_wrong_type(self):
        a = EventListener(callback_a, priority=0)
        b = 'string'
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            a.__lt__(b)


class TestEventListeners:

    def test_priority_default_type(self, listeners, default_priority):
        priority = listeners.priority(None)
        assert priority == default_priority

    @pytest.mark.parametrize('priority', [-20, -1, 0, 1, 10, 500])
    def test_priority_int_value(self, listeners, priority):
        new_priority = listeners.priority(priority)
        assert priority == new_priority

    @pytest.mark.parametrize('priority', ['11', 25.8, callback_a])
    def test_priority_wrong_type(self, listeners, priority):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            listeners.priority(priority)

    def test_get_event_callbacks(self, listeners, default_priority):
        listeners.add_event_callback('event', callback_a, default_priority)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_get_event_callbacks_empty(self, listeners):
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ()

    def test_get_event_callbacks_same_priority(self, listeners):
        listeners.add_event_callback('event', callback_a, priority=1)
        listeners.add_event_callback('event', callback_b, priority=1)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_a, callback_b),)

    def test_get_event_callbacks_diff_priority(self, listeners):
        listeners.add_event_callback('event', callback_a, priority=2)
        listeners.add_event_callback('event', callback_b, priority=1)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_b,), (callback_a,))

    def test_get_event_callbacks_duplicate(self, listeners, default_priority):
        listeners.add_event_callback('event', callback_a, default_priority)
        listeners.add_event_callback('event', callback_a, default_priority)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_get_event_callbacks_multi_events(self, listeners, default_priority):
        listeners.add_event_callback('event', callback_a, default_priority)
        listeners.add_event_callback('other', callback_a, default_priority)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_get_event_callbacks_diff_event(self, listeners, default_priority):
        listeners.add_event_callback('other', callback_a, default_priority)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ()

    def test_get_event_callbacks_removed(self, listeners, default_priority):
        listeners.add_event_callback('event', callback_a, default_priority)
        listeners.remove_event_callback('event', callback_a)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ()

    def test_get_event_callbacks_wrong_type(self, listeners):
        # noinspection PyTypeChecker
        callbacks = listeners.get_event_callbacks(15)
        assert callbacks == ()

    def test_add_event_callback(self, listeners, default_priority):
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ()

        listeners.add_event_callback('event', callback_a, default_priority)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

    def test_add_event_callback_new_priority(self, listeners):
        listeners.add_event_callback('event', callback_a, priority=1)
        listeners.add_event_callback('event', callback_b, priority=2)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_a,), (callback_b,))

        listeners.add_event_callback('event', callback_a, priority=2)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_b, callback_a),)

        listeners.add_event_callback('event', callback_b, priority=1)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_b,), (callback_a,))

    def test_remove_event_callback(self, listeners, default_priority):
        listeners.add_event_callback('event', callback_a, default_priority)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ((callback_a,),)

        listeners.remove_event_callback('event', callback_a)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ()

    def test_remove_event_callback_missing(self, listeners):
        listeners.remove_event_callback('event', callback_a)
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ()

    def test_remove_event_callback_wrong_type(self, listeners):
        # noinspection PyTypeChecker
        listeners.remove_event_callback('event', 'callback')
        callbacks = listeners.get_event_callbacks('event')
        assert callbacks == ()
