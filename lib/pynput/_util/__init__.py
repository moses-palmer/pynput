# coding=utf-8
# pynput
# Copyright (C) 2015-2019 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
General utility functions and classes.
"""

# pylint: disable=R0903
# We implement minimal mixins

# pylint: disable=W0212
# We implement an internal API

import contextlib
import functools
import sys
import threading

import six

from six.moves import queue


class AbstractListener(threading.Thread):
    """A class implementing the basic behaviour for event listeners.

    Instances of this class can be used as context managers. This is equivalent
    to the following code::

        listener.start()
        listener.wait()
        try:
            with_statements()
        finally:
            listener.stop()

    Actual implementations of this class must set the attribute ``_log``, which
    must be an instance of :class:`logging.Logger`.

    :param bool suppress: Whether to suppress events. Setting this to ``True``
        will prevent the input events from being passed to the rest of the
        system.

    :param kwargs: A mapping from callback attribute to callback handler. All
        handlers will be wrapped in a function reading the return value of the
        callback, and if it ``is False``, raising :class:`StopException`.

        Any callback that is falsy will be ignored.
    """
    class StopException(Exception):
        """If an event listener callback raises this exception, the current
        listener is stopped.
        """
        pass

    #: Exceptions that are handled outside of the emitter and should thus not be
    #: passed through the queue
    _HANDLED_EXCEPTIONS = tuple()

    def __init__(self, suppress=False, **kwargs):
        super(AbstractListener, self).__init__()

        def wrapper(f):
            def inner(*args):
                if f(*args) is False:
                    raise self.StopException()
            return inner

        self._suppress = suppress
        self._running = False
        self._thread = threading.current_thread()
        self._condition = threading.Condition()
        self._ready = False

        # Allow multiple calls to stop
        self._queue = queue.Queue(10)

        self.daemon = True

        for name, callback in kwargs.items():
            setattr(self, name, wrapper(callback or (lambda *a: None)))

    @property
    def suppress(self):
        """Whether to suppress events.
        """
        return self._suppress

    @property
    def running(self):
        """Whether the listener is currently running.
        """
        return self._running

    def stop(self):
        """Stops listening for events.

        When this method returns, no more events will be delivered. Once this
        method has been called, the listener instance cannot be used any more,
        since a listener is a :class:`threading.Thread`, and once stopped it
        cannot be restarted.

        To resume listening for event, a new listener must be created.
        """
        if self._running:
            self._running = False
            self._queue.put(None)
            self._stop_platform()

    def __enter__(self):
        self.start()
        self.wait()
        return self

    def __exit__(self, exc_type, value, traceback):
        self.stop()

    def wait(self):
        """Waits for this listener to become ready.
        """
        self._condition.acquire()
        while not self._ready:
            self._condition.wait()
        self._condition.release()

    def run(self):
        """The thread runner method.
        """
        self._running = True
        self._thread = threading.current_thread()
        self._run()

        # Make sure that the queue contains something
        self._queue.put(None)

    @classmethod
    def _emitter(cls, f):
        """A decorator to mark a method as the one emitting the callbacks.

        This decorator will wrap the method and catch exception. If a
        :class:`StopException` is caught, the listener will be stopped
        gracefully. If any other exception is caught, it will be propagated to
        the thread calling :meth:`join` and reraised there.
        """
        @functools.wraps(f)
        def inner(self, *args, **kwargs):
            # pylint: disable=W0702; we want to catch all exception
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                if not isinstance(e, self._HANDLED_EXCEPTIONS):
                    if not isinstance(e, AbstractListener.StopException):
                        self._log.exception(
                            'Unhandled exception in listener callback')
                    self._queue.put(
                        None if isinstance(e, cls.StopException)
                        else sys.exc_info())
                    self.stop()
                raise
            # pylint: enable=W0702

        return inner

    def _mark_ready(self):
        """Marks this listener as ready to receive events.

        This method must be called from :meth:`_run`. :meth:`wait` will block
        until this method is called.
        """
        self._condition.acquire()
        self._ready = True
        self._condition.notify()
        self._condition.release()

    def _run(self):
        """The implementation of the :meth:`run` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _stop_platform(self):
        """The implementation of the :meth:`stop` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def join(self, *args):
        super(AbstractListener, self).join(*args)

        # Reraise any exceptions
        try:
            exc_type, exc_value, exc_traceback = self._queue.get()
        except TypeError:
            return
        six.reraise(exc_type, exc_value, exc_traceback)


class Events(object):
    """A base class to enable iterating over events.
    """
    #: The listener class providing events.
    _Listener = None

    class Event(object):
        def __str__(self):
            return '{}({})'.format(
                self.__class__.__name__,
                ', '.join(
                    '{}={}'.format(k, v)
                    for (k, v) in vars(self)))

        def __eq__(self, other):
            return self.__class__ == other.__class__ \
                and dir(self) == dir(other) \
                and all(
                    getattr(self, k) == getattr(other, k)
                    for k in dir(self))

    def __init__(self, *args, **kwargs):
        super(Events, self).__init__()
        self._event_queue = queue.Queue()
        self._sentinel = object()
        self._listener = self._Listener(*args, **{
            key: self._event_mapper(value)
            for (key, value) in kwargs.items()})
        self.start = self._listener.start

    def __enter__(self):
        self._listener.__enter__()
        return self

    def __exit__(self, *args):
        self._listener.__exit__(*args)

        # Drain the queue to ensure that the put does not block
        while True:
            try:
                self._event_queue.get_nowait()
            except queue.Empty:
                break

        self._event_queue.put(self._sentinel)

    def __iter__(self):
        return self

    def __next__(self):
        event = self.get()
        if event is not None:
            return event
        else:
            raise StopIteration()

    def get(self, timeout=None):
        """Attempts to read the next event.

        :param int timeout: An optional timeout. If this is not provided, this
            method may block infinitely.

        :return: The next event, or ``None`` if the source has been stopped
        """
        event = self._event_queue.get(timeout=timeout)
        return event if event is not self._sentinel else None

    def _event_mapper(self, event):
        """Generates an event callback to transforms the callback arguments to
        an event and then publishes it.

        :param callback event: A function generating an event object.

        :return: a callback
        """
        @functools.wraps(event)
        def inner(*args):
            try:
                self._event_queue.put(event(*args), block=False)
            except queue.Full:
                pass

        return inner


class NotifierMixin(object):
    """A mixin for notifiers of fake events.

    This mixin can be used for controllers on platforms where sending fake
    events does not cause a listener to receive a notification.
    """
    def _emit(self, action, *args):
        """Sends a notification to all registered listeners.

        This method will ensure that listeners that raise
        :class:`StopException` are stopped.

        :param str action: The name of the notification.

        :param args: The arguments to pass.
        """
        stopped = []
        for listener in self._listeners():
            try:
                getattr(listener, action)(*args)
            except listener.StopException:
                stopped.append(listener)
        for listener in stopped:
            listener.stop()

    @classmethod
    def _receiver(cls, listener_class):
        """A decorator to make a class able to receive fake events from a
        controller.

        This decorator will add the method ``_receive`` to the decorated class.

        This method is a context manager which ensures that all calls to
        :meth:`_emit` will invoke the named method in the listener instance
        while the block is active.
        """
        @contextlib.contextmanager
        def receive(self):
            """Executes a code block with this listener instance registered as
            a receiver of fake input events.
            """
            self._controller_class._add_listener(self)
            try:
                yield
            finally:
                self._controller_class._remove_listener(self)

        listener_class._receive = receive
        listener_class._controller_class = cls

        # Make sure this class has the necessary attributes
        if not hasattr(cls, '_listener_cache'):
            cls._listener_cache = set()
            cls._listener_lock = threading.Lock()

        return listener_class

    @classmethod
    def _listeners(cls):
        """Iterates over the set of running listeners.

        This method will quit without acquiring the lock if the set is empty,
        so there is potential for race conditions. This is an optimisation,
        since :class:`Controller` will need to call this method for every
        control event.
        """
        if not cls._listener_cache:
            return
        with cls._listener_lock:
            for listener in cls._listener_cache:
                yield listener

    @classmethod
    def _add_listener(cls, listener):
        """Adds a listener to the set of running listeners.

        :param listener: The listener for fake events.
        """
        with cls._listener_lock:
            cls._listener_cache.add(listener)

    @classmethod
    def _remove_listener(cls, listener):
        """Removes this listener from the set of running listeners.

        :param listener: The listener for fake events.
        """
        with cls._listener_lock:
            cls._listener_cache.remove(listener)
