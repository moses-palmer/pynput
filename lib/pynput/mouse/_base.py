# coding=utf-8
# pynput
# Copyright (C) 2015 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import enum
import functools
import threading


class Controller(object):
    """A controller for sending virtual mouse events to the system.
    """
    class Button(enum.Enum):
        """The various buttons.

        The actual values for these items differ between platforms. Some
        platforms may have additional buttons, but these are guaranteed to be
        present everywhere.
        """
        #: The left button
        left = 1

        #: The middle button
        middle = 2

        #: The right button
        right = 3

    @property
    def position(self):
        """The current position of the mouse pointer.

        This is the tuple ``(x, y)``.
        """
        return self._position_get()

    @position.setter
    def position(self, pos):
        self._position_set(pos)

    def scroll(self, dx, dy):
        """Sends scroll events.

        :param int dx: The horizontal scroll. The units of scrolling is
            undefined.

        :param int dy: The vertical scroll. The units of scrolling is
            undefined.
        """
        self._scroll(dx, dy)

    def press(self, button):
        """Emits a button press event at the current position.

        :param Controller.Button button: The button to press.
        """
        self._press(button)

    def release(self, button):
        """Emits a button release event at the current position.

        :param Controller.Button button: The button to release.
        """
        self._release(button)

    def move(self, dx, dy):
        """Moves the mouse pointer a number of pixels from its current
        position.

        :param int x: The horizontal offset.

        :param int dy: The vertical offset.
        """
        self.position = tuple(sum(i) for i in zip(self.position, (dx, dy)))

    def click(self, button, count=1):
        """Emits a button click event at the current position.

        The default implementation sends a series a press and release events.

        :param Controller.Button button: The button to click.

        :param int count: The number of clicks to send.
        """
        with self as controller:
            for _ in range(count):
                controller.press(button)
                controller.release(button)

    def __enter__(self):
        """Begins a series of clicks.

        In the default :meth:`click` implementation, the return value of this
        method is used for the calls to :meth:`press` and :meth:`release`
        instead of ``self``.

        The default implementation is a no-op.
        """
        return self

    def __exit__(self, type, value, traceback):
        """Ends a series of clicks.
        """
        pass

    def _position_get(self):
        """The implementation of the getter for :attr:`position`.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _position_set(self, pos):
        """The implementation of the setter for :attr:`position`.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _scroll(self, dx, dy):
        """The implementation of the :meth:`scroll` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _press(self, button):
        """The implementation of the :meth:`press` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _release(self, button):
        """The implementation of the :meth:`release` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()


class Listener(threading.Thread):
    """A listener for mouse events.

    Instances of this class can be used as context managers. This is equivalent
    to the following code::

        listener.start()
        try:
            with_statements()
        finally:
            listener.stop()

    :param callable on_move: The callback to call when mouse move events occur.

        It will be called with the arguments ``(x, y)``, which is the new
        pointer position. If this callback raises :class:`StopException` or
        returns ``False``, the listener is stopped.

    :param callable on_click: The callback to call when a mouse button is
        clicked.

        It will be called with the arguments ``(x, y, button, pressed)``,
        where ``(x, y)`` is the new pointer position, ``button`` is one of the
        :class:`Controller.Button` values and ``pressed`` is whether the button
        was pressed.

        If this callback raises :class:`StopException` or returns ``False``,
        the listener is stopped.

    :param callable on_scroll: The callback to call when mouse scroll
        events occur.

        It will be called with the arguments ``(x, y, dx, dy)``, where
        ``(x, y)`` is the new pointer position, and ``(dx, dy)`` is the scroll
        vector.

        If this callback raises :class:`StopException` or returns ``False``,
        the listener is stopped.
    """
    class StopException(Exception):
        """If an event listener callback raises this exception, the current
        listener is stopped.

        Its first argument must be set to the :class:`Listener` to stop.
        """
        pass

    def __init__(self, on_move=None, on_click=None, on_scroll=None):
        super(Listener, self).__init__()

        def wrapper(f):
            def inner(*args):
                if f(*args) is False:
                    raise self.StopException(self)
            return inner

        self._running = False
        self._thread = threading.current_thread()
        self.on_move = wrapper(on_move or (lambda *a: None))
        self.on_click = wrapper(on_click or (lambda *a: None))
        self.on_scroll = wrapper(on_scroll or (lambda *a: None))

    @property
    def running(self):
        """Whether the listener is currently running.
        """
        return self._running

    def stop(self):
        """Stops listening for mouse events.

        When this method returns, the listening thread will have stopped.
        """
        if self._running:
            self._running = False
            self._stop()
            if threading.current_thread() != self._thread:
                self.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def run(self):
        """The thread runner method.
        """
        self._running = True
        self._thread = threading.current_thread()
        self._run()

    @classmethod
    def _emitter(self, f):
        """A decorator to mark a method as the one emitting the callbacks.

        This decorator will wrap the method and catch :class:`StopException`.
        If this exception is caught, the listener will be stopped.
        """
        @functools.wraps(f)
        def inner(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except self.StopException as e:
                e.args[0].stop()

        return inner

    def _run(self):
        """The implementation of the :meth:`start` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _stop(self):
        """The implementation of the :meth:`stop` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()
