from unittest import TestCase

from events.listeners import (
    _EventListener as EventListener,
    EventListeners
)


def callback_a():
    pass


def callback_b():
    pass


class TestEventListener(TestCase):

    def test_equals_same_callback_same_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_a, priority=0)
        self.assertEqual(a, b)

    def test_equals_same_callback_different_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_a, priority=1)
        self.assertEqual(a, b)

    def test_equals_different_callback_same_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_b, priority=0)
        self.assertNotEqual(a, b)

    def test_equals_different_callback_different_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_b, priority=1)
        self.assertNotEqual(a, b)

    def test_equals_unsupported_type(self):
        a = EventListener(callback_a, priority=0)
        b = 'string'
        self.assertNotEqual(a, b)

    def test_compare_same_callback_same_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_a, priority=0)
        self.assertFalse(a < b, f'{a!r} less than {b!r}')

    def test_compare_same_callback_higher_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_a, priority=1)
        self.assertLess(a, b)

    def test_compare_same_callback_lower_priority(self):
        a = EventListener(callback_a, priority=1)
        b = EventListener(callback_a, priority=0)
        self.assertFalse(a < b, f'{a!r} less than {b!r}')

    def test_compare_different_callback_same_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_b, priority=0)
        self.assertFalse(a < b, f'{a!r} less than {b!r}')

    def test_compare_different_callback_higher_priority(self):
        a = EventListener(callback_a, priority=0)
        b = EventListener(callback_b, priority=1)
        self.assertLess(a, b)

    def test_compare_different_callback_lower_priority(self):
        a = EventListener(callback_a, priority=1)
        b = EventListener(callback_b, priority=0)
        self.assertFalse(a < b, f'{a!r} less than {b!r}')

    def test_compare_unsupported_type(self):
        a = EventListener(callback_a, priority=0)
        b = 'string'
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            a.__lt__(b)


class TestEventListeners(TestCase):

    def setUp(self):
        self.default_priority = default_priority = 10
        self.listeners = EventListeners(default_priority)

    def test_priority_default_type(self):
        priority = self.listeners.priority(None)
        self.assertEqual(priority, self.default_priority)

    def test_priority_int_value(self):
        test_values = [-20, -1, 0, 1, 10, 500]

        for old_priority in test_values:
            with self.subTest(old_priority):

                new_priority = self.listeners.priority(old_priority)
                self.assertEqual(old_priority, new_priority)

    def test_priority_unsupported_type(self):
        test_values = ['11', 25.8, callback_a]

        for priority in test_values:
            with self.subTest(priority):

                with self.assertRaises(TypeError):
                    # noinspection PyTypeChecker
                    self.listeners.priority(priority)

    def test_get_event_callbacks_empty(self):
        callbacks = self.listeners.get_event_callbacks('missing')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_get_event_callbacks_single_item(self):
        self.listeners.add_event_callback('single', callback_a, 1)
        callbacks = self.listeners.get_event_callbacks('single')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a,),))

    def test_get_event_callbacks_multiple_items_same_priority(self):
        self.listeners.add_event_callback('multiple', callback_a, 1)
        self.listeners.add_event_callback('multiple', callback_b, 1)
        callbacks = self.listeners.get_event_callbacks('multiple')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a, callback_b),))

    def test_get_event_callbacks_multiple_items_different_priority(self):
        self.listeners.add_event_callback('multiple', callback_a, 2)
        self.listeners.add_event_callback('multiple', callback_b, 1)
        callbacks = self.listeners.get_event_callbacks('multiple')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_b,), (callback_a,)))

    def test_get_event_callbacks_single_item_duplicate_entries(self):
        self.listeners.add_event_callback('single', callback_a, 1)
        self.listeners.add_event_callback('single', callback_a, 1)
        callbacks = self.listeners.get_event_callbacks('single')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a,),))

    def test_get_event_callbacks_single_item_multiple_events(self):
        self.listeners.add_event_callback('single', callback_a, 1)
        self.listeners.add_event_callback('other', callback_a, 1)
        callbacks = self.listeners.get_event_callbacks('single')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a,),))

    def test_get_event_callbacks_empty_item_different_event(self):
        self.listeners.add_event_callback('other', callback_a, 1)
        callbacks = self.listeners.get_event_callbacks('missing')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_get_event_callbacks_emtpy_item_removed_entry(self):
        self.listeners.add_event_callback('event', callback_a, 1)
        self.listeners.remove_event_callback('event', callback_a)
        callbacks = self.listeners.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_get_event_callbacks_unexpected_type(self):
        # noinspection PyTypeChecker
        callbacks = self.listeners.get_event_callbacks(15)
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_add_event_callback_same_callback_different_priority(self):
        self.listeners.add_event_callback('event', callback_a, 1)
        self.listeners.add_event_callback('event', callback_b, 1)

        callbacks = self.listeners.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a, callback_b),))

        self.listeners.add_event_callback('event', callback_a, 2)

        callbacks = self.listeners.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_b,), (callback_a,)))

    def test_remove_event_callback(self):
        self.listeners.add_event_callback('event', callback_a, 1)

        callbacks = self.listeners.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ((callback_a,),))

        self.listeners.remove_event_callback('event', callback_a)

        callbacks = self.listeners.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())

    def test_remove_event_callback_missing(self):
        # (no exception raised)
        self.listeners.remove_event_callback('event', callback_a)

        callbacks = self.listeners.get_event_callbacks('event')
        # noinspection PyTypeChecker
        self.assertTupleEqual(callbacks, ())
