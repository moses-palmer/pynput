# coding=utf-8
# pynput
# Copyright (C) 2015-2021 Moses Palmér
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
The keyboard implementation for *Windows*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import contextlib
import ctypes
import enum
import six

from ctypes import wintypes

import pynput._util.win32_vks as VK

from pynput._util import AbstractListener
from pynput._util.win32 import (
    INPUT,
    INPUT_union,
    KEYBDINPUT,
    KeyTranslator,
    ListenerMixin,
    SendInput,
    SystemHook,
    VkKeyScan)
from . import _base


class KeyCode(_base.KeyCode):
    _PLATFORM_EXTENSIONS = (
        # Any extra flags.
        '_flags',

        #: The scan code.
        '_scan',
    )

    # Be explicit about fields
    _flags = None
    _scan = None

    def _parameters(self, is_press):
        """The parameters to pass to ``SendInput`` to generate this key.

        :param bool is_press: Whether to generate a press event.

        :return: all arguments to pass to ``SendInput`` for this key

        :rtype: dict
        """
        if self.vk:
            vk = self.vk
            scan = self._scan or 0
            flags = 0
        else:
            res = VkKeyScan(self.char)
            if (res >> 8) & 0xFF == 0:
                vk = res & 0xFF
                scan = self._scan or 0
                flags = 0
            else:
                vk = 0
                scan = ord(self.char)
                flags = KEYBDINPUT.UNICODE
        state_flags = (KEYBDINPUT.KEYUP if not is_press else 0)
        return dict(
            dwFlags=(self._flags or 0) | flags | state_flags,
            wVk=vk,
            wScan=scan)

    @classmethod
    def _from_ext(cls, vk, **kwargs):
        """Creates an extended key code.

        :param vk: The virtual key code.

        :param kwargs: Any other parameters to pass.

        :return: a key code
        """
        return cls.from_vk(vk, _flags=KEYBDINPUT.EXTENDEDKEY, **kwargs)


# pylint: disable=W0212
class Key(enum.Enum):
    alt = KeyCode.from_vk(VK.MENU)
    alt_l = KeyCode.from_vk(VK.LMENU)
    alt_r = KeyCode._from_ext(VK.RMENU)
    alt_gr = KeyCode.from_vk(VK.RMENU)
    backspace = KeyCode.from_vk(VK.BACK)
    caps_lock = KeyCode.from_vk(VK.CAPITAL)
    cmd = KeyCode.from_vk(VK.LWIN)
    cmd_l = KeyCode.from_vk(VK.LWIN)
    cmd_r = KeyCode.from_vk(VK.RWIN)
    ctrl = KeyCode.from_vk(VK.CONTROL)
    ctrl_l = KeyCode.from_vk(VK.LCONTROL)
    ctrl_r = KeyCode._from_ext(VK.RCONTROL)
    delete = KeyCode._from_ext(VK.DELETE)
    down = KeyCode._from_ext(VK.DOWN)
    end = KeyCode._from_ext(VK.END)
    enter = KeyCode.from_vk(VK.RETURN)
    esc = KeyCode.from_vk(VK.ESCAPE)
    f1 = KeyCode.from_vk(VK.F1)
    f2 = KeyCode.from_vk(VK.F2)
    f3 = KeyCode.from_vk(VK.F3)
    f4 = KeyCode.from_vk(VK.F4)
    f5 = KeyCode.from_vk(VK.F5)
    f6 = KeyCode.from_vk(VK.F6)
    f7 = KeyCode.from_vk(VK.F7)
    f8 = KeyCode.from_vk(VK.F8)
    f9 = KeyCode.from_vk(VK.F9)
    f10 = KeyCode.from_vk(VK.F10)
    f11 = KeyCode.from_vk(VK.F11)
    f12 = KeyCode.from_vk(VK.F12)
    f13 = KeyCode.from_vk(VK.F13)
    f14 = KeyCode.from_vk(VK.F14)
    f15 = KeyCode.from_vk(VK.F15)
    f16 = KeyCode.from_vk(VK.F16)
    f17 = KeyCode.from_vk(VK.F17)
    f18 = KeyCode.from_vk(VK.F18)
    f19 = KeyCode.from_vk(VK.F19)
    f20 = KeyCode.from_vk(VK.F20)
    f21 = KeyCode.from_vk(VK.F21)
    f22 = KeyCode.from_vk(VK.F22)
    f23 = KeyCode.from_vk(VK.F23)
    f24 = KeyCode.from_vk(VK.F24)
    home = KeyCode._from_ext(VK.HOME)
    left = KeyCode._from_ext(VK.LEFT)
    page_down = KeyCode._from_ext(VK.NEXT)
    page_up = KeyCode._from_ext(VK.PRIOR)
    right = KeyCode._from_ext(VK.RIGHT)
    shift = KeyCode.from_vk(VK.LSHIFT)
    shift_l = KeyCode.from_vk(VK.LSHIFT)
    shift_r = KeyCode.from_vk(VK.RSHIFT)
    space = KeyCode.from_vk(VK.SPACE, char=' ')
    tab = KeyCode.from_vk(VK.TAB)
    up = KeyCode._from_ext(VK.UP)

    media_play_pause = KeyCode._from_ext(VK.MEDIA_PLAY_PAUSE)
    media_volume_mute = KeyCode._from_ext(VK.VOLUME_MUTE)
    media_volume_down = KeyCode._from_ext(VK.VOLUME_DOWN)
    media_volume_up = KeyCode._from_ext(VK.VOLUME_UP)
    media_previous = KeyCode._from_ext(VK.MEDIA_PREV_TRACK)
    media_next = KeyCode._from_ext(VK.MEDIA_NEXT_TRACK)

    insert = KeyCode._from_ext(VK.INSERT)
    menu = KeyCode.from_vk(VK.APPS)
    num_lock = KeyCode._from_ext(VK.NUMLOCK)
    pause = KeyCode.from_vk(VK.PAUSE)
    print_screen = KeyCode._from_ext(VK.SNAPSHOT)
    scroll_lock = KeyCode.from_vk(VK.SCROLL)
# pylint: enable=W0212


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)

    def _handle(self, key, is_press):
        SendInput(
            1,
            ctypes.byref(INPUT(
                type=INPUT.KEYBOARD,
                value=INPUT_union(
                    ki=KEYBDINPUT(**key._parameters(is_press))))),
            ctypes.sizeof(INPUT))


class Listener(ListenerMixin, _base.Listener):
    #: The Windows hook ID for low level keyboard events, ``WH_KEYBOARD_LL``
    _EVENTS = 13

    _WM_INPUTLANGCHANGE = 0x0051
    _WM_KEYDOWN = 0x0100
    _WM_KEYUP = 0x0101
    _WM_SYSKEYDOWN = 0x0104
    _WM_SYSKEYUP = 0x0105

    # A bit flag attached to messages indicating that the payload is an actual
    # UTF-16 character code
    _UTF16_FLAG = 0x1000

    # A special virtual key code designating unicode characters
    _VK_PACKET = 0xE7

    #: The messages that correspond to a key press
    _PRESS_MESSAGES = (_WM_KEYDOWN, _WM_SYSKEYDOWN)

    #: The messages that correspond to a key release
    _RELEASE_MESSAGES = (_WM_KEYUP, _WM_SYSKEYUP)

    #: Additional window messages to propagate to the subclass handler.
    _WM_NOTIFICATIONS = (
        _WM_INPUTLANGCHANGE,
    )

    #: A mapping from keysym to special key
    _SPECIAL_KEYS = {
        key.value.vk: key
        for key in Key}

    _HANDLED_EXCEPTIONS = (
        SystemHook.SuppressException,)

    class _KBDLLHOOKSTRUCT(ctypes.Structure):
        """Contains information about a mouse event passed to a
        ``WH_KEYBOARD_LL`` hook procedure, ``LowLevelKeyboardProc``.
        """
        _fields_ = [
            ('vkCode', wintypes.DWORD),
            ('scanCode', wintypes.DWORD),
            ('flags', wintypes.DWORD),
            ('time', wintypes.DWORD),
            ('dwExtraInfo', ctypes.c_void_p)]

    #: A pointer to a :class:`KBDLLHOOKSTRUCT`
    _LPKBDLLHOOKSTRUCT = ctypes.POINTER(_KBDLLHOOKSTRUCT)

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._translator = KeyTranslator()
        self._event_filter = self._options.get(
            'event_filter',
            lambda msg, data: True)

    def _convert(self, code, msg, lpdata):
        if code != SystemHook.HC_ACTION:
            return

        data = ctypes.cast(lpdata, self._LPKBDLLHOOKSTRUCT).contents
        is_packet = data.vkCode == self._VK_PACKET

        # Suppress further propagation of the event if it is filtered
        if self._event_filter(msg, data) is False:
            return None
        elif is_packet:
            return (msg | self._UTF16_FLAG, data.scanCode)
        else:
            return (msg, data.vkCode)

    @AbstractListener._emitter
    def _process(self, wparam, lparam):
        msg = wparam
        vk = lparam

        # If the key has the UTF-16 flag, we treat it as a unicode character,
        # otherwise convert the event to a KeyCode; this may fail, and in that
        # case we pass None
        is_utf16 = msg & self._UTF16_FLAG
        if is_utf16:
            msg = msg ^ self._UTF16_FLAG
            scan = vk
            key = KeyCode.from_char(six.unichr(scan))
        else:
            try:
                key = self._event_to_key(msg, vk)
            except OSError:
                key = None

        if msg in self._PRESS_MESSAGES:
            self.on_press(key)

        elif msg in self._RELEASE_MESSAGES:
            self.on_release(key)

    # pylint: disable=R0201
    @contextlib.contextmanager
    def _receive(self):
        """An empty context manager; we do not need to fake keyboard events.
        """
        yield
    # pylint: enable=R0201

    def _on_notification(self, code, wparam, lparam):
        """Receives ``WM_INPUTLANGCHANGE`` and updates the cached layout.
        """
        if code == self._WM_INPUTLANGCHANGE:
            self._translator.update_layout()

    def _event_to_key(self, msg, vk):
        """Converts an :class:`_KBDLLHOOKSTRUCT` to a :class:`KeyCode`.

        :param msg: The message received.

        :param vk: The virtual key code to convert.

        :return: a :class:`pynput.keyboard.KeyCode`

        :raises OSError: if the message and data could not be converted
        """
        # If the virtual key code corresponds to a Key value, we prefer that
        if vk in self._SPECIAL_KEYS:
            return self._SPECIAL_KEYS[vk]
        else:
            return KeyCode(**self._translate(
                vk,
                msg in self._PRESS_MESSAGES))

    def _translate(self, vk, is_press):
        """Translates a virtual key code to a parameter list passable to
        :class:`pynput.keyboard.KeyCode`.

        :param int vk: The virtual key code.

        :param bool is_press: Whether this is a press event.

        :return: a parameter list to the :class:`pynput.keyboard.KeyCode`
            constructor
        """
        return self._translator(vk, is_press)

    def canonical(self, key):
        # If the key has a scan code, and we can find the character for it,
        # return that, otherwise call the super class
        scan = getattr(key, '_scan', None)
        if scan is not None:
            char = self._translator.char_from_scan(scan)
            if char is not None:
                return KeyCode.from_char(char)

        return super(Listener, self).canonical(key)
