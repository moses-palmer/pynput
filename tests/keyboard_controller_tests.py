# coding: utf-8
import unittest

import contextlib
import locale
import sys
import threading

import pynput.keyboard

from . import notify


class KeyboardControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        notify(
            'This test case is non-interactive, so you must not use the '
            'keyboard',
            delay=2)

    def setUp(self):
        self.controller = pynput.keyboard.Controller()

    def decode(self, string):
        """Decodes a string read from ``stdin``.

        :param str string: The string to decode.
        """
        if sys.version_info.major >= 3:
            yield string
        else:
            for encoding in (
                    'utf-8',
                    locale.getpreferredencoding(),
                    sys.stdin.encoding):
                if encoding:
                    try:
                        yield string.decode(encoding)
                    except:
                        pass

    @contextlib.contextmanager
    def capture(self):
        """Captures a string in a code block.

        :returns: a callable which returns the actual data read
        """
        data = []

        #: The thread body that reads a line from stdin and appends it to data
        def reader():
            while reader.running:
                data.append(sys.stdin.readline()[:-1])
        reader.running = True

        # Start the thread
        thread = threading.Thread(target=reader)
        thread.start()

        # Run the code block
        try:
            yield lambda: tuple(self.decode(''.join(data)))

        finally:
            # Send a newline to let sys.stdin.readline return in reader
            reader.running = False
            self.controller.press(pynput.keyboard.Key.enter)
            self.controller.release(pynput.keyboard.Key.enter)
            thread.join()

    def assertInput(self, failure_message, expected):
        """Asserts that a specific text is generated when typing.

        :param str failure_message: The message to display upon failure.

        :param text: The text to type and expect.
        """
        with self.capture() as collect:
            self.controller.type(expected)

        self.assertIn(expected, collect(), failure_message)

    def test_keys(self):
        """Asserts that all keys defined for the base keyboard interface are
        defined for the current platform"""
        from pynput.keyboard._base import Key
        for key in Key:
            self.assertTrue(
                hasattr(pynput.keyboard.Key, key.name),
                '%s is not defined for the current platform' % key.name)

    def test_press_release(self):
        """Asserts that a press followed by a release generates a typed string
        for an ascii character"""
        with self.capture() as collect:
            self.controller.press(pynput.keyboard.Key.space)
            self.controller.release(pynput.keyboard.Key.space)

        self.assertIn(
            ' ',
            collect(),
            'Failed to press and release space')

    def test_touch(self):
        """Asserts that the touch shortcut behaves as expected"""
        with self.capture() as collect:
            self.controller.touch(pynput.keyboard.Key.space, True)
            self.controller.touch(pynput.keyboard.Key.space, False)

        self.assertIn(
            ' ',
            collect(),
            'Failed to press and release space')

    def test_touch_dead(self):
        """Asserts that pressing dead keys generate combined characters"""
        with self.capture() as collect:
            dead = pynput.keyboard.KeyCode.from_dead('~')
            self.controller.press(dead)
            self.controller.release(dead)
            self.controller.press('a')
            self.controller.release('a')

        self.assertIn(
            u'ã',
            collect(),
            'Failed to apply dead key')

    def test_touch_dead_space(self):
        """Asserts that pressing dead keys followed by space yields the
        non-dead version"""
        with self.capture() as collect:
            dead = pynput.keyboard.KeyCode.from_dead('~')
            self.controller.press(dead)
            self.controller.release(dead)
            self.controller.press(pynput.keyboard.Key.space)
            self.controller.release(pynput.keyboard.Key.space)

        self.assertIn(
            u'~',
            collect(),
            'Failed to apply dead key')

    def test_touch_dead_twice(self):
        """Asserts that pressing dead keys twice yields the non-dead version"""
        with self.capture() as collect:
            dead = pynput.keyboard.KeyCode.from_dead('~')
            self.controller.press(dead)
            self.controller.release(dead)
            self.controller.press(dead)
            self.controller.release(dead)

        self.assertIn(
            u'~',
            collect(),
            'Failed to apply dead key')

    def test_type_latin(self):
        """Asserts that type works for a Latin string"""
        self.assertInput(
            'Failed to type latin string',
            u'Hello World')

    def test_type_ascii(self):
        """Asserts that type works for an ascii string"""
        self.assertInput(
            'Failed to type ascii string',
            u'abc123, "quoted!"')

    def test_type_nonascii(self):
        """Asserts that type works for a non-ascii strings"""
        self.assertInput(
            'Failed to type Spanish string',
            u'Teclado (informática)')
        self.assertInput(
            'Failed to type Russian string',
            u'Компьютерная клавиатура')
