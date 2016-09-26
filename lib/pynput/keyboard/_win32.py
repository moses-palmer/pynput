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

from pynput._util import AbstractListener, NotifierMixin
from pynput._util.win32 import *
from pynput._util.win32_vks import *
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
            r = VkKeyScan(self.char)
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
    alt = KeyCode.from_vk(VK_MENU)
    alt_l = KeyCode.from_vk(VK_LMENU)
    alt_r = KeyCode.from_vk(VK_RMENU)
    alt_gr = KeyCode.from_vk(VK_RMENU)
    backspace = KeyCode.from_vk(VK_BACK)
    caps_lock = KeyCode.from_vk(VK_CAPITAL)
    cmd = KeyCode.from_vk(VK_LWIN)
    cmd_l = KeyCode.from_vk(VK_LWIN)
    cmd_r = KeyCode.from_vk(VK_RWIN)
    ctrl = KeyCode.from_vk(VK_CONTROL)
    ctrl_l = KeyCode.from_vk(VK_LCONTROL)
    ctrl_r = KeyCode.from_vk(VK_RCONTROL)
    delete = KeyCode.from_vk(VK_DELETE)
    down = KeyCode.from_vk(VK_DOWN)
    end = KeyCode.from_vk(VK_END)
    enter = KeyCode.from_vk(VK_RETURN)
    esc = KeyCode.from_vk(VK_ESCAPE)
    f1 = KeyCode.from_vk(VK_F1)
    f2 = KeyCode.from_vk(VK_F2)
    f3 = KeyCode.from_vk(VK_F3)
    f4 = KeyCode.from_vk(VK_F4)
    f5 = KeyCode.from_vk(VK_F5)
    f6 = KeyCode.from_vk(VK_F6)
    f7 = KeyCode.from_vk(VK_F7)
    f8 = KeyCode.from_vk(VK_F8)
    f9 = KeyCode.from_vk(VK_F9)
    f10 = KeyCode.from_vk(VK_F10)
    f11 = KeyCode.from_vk(VK_F11)
    f12 = KeyCode.from_vk(VK_F12)
    f13 = KeyCode.from_vk(VK_F13)
    f14 = KeyCode.from_vk(VK_F14)
    f15 = KeyCode.from_vk(VK_F15)
    f16 = KeyCode.from_vk(VK_F16)
    f17 = KeyCode.from_vk(VK_F17)
    f18 = KeyCode.from_vk(VK_F18)
    f19 = KeyCode.from_vk(VK_F19)
    f20 = KeyCode.from_vk(VK_F20)
    home = KeyCode.from_vk(VK_HOME)
    left = KeyCode.from_vk(VK_LEFT)
    page_down = KeyCode.from_vk(VK_NEXT)
    page_up = KeyCode.from_vk(VK_PRIOR)
    right = KeyCode.from_vk(VK_RIGHT)
    shift = KeyCode.from_vk(VK_LSHIFT)
    shift_l = KeyCode.from_vk(VK_LSHIFT)
    shift_r = KeyCode.from_vk(VK_RSHIFT)
    space = KeyCode.from_vk(VK_SPACE, char=' ')
    tab = KeyCode.from_vk(VK_TAB)
    up = KeyCode.from_vk(VK_UP)

    insert = KeyCode.from_vk(VK_INSERT)
    menu = KeyCode.from_vk(VK_APPS)
    num_lock = KeyCode.from_vk(VK_NUMLOCK)
    pause = KeyCode.from_vk(VK_PAUSE)
    print_screen = KeyCode.from_vk(VK_SNAPSHOT)
    scroll_lock = KeyCode.from_vk(VK_SCROLL)


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

    def _convert(self, code, msg, lpdata):
        if code != SystemHook.HC_ACTION:
            return

        data = ctypes.cast(lpdata, self._LPKBDLLHOOKSTRUCT).contents
        return (msg, data.vkCode)

    @AbstractListener._emitter
    def _process(self, wparam, lparam):
        msg = wparam
        vk = lparam

        # Convert the event to a KeyCode; this may fail, and in that case we
        # pass None
        try:
            key = self._event_to_key(msg, vk)
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
