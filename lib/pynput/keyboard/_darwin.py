# coding=utf-8
# pynput
# Copyright (C) 2015-2018 Moses Palmér
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
The keyboard implementation for *OSX*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import enum

import Quartz

from pynput._util.darwin import (
    get_unicode_to_keycode_map,
    keycode_context,
    ListenerMixin)
from . import _base


class KeyCode(_base.KeyCode):
    def _event(self, modifiers, mapping, is_pressed):
        """This key as a *Quartz* event.

        :param set modifiers: The currently active modifiers.

        :param mapping: The current keyboard mapping.

        :param bool is_press: Whether to generate a press event.

        :return: a *Quartz* event
        """
        vk = self.vk or mapping.get(self.char, 0)
        result = Quartz.CGEventCreateKeyboardEvent(None, vk, is_pressed)

        Quartz.CGEventSetFlags(
            result,
            0
            | (Quartz.kCGEventFlagMaskAlternate
               if Key.alt in modifiers else 0)

            | (Quartz.kCGEventFlagMaskCommand
               if Key.cmd in modifiers else 0)

            | (Quartz.kCGEventFlagMaskControl
               if Key.ctrl in modifiers else 0)

            | (Quartz.kCGEventFlagMaskShift
               if Key.shift in modifiers else 0))

        if vk is None and self.char is not None:
            Quartz.CGEventKeyboardSetUnicodeString(
                result, len(self.char), self.char)

        return result


class Key(enum.Enum):
    # Default keys
    alt = KeyCode.from_vk(0x3A)
    alt_l = KeyCode.from_vk(0x3A)
    alt_r = KeyCode.from_vk(0x3D)
    alt_gr = KeyCode.from_vk(0x3D)
    backspace = KeyCode.from_vk(0x33)
    caps_lock = KeyCode.from_vk(0x39)
    cmd = KeyCode.from_vk(0x37)
    cmd_l = KeyCode.from_vk(0x37)
    cmd_r = KeyCode.from_vk(0x36)
    ctrl = KeyCode.from_vk(0x3B)
    ctrl_l = KeyCode.from_vk(0x3B)
    ctrl_r = KeyCode.from_vk(0x3E)
    delete = KeyCode.from_vk(0x75)
    down = KeyCode.from_vk(0x7D)
    end = KeyCode.from_vk(0x77)
    enter = KeyCode.from_vk(0x24)
    esc = KeyCode.from_vk(0x35)
    f1 = KeyCode.from_vk(0x7A)
    f2 = KeyCode.from_vk(0x78)
    f3 = KeyCode.from_vk(0x63)
    f4 = KeyCode.from_vk(0x76)
    f5 = KeyCode.from_vk(0x60)
    f6 = KeyCode.from_vk(0x61)
    f7 = KeyCode.from_vk(0x62)
    f8 = KeyCode.from_vk(0x64)
    f9 = KeyCode.from_vk(0x65)
    f10 = KeyCode.from_vk(0x6D)
    f11 = KeyCode.from_vk(0x67)
    f12 = KeyCode.from_vk(0x6F)
    f13 = KeyCode.from_vk(0x69)
    f14 = KeyCode.from_vk(0x6B)
    f15 = KeyCode.from_vk(0x71)
    f16 = KeyCode.from_vk(0x6A)
    f17 = KeyCode.from_vk(0x40)
    f18 = KeyCode.from_vk(0x4F)
    f19 = KeyCode.from_vk(0x50)
    f20 = KeyCode.from_vk(0x5A)
    home = KeyCode.from_vk(0x73)
    left = KeyCode.from_vk(0x7B)
    page_down = KeyCode.from_vk(0x79)
    page_up = KeyCode.from_vk(0x74)
    right = KeyCode.from_vk(0x7C)
    shift = KeyCode.from_vk(0x38)
    shift_l = KeyCode.from_vk(0x38)
    shift_r = KeyCode.from_vk(0x3C)
    space = KeyCode.from_vk(0x31, char=' ')
    tab = KeyCode.from_vk(0x30)
    up = KeyCode.from_vk(0x7E)


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def __init__(self):
        super(Controller, self).__init__()
        self._mapping = get_unicode_to_keycode_map()

    def _handle(self, key, is_press):
        with self.modifiers as modifiers:
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                (key if key not in Key else key.value)._event(
                    modifiers, self._mapping, is_press))


class Listener(ListenerMixin, _base.Listener):
    #: The events that we listen to
    _EVENTS = (
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) |
        Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged))

    #: A mapping from keysym to special key
    _SPECIAL_KEYS = {
        key.value.vk: key
        for key in Key}

    #: The event flags set for the various modifier keys
    _MODIFIER_FLAGS = {
        Key.alt: Quartz.kCGEventFlagMaskAlternate,
        Key.alt_l: Quartz.kCGEventFlagMaskAlternate,
        Key.alt_r: Quartz.kCGEventFlagMaskAlternate,
        Key.cmd: Quartz.kCGEventFlagMaskCommand,
        Key.cmd_l: Quartz.kCGEventFlagMaskCommand,
        Key.cmd_r: Quartz.kCGEventFlagMaskCommand,
        Key.ctrl: Quartz.kCGEventFlagMaskControl,
        Key.ctrl_l: Quartz.kCGEventFlagMaskControl,
        Key.ctrl_r: Quartz.kCGEventFlagMaskControl,
        Key.shift: Quartz.kCGEventFlagMaskShift,
        Key.shift_l: Quartz.kCGEventFlagMaskShift,
        Key.shift_r: Quartz.kCGEventFlagMaskShift}

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._flags = 0
        self._context = None
        self._intercept = self._options.get(
            'intercept',
            None)

    def _run(self):
        with keycode_context() as context:
            self._context = context
            try:
                super(Listener, self)._run()
            finally:
                self._context = None

    def _handle(self, dummy_proxy, event_type, event, dummy_refcon):
        # Convert the event to a KeyCode; this may fail, and in that case we
        # pass None
        try:
            key = self._event_to_key(event)
        except IndexError:
            key = None

        try:
            if event_type == Quartz.kCGEventKeyDown:
                # This is a normal key press
                self.on_press(key)

            elif event_type == Quartz.kCGEventKeyUp:
                # This is a normal key release
                self.on_release(key)

            elif key == Key.caps_lock:
                # We only get an event when caps lock is toggled, so we fake
                # press and release
                self.on_press(key)
                self.on_release(key)

            else:
                # This is a modifier event---excluding caps lock---for which we
                # must check the current modifier state to determine whether
                # the key was pressed or released
                flags = Quartz.CGEventGetFlags(event)
                is_press = flags & self._MODIFIER_FLAGS.get(key, 0)
                if is_press:
                    self.on_press(key)
                else:
                    self.on_release(key)

        finally:
            # Store the current flag mask to be able to detect modifier state
            # changes
            self._flags = Quartz.CGEventGetFlags(event)

    def _event_to_key(self, event):
        """Converts a *Quartz* event to a :class:`KeyCode`.

        :param event: The event to convert.

        :return: a :class:`pynput.keyboard.KeyCode`

        :raises IndexError: if the key code is invalid
        """
        vk = Quartz.CGEventGetIntegerValueField(
            event, Quartz.kCGKeyboardEventKeycode)

        # First try special keys...
        if vk in self._SPECIAL_KEYS:
            return self._SPECIAL_KEYS[vk]

        # ...then try characters...
        length, chars = Quartz.CGEventKeyboardGetUnicodeString(
            event, 100, None, None)
        if length > 0:
            return KeyCode.from_char(chars, vk=vk)

        # ...and fall back on a virtual key code
        return KeyCode.from_vk(vk)
