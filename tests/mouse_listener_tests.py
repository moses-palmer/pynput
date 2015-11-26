import unittest

import pynput.mouse
import time

from . import notify


class MouseListenerTest(unittest.TestCase):
    #: The minimum number of events to accumulate before checking for changes
    CHANGE_MIN_EVENTS = 50

    @classmethod
    def setUpClass(self):
        notify(
            'This test case is interactive, so you must follow the '
            'instructions on screen')

    def assertEvent(self, info_message, failure_message, *args, **kwargs):
        """Asserts that a specific event is emitted.

        :param str info_message: The message to display.

        :param str failure_message: The message to display upon failure.

        :param args: Arguments to pass to :class:`pynput.mouse.Listener`.

        :param kwargs: Arguments to pass to :class:`pynput.mouse.Listener`.
        """
        notify(info_message)

        success = False
        listener = pynput.mouse.Listener(*args, **kwargs)
        with listener:
            for _ in range(30):
                time.sleep(0.1)
                if not listener.running:
                    success = True
                    break

        self.assertTrue(
            success,
            failure_message)

    def assertChange(self, info_message, failure_message, **callbacks):
        """Asserts that the callback returns true for at least two thirds of
        the elements.

        :param str info_message: The message to display.

        :param str failure_message: The message to display upon failure.

        :param args: Arguments to pass to :class:`pynput.mouse.Listener`.

        :param callbacks: The callbacks for checking whether change has
            occurred.
        """
        events = ([], [], [])

        def handler(index, name):
            callback = callbacks.get(name, None)

            def inner(*a):
                cache = events[index]
                cache.append(a)

                total_length = len(cache)
                if total_length > self.CHANGE_MIN_EVENTS:
                    change_length = len([
                        None
                        for i, b in enumerate(cache[1:])
                        if callback(cache[i], b)])

                    if change_length > (2 * total_length) / 3:
                        return False

            return inner if callback else None

        notify(info_message)
        with pynput.mouse.Listener(
                on_move=handler(0, 'on_move'),
                on_click=handler(1, 'on_click'),
                on_scroll=handler(2, 'on_scroll')) as listener:
            for _ in range(30):
                time.sleep(0.1)
                if not listener.running:
                    notify('Stop')
                    time.sleep(1.0)
                    return

        # Unconditionally fail
        self.assertTrue(False, failure_message)

    def test_move(self):
        """Tests that move events are emitted at all"""
        self.assertChange(
            'Move mouse pointer',
            'Failed to register movement',
            on_move=lambda a, b: True)

    def test_left(self):
        """Tests that move left events are emitted correctly"""
        self.assertChange(
            'Move mouse pointer left',
            'Failed to register movement',
            on_move=lambda a, b: b[0] < a[0])

    def test_right(self):
        """Tests that move right events are emitted correctly"""
        self.assertChange(
            'Move mouse pointer right',
            'Failed to register movement',
            on_move=lambda a, b: b[0] > a[0])

    def test_up(self):
        """Tests that move up events are emitted correctly"""
        self.assertChange(
            'Move mouse pointer up',
            'Failed to register movement',
            on_move=lambda a, b: b[1] < a[1])

    def test_down(self):
        """Tests that move down events are emitted correctly"""
        self.assertChange(
            'Move mouse pointer down',
            'Failed to register movement',
            on_move=lambda a, b: b[1] > a[1])

    def test_click_left(self):
        """Tests that left click events are emitted"""
        self.assertEvent(
            'Click left mouse button',
            'No left click registered',
            on_click=lambda x, y, button, pressed: not (
                pressed and button == pynput.mouse.Controller.Button.left))

    def test_click_right(self):
        """Tests that right click events are emitted"""
        self.assertEvent(
            'Click right mouse button',
            'No right click registered',
            on_click=lambda x, y, button, pressed: not (
                pressed and button == pynput.mouse.Controller.Button.right))

    def test_scroll_up(self):
        """Tests that scroll up events are emitted"""
        self.assertEvent(
            'Scroll up',
            'No scroll up registered',
            on_scroll=lambda x, y, dx, dy: not (
                dy > 0))

    def test_scroll_down(self):
        """Tests that scroll down events are emitted"""
        self.assertEvent(
            'Scroll down',
            'No scroll down registered',
            on_scroll=lambda x, y, dx, dy: not (
                dy < 0))
