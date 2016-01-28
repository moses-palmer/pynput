import contextlib
import time
import unittest


class EventTest(unittest.TestCase):
    #: The message displayed when this test suite is started
    NOTIFICATION = None

    #: The controller class; if this is defined, :attr:`controller` will be
    # instantiated for every test
    CONTROLLER_CLASS = None

    #: The listener class; this must be defined for subclasses
    LISTENER_CLASS = None

    #: Tha maximum number of seconds to wait before failing in
    #: :meth:`assert_stop`
    STOP_MAX_WAIT = 3.0

    #: The minimum number of events to accumulate before checking for changes
    #: in :meth:`assertChange`
    CHANGE_MIN_EVENTS = 50

    @classmethod
    def setUpClass(self):
        self.notify(self.NOTIFICATION)
        self.listeners = []

    @classmethod
    def tearDownClass(self):
        remaining = [
            listener
            for listener in self.listeners
            if not (listener.join(0.5) or listener.is_alive)]
        for listener in remaining:
            listener.join()

    def setUp(self):
        if self.CONTROLLER_CLASS is not None:
            self.controller = self.CONTROLLER_CLASS()

    @classmethod
    def notify(self, message, delay=None, columns=40):
        """Prints a notification on screen.

        :param str message: The message to display.

        :param delay: An optional delay, in seconds, before returning from this
            function
        :type delay: float or None

        :param int columns: The number of columns for the notification.
        """
        # The maximum length of a message line; we need four columns for the
        # frame
        max_length = columns - 4

        # Split the message into lines containing at most max_length characters
        lines = []
        for word in message.split():
            if not lines or len(lines[-1]) + 1 + len(word) > max_length:
                lines.append(word)
            else:
                lines[-1] += ' ' + word

        # Print the message
        print('')
        print('+' + '=' * (columns - 2) + '+')
        for line in lines:
            print(('| {:<%ds} |' % max_length).format(line))
        print('+' + '-' * (columns - 2) + '+')

        if delay:
            time.sleep(delay)

    def listener(self, *args, **kwargs):
        """Creates a listener.

        All arguments are passed to the constructor.
        """
        listener = self.LISTENER_CLASS(*args, **kwargs)
        self.listeners.append(listener)
        return listener

    @contextlib.contextmanager
    def assert_event(self, failure_message, **kwargs):
        """Asserts that a specific event is emitted when a code block is
        executed.

        :param str failure_message: The message to display upon failure.

        :param args: Arguments to pass to the listener constructor.

        :param kwargs: Arguments to pass to the listener constructor.
        """
        def wrapper(name, callback):
            def inner(*a):
                if callback(*a):
                    listener.success = True
                    return False

            return inner if callback else None

        with self.listener(**{
                name: wrapper(name, callback)
                for name, callback in kwargs.items()}) as listener:
            time.sleep(0.1)
            listener.success = False
            yield

            for _ in range(30):
                time.sleep(0.1)
                if listener.success:
                    break

        self.assertTrue(
            listener.success,
            failure_message)

    def assert_stop(self, failure_message, **callbacks):
        """Asserts that a listener stop within :attr:`STOP_MAX_WAIT` seconds.

        :param str failure_message: The message to display upon failure.

        :param args: Arguments to pass to the listener constructor.

        :param callbacks: The callbacks for checking whether change has
            occurred.
        """
        success = False
        listener = self.listener(**callbacks)
        with listener:
            for _ in range(10):
                time.sleep(self.STOP_MAX_WAIT * 0.1)
                if not listener.running:
                    success = True
                    break

        self.assertTrue(
            success,
            failure_message)

    def assert_cumulative(self, failure_message, **callbacks):
        """Asserts that the callback returns true for at least two thirds of
        the elements.

        At least :attr:`CHANGE_MIN_EVENTS` will be examined.

        :param str failure_message: The message to display upon failure.

        :param callbacks: The callbacks for checking whether change has
            occurred.
        """
        # The lists of accumulated events
        events = {
            name: []
            for name in callbacks}

        def wrapper(name, callback):
            def inner(*a):
                cache = events[name]
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

        self.assert_stop(failure_message, **{
            name: wrapper(name, callback)
            for name, callback in callbacks.items()})
