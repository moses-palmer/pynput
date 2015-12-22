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

    def test_pressed_shift(self):
        """Asserts that pressing a releasing a Latin character causes it to
        shift to upper case"""
        with self.capture() as collect:
            with self.controller.pressed(pynput.keyboard.Key.shift):
                self.controller.press('a')
                self.controller.release('a')

                self.assertIn(
                    pynput.keyboard.Key.shift,
                    self.controller.keys_down)

        self.assertIn(
            'A',
            collect(),
            'shift+a did not yield "A"')

    def test_pressed_multiple(self):
        """Asserts that multiple calls to pressed accumulates keys"""
        with self.capture() as collect:
            with self.controller.pressed(pynput.keyboard.Key.shift):
                keys_down_outer = self.controller.keys_down
                with self.controller.pressed('a'):
                    keys_down_inner = self.controller.keys_down

        self.assertIn(
            pynput.keyboard.Key.shift,
            keys_down_outer,
            'Outer call to pressed did not update keys_down')
        self.assertIn(
            pynput.keyboard.Key.shift,
            keys_down_inner,
            'Inner call to pressed incorrectly updated keys_down')
        self.assertGreater(
            len(keys_down_inner),
            len(keys_down_outer),
            'Inner call to pressed did not add keys to keys_down')

        self.assertIn(
            'A',
            collect(),
            'shift+a did not yield "A"')

    def test_shift_active_inactive(self):
        """Asserts that shift_active is False when shift has not been
        pressed"""
        self.assertFalse(
            self.controller.shift_active,
            'shift_active was incorrectly set')

    def test_shift_active_pressed(self):
        """Asserts that shift_active is True when shift is pressed"""
        for key in (
                pynput.keyboard.Key.shift,
                pynput.keyboard.Key.shift_l,
                pynput.keyboard.Key.shift_r):
            with self.controller.pressed(key):
                self.assertTrue(
                    self.controller.shift_active,
                    'shift_active was not set with %s down' % key.name)
            self.assertFalse(
                self.controller.shift_active,
                'shift_active was incorrectly set')

    def test_shift_active_caps_lock(self):
        """Asserts that shift_active is True when caps lock is toggled"""
        self.controller.press(pynput.keyboard.Key.caps_lock)
        self.controller.release(pynput.keyboard.Key.caps_lock)
        self.assertTrue(
            self.controller.shift_active,
            'shift_active was not set with caps lock toggled')

        self.controller.press(pynput.keyboard.Key.caps_lock)
        self.controller.release(pynput.keyboard.Key.caps_lock)
        self.assertFalse(
            self.controller.shift_active,
            'shift_active was not deactivated with caps lock toggled')

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
