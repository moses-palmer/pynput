import pynput.mouse
import time

from . import EventTest


class MouseListenerTest(EventTest):
    NOTIFICATION = (
        'This test case is interactive, so you must follow the instructions '
        'on screen.\n'
        'You do not have to perform any actions on this specific window.')
    LISTENER_CLASS = pynput.mouse.Listener

    def test_stop(self):
        """Tests that stopping the listener from a different thread works"""
        listener = self.listener()

        listener.start()
        listener.wait()
        self.notify('Move mouse, click button or scroll')
        listener.stop()

        time.sleep(1)

    def test_stop_no_wait(self):
        """Tests that stopping the listener from a different thread without
        waiting for the listener to start works"""
        listener = self.listener()

        listener.start()
        self.notify('Move mouse, click button or scroll')
        listener.stop()

        time.sleep(1)

    def test_move(self):
        """Tests that move events are emitted at all"""
        self.notify('Move mouse pointer')
        self.assert_cumulative(
            'Failed to register movement',
            on_move=lambda a, b: True)

    def test_left(self):
        """Tests that move left events are emitted correctly"""
        self.notify('Move mouse pointer left')
        self.assert_cumulative(
            'Failed to register movement',
            on_move=lambda a, b: b[0] < a[0])

    def test_right(self):
        """Tests that move right events are emitted correctly"""
        self.notify('Move mouse pointer right')
        self.assert_cumulative(
            'Failed to register movement',
            on_move=lambda a, b: b[0] > a[0])

    def test_up(self):
        """Tests that move up events are emitted correctly"""
        self.notify('Move mouse pointer up')
        self.assert_cumulative(
            'Failed to register movement',
            on_move=lambda a, b: b[1] < a[1])

    def test_down(self):
        """Tests that move down events are emitted correctly"""
        self.notify('Move mouse pointer down')
        self.assert_cumulative(
            'Failed to register movement',
            on_move=lambda a, b: b[1] > a[1])

    def test_click_left(self):
        """Tests that left click events are emitted"""
        self.notify('Click left mouse button')
        self.assert_stop(
            'No left click registered',
            on_click=lambda x, y, button, pressed: not (
                pressed and button == pynput.mouse.Button.left))

    def test_click_right(self):
        """Tests that right click events are emitted"""
        self.notify('Click right mouse button')
        self.assert_stop(
            'No right click registered',
            on_click=lambda x, y, button, pressed: not (
                pressed and button == pynput.mouse.Button.right))

    def test_scroll_up(self):
        """Tests that scroll up events are emitted"""
        self.notify('Scroll up')
        self.assert_stop(
            'No scroll up registered',
            on_scroll=lambda x, y, dx, dy: not (
                dy > 0))

    def test_scroll_down(self):
        """Tests that scroll down events are emitted"""
        self.notify('Scroll down')
        self.assert_stop(
            'No scroll down registered',
            on_scroll=lambda x, y, dx, dy: not (
                dy < 0))

    def test_reraise(self):
        """Tests that exception are reraised"""
        class MyException(Exception): pass

        def on_click(x, y, button, pressed):
            raise MyException()

        with self.assertRaises(MyException):
            with pynput.mouse.Listener(
                    on_click=on_click) as l:
                self.notify('Click any button')
                l.join()
