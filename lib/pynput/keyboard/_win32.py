# coding=utf-8
# pynput
# Copyright (C) 2015-2016 Moses Palmér
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

import enum

from pynput._util import NotifierMixin
from pynput._util.win32 import *
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
            r = VkKeyScan(ord(self.char))
            if (r >> 8) & 0xFF == 0:
                vk = r & 0xFF
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
    alt = KeyCode.from_vk(0x12)
    alt_l = KeyCode.from_vk(0xA4)
    alt_r = KeyCode.from_vk(0xA5)
    alt_gr = KeyCode.from_vk(0xA5)
    backspace = KeyCode.from_vk(0x08)
    caps_lock = KeyCode.from_vk(0x14)
    cmd = KeyCode.from_vk(0x5B)
    cmd_l = KeyCode.from_vk(0x5B)
    cmd_r = KeyCode.from_vk(0xA4)
    ctrl = KeyCode.from_vk(0x11)
    ctrl_l = KeyCode.from_vk(0xA2)
    ctrl_r = KeyCode.from_vk(0xA3)
    delete = KeyCode.from_vk(0x2E)
    down = KeyCode.from_vk(0x28)
    end = KeyCode.from_vk(0x23)
    enter = KeyCode.from_vk(0x0D)
    esc = KeyCode.from_vk(0x1B)
    f1 = KeyCode.from_vk(0x70)
    f2 = KeyCode.from_vk(0x71)
    f3 = KeyCode.from_vk(0x72)
    f4 = KeyCode.from_vk(0x73)
    f5 = KeyCode.from_vk(0x74)
    f6 = KeyCode.from_vk(0x75)
    f7 = KeyCode.from_vk(0x76)
    f8 = KeyCode.from_vk(0x77)
    f9 = KeyCode.from_vk(0x78)
    f10 = KeyCode.from_vk(0x79)
    f11 = KeyCode.from_vk(0x7A)
    f12 = KeyCode.from_vk(0x7B)
    f13 = KeyCode.from_vk(0x7C)
    f14 = KeyCode.from_vk(0x7D)
    f15 = KeyCode.from_vk(0x7E)
    f16 = KeyCode.from_vk(0x7F)
    f17 = KeyCode.from_vk(0x80)
    f18 = KeyCode.from_vk(0x81)
    f19 = KeyCode.from_vk(0x82)
    f20 = KeyCode.from_vk(0x83)
    home = KeyCode.from_vk(0x24)
    left = KeyCode.from_vk(0x25)
    page_down = KeyCode.from_vk(0x22)
    page_up = KeyCode.from_vk(0x21)
    right = KeyCode.from_vk(0x27)
    shift = KeyCode.from_vk(0xA0)
    shift_l = KeyCode.from_vk(0xA0)
    shift_r = KeyCode.from_vk(0xA1)
    space = KeyCode.from_vk(0x20, char=' ')
    tab = KeyCode.from_vk(0x09)
    up = KeyCode.from_vk(0x26)

    insert = KeyCode.from_vk(0x2D)
    menu = KeyCode.from_vk(0x5D)
    num_lock = KeyCode.from_vk(0x90)
    pause = KeyCode.from_vk(0x13)
    print_screen = KeyCode.from_vk(0x2C)
    scroll_lock = KeyCode.from_vk(0x91)


class Controller(NotifierMixin, _base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def _handle(self, key, is_press):
        SendInput(
            1,
            ctypes.byref(INPUT(
                type=INPUT.KEYBOARD,
                value=INPUT_union(
                    ki=KEYBDINPUT(**key._parameters(is_press))))),
            ctypes.sizeof(INPUT))

        # Notify any running listeners
        self._emit('_on_fake_event', key, is_press)


@Controller._receiver
class Listener(ListenerMixin, _base.Listener):
    #: The Windows hook ID for low level keyboard events, ``WH_KEYBOARD_LL``
    _EVENTS = 13

    _WM_KEYDOWN = 0x0100
    _WM_KEYUP = 0x0101
    _WM_SYSKEYDOWN = 0x0104
    _WM_SYSKEYUP = 0x0105

    #: The messages that correspond to a key press
    _PRESS_MESSAGES = (_WM_KEYDOWN, _WM_SYSKEYDOWN)

    #: The messages that correspond to a key release
    _RELEASE_MESSAGES = (_WM_KEYUP, _WM_SYSKEYUP)

    #: A mapping from keysym to special key
    _SPECIAL_KEYS = {
        key.value.vk: key
        for key in Key}

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._translate = KeyTranslator()

    def _event_to_key(self, msg, data):
        """Converts an :class:`_KBDLLHOOKSTRUCT` to a :class:`KeyCode`.

        :param msg: The message received.

        :param data: The data to convert.

        :return: a :class:`pynput.keyboard.KeyCode`

        :raises OSError: if the message and data could not be converted
        """
        # We must always call self._translate to keep the keyboard state up to
        # date
        key = KeyCode(**self._translate(
            data.vkCode,
            msg in self._PRESS_MESSAGES))

        # If the virtual key code corresponds to a Key value, we prefer that
        if data.vkCode in self._SPECIAL_KEYS:
            return self._SPECIAL_KEYS[data.vkCode]
        else:
            return key

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

    def _handle(self, code, msg, lpdata):
        if code != SystemHook.HC_ACTION:
            return

        data = ctypes.cast(lpdata, self._LPKBDLLHOOKSTRUCT).contents

        # Convert the event to a KeyCode; this may fail, and in that case we
        # pass None
        try:
            key = self._event_to_key(msg, data)
        except OSError:
            key = None
        except:
            # TODO: Error reporting
            return

        if msg in self._PRESS_MESSAGES:
            self.on_press(key)

        elif msg in self._RELEASE_MESSAGES:
            self.on_release(key)

    def _on_fake_event(self, key, is_press):
        """The handler for fake press events sent by the controllers.

        :param KeyCode key: The key pressed.

        :param bool is_press: Whether this is a press event.
        """
        (self.on_press if is_press else self.on_release)(
            self._SPECIAL_KEYS.get(key.vk, key))
