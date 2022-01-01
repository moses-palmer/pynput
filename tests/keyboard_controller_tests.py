# coding=utf-8
# pystray
# Copyright (C) 2015-2022 Moses Palmér
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

import contextlib
import locale
import sys
import threading

import pynput.keyboard

from six.moves import input

from . import EventTest


class KeyboardControllerTest(EventTest):
    NOTIFICATION = (
        'This test case is non-interactive, so you must not use the '
        'keyboard.\n'
        'You must, however, keep this window focused.')
    CONTROLLER_CLASS = pynput.keyboard.Controller
    LISTENER_CLASS = pynput.keyboard.Listener

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
            self.controller.tap(pynput.keyboard.Key.enter)
            thread.join()

    def assert_input(self, failure_message, expected):
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

    def test_press_invalid(self):
        with self.assertRaises(self.controller.InvalidKeyException):
            self.controller.press(True)

    def test_release_invalid(self):
        with self.assertRaises(self.controller.InvalidKeyException):
            self.controller.release(True)

    def test_press_release(self):
        """Asserts that a press followed by a release generates a typed string
        for an ascii character"""
        with self.capture() as collect:
            self.controller.tap(pynput.keyboard.Key.space)

        self.assertIn(
            u' ',
            collect(),
            'Failed to press and release space')

    def test_touch(self):
        """Asserts that the touch shortcut behaves as expected"""
        with self.capture() as collect:
            self.controller.touch(pynput.keyboard.Key.space, True)
            self.controller.touch(pynput.keyboard.Key.space, False)

        self.assertIn(
            u' ',
            collect(),
            'Failed to press and release space')

    def test_touch_dead(self):
        """Asserts that pressing dead keys generate combined characters"""
        with self.capture() as collect:
            dead = pynput.keyboard.KeyCode.from_dead(u'~')
            self.controller.tap(dead)
            self.controller.tap(u'a')

        self.assertIn(
            u'ã',
            collect(),
            'Failed to apply dead key')

    def test_touch_dead_space(self):
        """Asserts that pressing dead keys followed by space yields the
        non-dead version"""
        with self.capture() as collect:
            dead = pynput.keyboard.KeyCode.from_dead(u'~')
            self.controller.tap(dead)
            self.controller.tap(pynput.keyboard.Key.space)

        self.assertIn(
            u'~',
            collect(),
            'Failed to apply dead key')

    def test_touch_dead_twice(self):
        """Asserts that pressing dead keys twice yields the non-dead version"""
        with self.capture() as collect:
            dead = pynput.keyboard.KeyCode.from_dead(u'~')
            self.controller.tap(dead)
            self.controller.tap(dead)

        self.assertIn(
            u'~',
            collect(),
            'Failed to apply dead key')

    def test_alt_pressed(self):
        """Asserts that alt_pressed works"""
        # We do not test alt_r, since that does not necessarily exist on the
        # keyboard
        for key in (
                pynput.keyboard.Key.alt,
                pynput.keyboard.Key.alt_l):
            self.controller.press(key)
            self.assertTrue(
                self.controller.alt_pressed,
                'alt_pressed was not set with %s down' % key.name)
            self.controller.release(key)
            self.assertFalse(
                self.controller.alt_pressed,
                'alt_pressed was incorrectly set')

    def test_ctrl_pressed(self):
        """Asserts that ctrl_pressed works"""
        for key in (
                pynput.keyboard.Key.ctrl,
                pynput.keyboard.Key.ctrl_l,
                pynput.keyboard.Key.ctrl_r):
            self.controller.press(key)
            self.assertTrue(
                self.controller.ctrl_pressed,
                'ctrl_pressed was not set with %s down' % key.name)
            self.controller.release(key)
            self.assertFalse(
                self.controller.ctrl_pressed,
                'ctrl_pressed was incorrectly set')

    def test_shift_pressed(self):
        """Asserts that shift_pressed works with normal presses"""
        for key in (
                pynput.keyboard.Key.shift,
                pynput.keyboard.Key.shift_l,
                pynput.keyboard.Key.shift_r):
            self.controller.press(key)
            self.assertTrue(
                self.controller.shift_pressed,
                'shift_pressed was not set with %s down' % key.name)
            self.controller.release(key)
            self.assertFalse(
                self.controller.shift_pressed,
                'shift_pressed was incorrectly set')

    def test_shift_pressed_caps_lock(self):
        """Asserts that shift_pressed is True when caps lock is toggled"""
        self.controller.tap(pynput.keyboard.Key.caps_lock)
        self.assertTrue(
            self.controller.shift_pressed,
            'shift_pressed was not set with caps lock toggled')

        self.controller.tap(pynput.keyboard.Key.caps_lock)
        self.assertFalse(
            self.controller.shift_pressed,
            'shift_pressed was not deactivated with caps lock toggled')

    def test_pressed_shift(self):
        """Asserts that pressing and releasing a Latin character while pressing
        shift causes it to shift to upper case"""
        with self.capture() as collect:
            with self.controller.pressed(pynput.keyboard.Key.shift):
                self.controller.tap(u'a')

                with self.controller.modifiers as modifiers:
                    self.assertIn(
                        pynput.keyboard.Key.shift,
                        modifiers)

        self.assertIn(
            u'A',
            collect(),
            'shift+a did not yield "A"')

    def test_pressed_is_release(self):
        """Asserts that pressed actually releases the key"""
        with self.capture() as collect:
            with self.controller.pressed(pynput.keyboard.Key.shift):
                self.controller.tap(u'a')

            self.controller.tap(u'a')

            with self.controller.pressed(pynput.keyboard.Key.shift):
                self.controller.tap(u'a')


        self.assertIn(
            u'AaA',
            collect(),
            'Keys were not properly released')

    def test_type_latin(self):
        """Asserts that type works for a Latin string"""
        self.assert_input(
            'Failed to type latin string',
            u'Hello World')

    def test_type_ascii(self):
        """Asserts that type works for an ascii string"""
        self.assert_input(
            'Failed to type ascii string',
            u'abc123, "quoted!"')

    def test_type_nonascii(self):
        """Asserts that type works for a non-ascii strings"""
        self.assert_input(
            'Failed to type Spanish string',
            u'Teclado (informática)')
        self.assert_input(
            'Failed to type Russian string',
            u'Компьютерная клавиатура')

    def test_type_control_codes(self):
        """Asserts that type works for a string containing control codes"""
        self.assert_input(
            'Failed to type latin string',
            u'Hello\tworld')

    def test_controller_events(self):
        """Tests that events sent by a controller are received correctly"""
        with self.assert_event(
                'Failed to send press',
                on_press=lambda k: getattr(k, 'char', None) == u'a'):
            self.controller.press(u'a')
        with self.assert_event(
                'Failed to send release',
                on_release=lambda k: getattr(k, 'char', None) == u'a'):
            self.controller.release(u'a')

        self.controller.tap(pynput.keyboard.Key.enter)
        input()
