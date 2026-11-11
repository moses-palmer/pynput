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
"""
The keyboard implementation for *libei*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import enum

from pynput._util.libei import ListenerMixin, session
from . import _base


class KeyCode(_base.KeyCode):
    _PLATFORM_EXTENSIONS = (
        # The name of the key in linux/input-event-codes.h
        '_kernel_name',
    )

    # Be explicit about fields
    _kernel_name = None

    @classmethod
    def _from_name(cls, kernel_name, **kwargs):
        """Creates a key from its kernel name.

        :param str kernel_name: The name of the key in
            ``linux/input-event-codes.h``.

        :return: a key code
        """
        return cls.from_vk(
            KERNEL_KEYS[kernel_name], _kernel_name=kernel_name, **kwargs)


#: The kernel keycodes of the keys below, from
#: ``linux/input-event-codes.h``.
#:
#: These are spelled out rather than read from ``evdev.ecodes`` for the same
#: reason the mouse buttons are: they are a stable kernel *ABI*, and this
#: backend exists for the case where the *evdev* device cannot be opened.
KERNEL_KEYS = {
    'KEY_ESC': 1,
    'KEY_BACKSPACE': 14,
    'KEY_TAB': 15,
    'KEY_ENTER': 28,
    'KEY_LEFTCTRL': 29,
    'KEY_LEFTSHIFT': 42,
    'KEY_RIGHTSHIFT': 54,
    'KEY_LEFTALT': 56,
    'KEY_SPACE': 57,
    'KEY_CAPSLOCK': 58,
    'KEY_F1': 59,
    'KEY_F2': 60,
    'KEY_F3': 61,
    'KEY_F4': 62,
    'KEY_F5': 63,
    'KEY_F6': 64,
    'KEY_F7': 65,
    'KEY_F8': 66,
    'KEY_F9': 67,
    'KEY_F10': 68,
    'KEY_NUMLOCK': 69,
    'KEY_SCROLLLOCK': 70,
    'KEY_F11': 87,
    'KEY_F12': 88,
    'KEY_RIGHTCTRL': 97,
    'KEY_SYSRQ': 99,
    'KEY_RIGHTALT': 100,
    'KEY_HOME': 102,
    'KEY_UP': 103,
    'KEY_PAGEUP': 104,
    'KEY_LEFT': 105,
    'KEY_RIGHT': 106,
    'KEY_END': 107,
    'KEY_DOWN': 108,
    'KEY_PAGEDOWN': 109,
    'KEY_INSERT': 110,
    'KEY_DELETE': 111,
    'KEY_MUTE': 113,
    'KEY_VOLUMEDOWN': 114,
    'KEY_VOLUMEUP': 115,
    'KEY_PAUSE': 119,
    'KEY_LEFTMETA': 125,
    'KEY_RIGHTMETA': 126,
    'KEY_MENU': 139,
    'KEY_NEXTSONG': 163,
    'KEY_PLAYPAUSE': 164,
    'KEY_PREVIOUSSONG': 165,
    'KEY_STOPCD': 166,
    'KEY_F13': 183,
    'KEY_F14': 184,
    'KEY_F15': 185,
    'KEY_F16': 186,
    'KEY_F17': 187,
    'KEY_F18': 188,
    'KEY_F19': 189,
    'KEY_F20': 190,
}


# pylint: disable=W0212
class Key(enum.Enum):
    alt = KeyCode._from_name('KEY_LEFTALT')
    alt_l = KeyCode._from_name('KEY_LEFTALT')
    alt_r = KeyCode._from_name('KEY_RIGHTALT')
    alt_gr = KeyCode._from_name('KEY_RIGHTALT')
    backspace = KeyCode._from_name('KEY_BACKSPACE')
    caps_lock = KeyCode._from_name('KEY_CAPSLOCK')
    cmd = KeyCode._from_name('KEY_LEFTMETA')
    cmd_l = KeyCode._from_name('KEY_LEFTMETA')
    cmd_r = KeyCode._from_name('KEY_RIGHTMETA')
    ctrl = KeyCode._from_name('KEY_LEFTCTRL')
    ctrl_l = KeyCode._from_name('KEY_LEFTCTRL')
    ctrl_r = KeyCode._from_name('KEY_RIGHTCTRL')
    delete = KeyCode._from_name('KEY_DELETE')
    down = KeyCode._from_name('KEY_DOWN')
    end = KeyCode._from_name('KEY_END')
    enter = KeyCode._from_name('KEY_ENTER')
    esc = KeyCode._from_name('KEY_ESC')
    f1 = KeyCode._from_name('KEY_F1')
    f2 = KeyCode._from_name('KEY_F2')
    f3 = KeyCode._from_name('KEY_F3')
    f4 = KeyCode._from_name('KEY_F4')
    f5 = KeyCode._from_name('KEY_F5')
    f6 = KeyCode._from_name('KEY_F6')
    f7 = KeyCode._from_name('KEY_F7')
    f8 = KeyCode._from_name('KEY_F8')
    f9 = KeyCode._from_name('KEY_F9')
    f10 = KeyCode._from_name('KEY_F10')
    f11 = KeyCode._from_name('KEY_F11')
    f12 = KeyCode._from_name('KEY_F12')
    f13 = KeyCode._from_name('KEY_F13')
    f14 = KeyCode._from_name('KEY_F14')
    f15 = KeyCode._from_name('KEY_F15')
    f16 = KeyCode._from_name('KEY_F16')
    f17 = KeyCode._from_name('KEY_F17')
    f18 = KeyCode._from_name('KEY_F18')
    f19 = KeyCode._from_name('KEY_F19')
    f20 = KeyCode._from_name('KEY_F20')
    home = KeyCode._from_name('KEY_HOME')
    left = KeyCode._from_name('KEY_LEFT')
    page_down = KeyCode._from_name('KEY_PAGEDOWN')
    page_up = KeyCode._from_name('KEY_PAGEUP')
    right = KeyCode._from_name('KEY_RIGHT')
    shift = KeyCode._from_name('KEY_LEFTSHIFT')
    shift_l = KeyCode._from_name('KEY_LEFTSHIFT')
    shift_r = KeyCode._from_name('KEY_RIGHTSHIFT')
    space = KeyCode._from_name('KEY_SPACE', char=' ')
    tab = KeyCode._from_name('KEY_TAB', char='\t')
    up = KeyCode._from_name('KEY_UP')

    media_play_pause = KeyCode._from_name('KEY_PLAYPAUSE')
    media_volume_mute = KeyCode._from_name('KEY_MUTE')
    media_volume_down = KeyCode._from_name('KEY_VOLUMEDOWN')
    media_volume_up = KeyCode._from_name('KEY_VOLUMEUP')
    media_previous = KeyCode._from_name('KEY_PREVIOUSSONG')
    media_next = KeyCode._from_name('KEY_NEXTSONG')
    media_stop = KeyCode._from_name('KEY_STOPCD')

    insert = KeyCode._from_name('KEY_INSERT')
    menu = KeyCode._from_name('KEY_MENU')
    num_lock = KeyCode._from_name('KEY_NUMLOCK')
    pause = KeyCode._from_name('KEY_PAUSE')
    print_screen = KeyCode._from_name('KEY_SYSRQ')
    scroll_lock = KeyCode._from_name('KEY_SCROLLLOCK')


# pylint: enable=W0212


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self._session = session()

    def _handle(self, key, is_press):
        keycode, shifted = self._resolve_keycode(key)

        # Shift is pressed around the key only when the layout needs it and
        # the caller is not already holding it; releasing it afterwards when
        # the caller holds it down would break the rest of their sequence
        if shifted and is_press and not self.shift_pressed:
            self._session.keyboard_key(Key.shift.value.vk, True)
            try:
                self._send(keycode, True)
            finally:
                self._session.keyboard_key(Key.shift.value.vk, False)
        else:
            self._send(keycode, is_press)

    def _send(self, keycode, is_press):
        """Sends a single key event.

        :param int keycode: The kernel keycode.

        :param bool is_press: Whether this is a press event.
        """
        self._session.keyboard_key(keycode, is_press)

    def _resolve_keycode(self, key):
        """Resolves a key to a kernel keycode.

        :param KeyCode key: The key to resolve.

        :return: the tuple ``(keycode, shifted)``, where ``shifted`` is
            whether the shift modifier is needed to produce the character

        :raises Controller.InvalidKeyException: if the key cannot be sent
        """
        # A key with a virtual key code is a position, which needs no layout
        if getattr(key, 'vk', None) is not None:
            return (key.vk, False)

        character = getattr(key, 'char', None)
        if character is None:
            raise self.InvalidKeyException(key)

        # A character is not a position, so the layout has to say which key
        # produces it. The compositor hands its layout over with the keyboard
        # device, but interpreting it needs libxkbcommon
        keymap = self._session.keymap
        if keymap is None:
            raise self.InvalidKeyException(
                key,
                'the keyboard layout is unavailable; install the xkbcommon '
                'package to type characters with the libei backend')
        resolved = keymap.get(character)
        if resolved is None:
            raise self.InvalidKeyException(
                key,
                'the character {!r} cannot be typed with the current '
                'keyboard layout'.format(character))
        return resolved


class Listener(ListenerMixin, _base.Listener):
    pass
