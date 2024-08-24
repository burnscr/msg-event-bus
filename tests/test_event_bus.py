from unittest import TestCase

from events.abc import AbstractEventBus
from events.eventful import Eventful
from events.listeners import event_listener


def callback_a():
    pass


def callback_b():
    pass


class DummyAbstractEventBus(AbstractEventBus):
    def emit(self, event, /, *args, **kwargs) -> None:
        raise NotImplementedError()


class DummyEventful(Eventful):

    @event_listener('event')
    def on_event(self):
        pass


class TestAbstractEventBus(TestCase):

    def setUp(self):
        self.default_priority = default_priority = 10
        self.bus = DummyAbstractEventBus(default_priority)

    def test_default_priority(self):
        self.assertEqual(self.bus.default_priority, self.default_priority)

    def test_get_event_callbacks_empty(self):
        callbacks = self.bus.get_event_callbacks('missing')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_get_event_callbacks_single_item(self):
        self.bus.add_event_callback('single', callback_a, 1)
        callbacks = self.bus.get_event_callbacks('single')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a,),))

    def test_get_event_callbacks_multiple_items_same_priority(self):
        self.bus.add_event_callback('multiple', callback_a, 1)
        self.bus.add_event_callback('multiple', callback_b, 1)
        callbacks = self.bus.get_event_callbacks('multiple')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a, callback_b),))

    def test_get_event_callbacks_multiple_items_different_priority(self):
        self.bus.add_event_callback('multiple', callback_a, 2)
        self.bus.add_event_callback('multiple', callback_b, 1)
        callbacks = self.bus.get_event_callbacks('multiple')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_b,), (callback_a,)))

    def test_get_event_callbacks_single_item_duplicate_entries(self):
        self.bus.add_event_callback('single', callback_a, 1)
        self.bus.add_event_callback('single', callback_a, 1)
        callbacks = self.bus.get_event_callbacks('single')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a,),))

    def test_get_event_callbacks_single_item_multiple_events(self):
        self.bus.add_event_callback('single', callback_a, 1)
        self.bus.add_event_callback('other', callback_a, 1)
        callbacks = self.bus.get_event_callbacks('single')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a,),))

    def test_get_event_callbacks_empty_item_different_event(self):
        self.bus.add_event_callback('other', callback_a, 1)
        callbacks = self.bus.get_event_callbacks('missing')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_get_event_callbacks_emtpy_item_removed_entry(self):
        self.bus.add_event_callback('event', callback_a, 1)
        self.bus.remove_event_callback('event', callback_a)
        callbacks = self.bus.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_get_event_callbacks_unexpected_type(self):
        # noinspection PyTypeChecker
        callbacks = self.bus.get_event_callbacks(15)
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_add_event_callback_same_callback_different_priority(self):
        self.bus.add_event_callback('event', callback_a, 1)
        self.bus.add_event_callback('event', callback_b, 1)

        callbacks = self.bus.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a, callback_b),))

        self.bus.add_event_callback('event', callback_a, 2)

        callbacks = self.bus.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_b,), (callback_a,)))

    def test_remove_event_callback(self):
        self.bus.add_event_callback('event', callback_a, 1)

        callbacks = self.bus.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a,),))

        self.bus.remove_event_callback('event', callback_a)

        callbacks = self.bus.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_remove_event_callback_missing(self):
        # (no exception raised)
        self.bus.remove_event_callback('event', callback_a)

        callbacks = self.bus.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_bind_eventful(self):
        eventful = DummyEventful()
        self.bus.bind_eventful(eventful)
        callbacks = self.bus.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((eventful.on_event,),))
