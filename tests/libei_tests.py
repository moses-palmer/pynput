# coding=utf-8
# pynput
# Copyright (C) 2015-2024 Moses Palmér
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

import os
import unittest

import pynput.keyboard
import pynput.mouse

from . import libei


class LibeiTableTest(unittest.TestCase):
    """Tests the tables of constants, which need no compositor.

    These are the parts of the backend that can be wrong silently: a keycode
    off by one sends a different key rather than failing, and the scroll unit
    was measured rather than read, so both are checked against their sources.
    """

    @libei
    def test_buttons(self):
        """Asserts that every button of the base interface is defined"""
        from pynput.mouse._base import Button
        for button in Button:
            self.assertTrue(
                hasattr(pynput.mouse.Button, button.name),
                '%s is not defined for the libei backend' % button.name)

    @libei
    def test_keys(self):
        """Asserts that every key of the base interface is defined"""
        from pynput.keyboard._base import Key
        for key in Key:
            self.assertTrue(
                hasattr(pynput.keyboard.Key, key.name),
                '%s is not defined for the libei backend' % key.name)

    @libei
    def test_keycodes_match_kernel(self):
        """Asserts that the hard coded keycodes are the kernel's"""
        import evdev.ecodes

        from pynput.keyboard._libei import KERNEL_KEYS
        for name, value in KERNEL_KEYS.items():
            self.assertEqual(
                getattr(evdev.ecodes, name),
                value,
                '%s is %d, not %d' % (
                    name, getattr(evdev.ecodes, name), value))

    @libei
    def test_buttons_match_kernel(self):
        """Asserts that the hard coded button codes are the kernel's"""
        import evdev.ecodes

        for name, code in (
                ('left', 'BTN_LEFT'),
                ('right', 'BTN_RIGHT'),
                ('middle', 'BTN_MIDDLE'),
                ('side', 'BTN_SIDE'),
                ('extra', 'BTN_EXTRA'),
                ('forward', 'BTN_FORWARD'),
                ('back', 'BTN_BACK'),
                ('task', 'BTN_TASK')):
            self.assertEqual(
                getattr(evdev.ecodes, code),
                getattr(pynput.mouse.Button, name).value,
                'Button.%s is not %s' % (name, code))

    @libei
    def test_scroll_detent(self):
        """Asserts that one scroll detent is 120 units

        libei counts discrete scrolling in 120ths of a detent; sending 1
        scrolls by a 120th of a click, which is almost imperceptible rather
        than obviously wrong.
        """
        from pynput._util.libei import SCROLL_DETENT
        self.assertEqual(120, SCROLL_DETENT)

    @libei
    def test_xkb_keycode_offset(self):
        """Asserts that the XKB keycode offset is 8"""
        from pynput._util.libei import XKB_KEYCODE_OFFSET
        self.assertEqual(8, XKB_KEYCODE_OFFSET)


class LibeiEnvironmentTest(unittest.TestCase):
    """Tests the parts of the backend driven by the environment."""

    def setUp(self):
        self._environ = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._environ)

    @libei
    def test_is_wayland(self):
        """Tests that a Wayland session is detected"""
        from pynput._util.libei import is_wayland

        os.environ.pop('WAYLAND_DISPLAY', None)
        os.environ.pop('XDG_SESSION_TYPE', None)
        self.assertFalse(is_wayland())

        os.environ['WAYLAND_DISPLAY'] = 'wayland-0'
        self.assertTrue(is_wayland())

        del os.environ['WAYLAND_DISPLAY']
        os.environ['XDG_SESSION_TYPE'] = 'Wayland'
        self.assertTrue(is_wayland())

        os.environ['XDG_SESSION_TYPE'] = 'x11'
        self.assertFalse(is_wayland())

    @libei
    def test_token_path_default(self):
        """Tests that the restore token is stored under XDG_DATA_HOME"""
        from pynput._util.libei import token_path

        os.environ.pop('PYNPUT_LIBEI_RESTORE_TOKEN', None)
        os.environ['XDG_DATA_HOME'] = '/tmp/pynput-test'
        self.assertEqual(
            os.path.join('/tmp/pynput-test', 'pynput', 'libei-restore-token'),
            token_path())

    @libei
    def test_token_path_override(self):
        """Tests that the restore token path can be overridden"""
        from pynput._util.libei import token_path

        os.environ['PYNPUT_LIBEI_RESTORE_TOKEN'] = '/tmp/pynput-test/token'
        self.assertEqual('/tmp/pynput-test/token', token_path())

    @libei
    def test_token_path_disabled(self):
        """Tests that storing the restore token can be switched off"""
        from pynput._util.libei import token_path

        os.environ['PYNPUT_LIBEI_RESTORE_TOKEN'] = ''
        self.assertIsNone(token_path())


class LibeiListenerTest(unittest.TestCase):
    """Tests that the absent listener says so.

    The listener is inert because monitoring input needs the InputCapture
    portal, which this backend does not implement. Silently receiving nothing
    would be worse than an error, so this makes sure the error happens.
    """

    @libei
    def test_mouse_listener_raises(self):
        """Tests that starting a mouse listener fails loudly"""
        listener = pynput.mouse.Listener(on_move=lambda x, y: None)
        self.assertRaises(NotImplementedError, listener.run)

    @libei
    def test_keyboard_listener_raises(self):
        """Tests that starting a keyboard listener fails loudly"""
        listener = pynput.keyboard.Listener(on_press=lambda key: None)
        self.assertRaises(NotImplementedError, listener.run)


class LibeiSessionTest(unittest.TestCase):
    """Tests that need a granted session, and so a compositor.

    The first of these raises the portal dialog unless a grant has already
    been stored.
    """

    @libei
    def test_bounds(self):
        """Tests that the compositor reports an area to move within"""
        from pynput._util.libei import session

        bounds = session().bounds
        self.assertIsNotNone(bounds)
        _, _, width, height = bounds
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)

    @libei
    def test_position_round_trip(self):
        """Tests that a position that was set can be read back"""
        from pynput._util.libei import session

        controller = pynput.mouse.Controller()
        left, top, width, height = session().bounds
        position = (left + width // 2, top + height // 2)
        controller.position = position
        self.assertEqual(position, controller.position)

    @libei
    def test_position_unknown(self):
        """Tests that an unset position is refused rather than guessed"""
        controller = pynput.mouse.Controller()
        with self.assertRaises(NotImplementedError):
            # pylint: disable=W0104; we want the property to be evaluated
            controller.position
            # pylint: enable=W0104

    @libei
    def test_position_out_of_bounds(self):
        """Tests that a position outside every screen is refused"""
        from pynput._util.libei import session

        controller = pynput.mouse.Controller()
        left, top, width, height = session().bounds
        with self.assertRaises(ValueError):
            controller.position = (left + width, top + height)

    @libei
    def test_move_relative(self):
        """Tests that a relative move does not need a known position"""
        from pynput._util.libei import session

        controller = pynput.mouse.Controller()
        left, top, width, height = session().bounds
        controller.position = (left + width // 2, top + height // 2)
        before = controller.position
        controller.move(10, 10)
        self.assertEqual(
            (before[0] + 10, before[1] + 10),
            controller.position)

    @libei
    def test_named_keys_need_no_layout(self):
        """Tests that a key with a known position resolves without a layout"""
        controller = pynput.keyboard.Controller()
        for key in (
                pynput.keyboard.Key.enter,
                pynput.keyboard.Key.esc,
                pynput.keyboard.Key.f5,
                pynput.keyboard.Key.ctrl):
            # pylint: disable=W0212; we are testing an internal API
            keycode, shifted = controller._resolve_keycode(key.value)
            # pylint: enable=W0212
            self.assertEqual(key.value.vk, keycode)
            self.assertFalse(shifted)

    @libei
    def test_characters_need_the_layout(self):
        """Tests that characters resolve through the compositor's layout"""
        from pynput._util.libei import session

        if session().keymap is None:
            self.skipTest('the xkbcommon package is not installed')

        controller = pynput.keyboard.Controller()
        # pylint: disable=W0212; we are testing an internal API
        lower, lower_shifted = controller._resolve_keycode(
            pynput.keyboard.KeyCode.from_char('a'))
        upper, upper_shifted = controller._resolve_keycode(
            pynput.keyboard.KeyCode.from_char('A'))
        # pylint: enable=W0212

        # The same physical key, reached at a different shift level
        self.assertEqual(lower, upper)
        self.assertFalse(lower_shifted)
        self.assertTrue(upper_shifted)

    @libei
    def test_untypable_character(self):
        """Tests that a character no key produces is reported as invalid"""
        from pynput._util.libei import session

        if session().keymap is None:
            self.skipTest('the xkbcommon package is not installed')

        controller = pynput.keyboard.Controller()
        with self.assertRaises(controller.InvalidKeyException):
            # pylint: disable=W0212; we are testing an internal API
            controller._resolve_keycode(
                pynput.keyboard.KeyCode.from_char('\N{SNOWMAN}'))
            # pylint: enable=W0212
