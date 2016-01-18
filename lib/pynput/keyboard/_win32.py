# coding=utf-8
# pynput
# Copyright (C) 2015 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import enum

from pynput._util.win32 import *
from . import _base


class KeyCode(_base.KeyCode):
    def parameters(self, is_press):
        """The parameters to pass to ``SendInput`` to generate this key.
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
    space = KeyCode(vk=0x20, char=' ')
    tab = KeyCode.from_vk(0x09)
    up = KeyCode.from_vk(0x26)

    insert = KeyCode.from_vk(0x2D)
    menu = KeyCode.from_vk(0x5D)
    num_lock = KeyCode.from_vk(0x90)
    pause = KeyCode.from_vk(0x13)
    print_screen = KeyCode.from_vk(0x2C)
    scroll_lock = KeyCode.from_vk(0x91)


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def _handle(self, key, is_press):
        SendInput(
            1,
            ctypes.byref(INPUT(
                type=INPUT.KEYBOARD,
                value=INPUT_union(
                    ki=KEYBDINPUT(**key.parameters(is_press))))),
            ctypes.sizeof(INPUT))
