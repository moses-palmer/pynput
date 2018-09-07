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

from pynput._util import AbstractListener, NotifierMixin
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
    def _parameters(self, is_press):
        """The parameters to pass to ``SendInput`` to generate this key.

        :param bool is_press: Whether to generate a press event.

        :return: all arguments to pass to ``SendInput`` for this key

        :rtype: dict
        """
        if self.vk:
            vk = self.vk
            scan = 0
            flags = 0
        else:
            res = VkKeyScan(self.char)
            if (res >> 8) & 0xFF == 0:
                vk = res & 0xFF
                scan = 0
                flags = 0
            else:
                vk = 0
                scan = ord(self.char)
                flags = KEYBDINPUT.UNICODE
        return dict(
            dwFlags=flags | (KEYBDINPUT.KEYUP if not is_press else 0),
            wVk=vk,
            wScan=scan)


class Key(enum.Enum):
    alt = KeyCode.from_vk(VK.MENU)
    alt_l = KeyCode.from_vk(VK.LMENU)
    alt_r = KeyCode.from_vk(VK.RMENU)
    alt_gr = KeyCode.from_vk(VK.RMENU)
    backspace = KeyCode.from_vk(VK.BACK)
    caps_lock = KeyCode.from_vk(VK.CAPITAL)
    cmd = KeyCode.from_vk(VK.LWIN)
    cmd_l = KeyCode.from_vk(VK.LWIN)
    cmd_r = KeyCode.from_vk(VK.RWIN)
    ctrl = KeyCode.from_vk(VK.CONTROL)
    ctrl_l = KeyCode.from_vk(VK.LCONTROL)
    ctrl_r = KeyCode.from_vk(VK.RCONTROL)
    delete = KeyCode.from_vk(VK.DELETE)
    down = KeyCode.from_vk(VK.DOWN)
    end = KeyCode.from_vk(VK.END)
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
    home = KeyCode.from_vk(VK.HOME)
    left = KeyCode.from_vk(VK.LEFT)
    page_down = KeyCode.from_vk(VK.NEXT)
    page_up = KeyCode.from_vk(VK.PRIOR)
    right = KeyCode.from_vk(VK.RIGHT)
    shift = KeyCode.from_vk(VK.LSHIFT)
    shift_l = KeyCode.from_vk(VK.LSHIFT)
    shift_r = KeyCode.from_vk(VK.RSHIFT)
    space = KeyCode.from_vk(VK.SPACE, char=' ')
    tab = KeyCode.from_vk(VK.TAB)
    up = KeyCode.from_vk(VK.UP)

    insert = KeyCode.from_vk(VK.INSERT)
    menu = KeyCode.from_vk(VK.APPS)
    num_lock = KeyCode.from_vk(VK.NUMLOCK)
    pause = KeyCode.from_vk(VK.PAUSE)
    print_screen = KeyCode.from_vk(VK.SNAPSHOT)
    scroll_lock = KeyCode.from_vk(VK.SCROLL)


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

    def _event_to_key(self, msg, vk):
        """Converts an :class:`_KBDLLHOOKSTRUCT` to a :class:`KeyCode`.

        :param msg: The message received.

        :param vk: The virtual key code to convert.

        :return: a :class:`pynput.keyboard.KeyCode`

        :raises OSError: if the message and data could not be converted
        """
        # We must always call self._translate to keep the keyboard state up to
        # date
        key = KeyCode(**self._translate(
            vk,
            msg in self._PRESS_MESSAGES))

        # If the virtual key code corresponds to a Key value, we prefer that
        if vk in self._SPECIAL_KEYS:
            return self._SPECIAL_KEYS[vk]
        else:
            return key

    def _translate(self, vk, is_press):
        """Translates a virtual key code to a parameter list passable to
        :class:`pynput.keyboard.KeyCode`.

        :param int vk: The virtual key code.

        :param bool is_press: Whether this is a press event.

        :return: a paramter list to the :class:`pynput.keyboard.KeyCode`
            constructor
        """
        return self._translator(vk, is_press)
