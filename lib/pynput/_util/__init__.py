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

import functools
import threading


class AbstractListener(threading.Thread):
    """A class implementing the basic behaviour for event listeners.

    Instances of this class can be used as context managers. This is equivalent
    to the following code::

        listener.start()
        try:
            with_statements()
        finally:
            listener.stop()

    :param kwargs: A mapping from callback attribute to callback handler. All
        handlers will be wrapped in a function reading the return value of the
        callback, and if it ``is False``, raising :class:`StopException`.

        Any callback that is falsy will be ignored.
    """
    class StopException(Exception):
        """If an event listener callback raises this exception, the current
        listener is stopped.

        Its first argument must be set to the :class:`Listener` to stop.
        """
        pass

    def __init__(self, **kwargs):
        super(AbstractListener, self).__init__()

        def wrapper(f):
            def inner(*args):
                if f(*args) is False:
                    raise self.StopException(self)
            return inner

        self._running = False
        self._thread = threading.current_thread()

        for name, callback in kwargs.items():
            setattr(self, name, wrapper(callback or (lambda *a: None)))

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
