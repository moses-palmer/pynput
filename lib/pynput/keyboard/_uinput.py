# coding=utf-8
# pynput
# Copyright (C) 2015-2020 Moses Palmér
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
The keyboard implementation for *uinput*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import enum

from pynput._util.uinput import ListenerMixin
from . import _base


class KeyCode(_base.KeyCode):
    _PLATFORM_EXTENSIONS = (
        # The name for this key
        '_x_name',
        '_kernel_name',
    )

    # Be explicit about fields
    _x_name = None
    _kernel_name = None
# pylint: enable=W0212

    @classmethod
    def _from_name(cls, x_name, kernel_name, **kwargs):
        """Creates a key from a name.

        :param str x_name: The X name.

        :param str kernel_name: The kernel name.

        :return: a key code
        """
        try:
            vk = getattr(evdev.ecodes, kernel_name)
        except AttributeError:
            vk = None
        return cls.from_vk(
            vk, _x_name=x_name, _kernel_name=kernel_name, **kwargs)

# pylint: disable=W0212
class Key(enum.Enum):
    alt = KeyCode._from_name('Alt_L', 'KEY_LEFTALT')
    alt_l = KeyCode._from_name('Alt_L', 'KEY_LEFTALT')
    alt_r = KeyCode._from_name('Alt_R', 'KEY_RIGHTALT')
    alt_gr = KeyCode._from_name('Mode_switch', 'KEY_RIGHTALT')
    backspace = KeyCode._from_name('BackSpace', 'KEY_BACKSPACE')
    caps_lock = KeyCode._from_name('Caps_Lock', 'KEY_CAPSLOCK')
    cmd = KeyCode._from_name('Super_L', 'KEY_LEFTMETA')
    cmd_l = KeyCode._from_name('Super_L', 'KEY_LEFTMETA')
    cmd_r = KeyCode._from_name('Super_R', 'KEY_RIGHTMETA')
    ctrl = KeyCode._from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_l = KeyCode._from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_r = KeyCode._from_name('Control_R', 'KEY_RIGHTCTRL')
    delete = KeyCode._from_name('Delete', 'KEY_DELETE')
    down = KeyCode._from_name('Down', 'KEY_DOWN')
    end = KeyCode._from_name('End', 'KEY_END')
    enter = KeyCode._from_name('Return', 'KEY_ENTER')
    esc = KeyCode._from_name('Escape', 'KEY_ESC')
    f1 = KeyCode._from_name('F1', 'KEY_F1')
    f2 = KeyCode._from_name('F2', 'KEY_F2')
    f3 = KeyCode._from_name('F3', 'KEY_F3')
    f4 = KeyCode._from_name('F4', 'KEY_F4')
    f5 = KeyCode._from_name('F5', 'KEY_F5')
    f6 = KeyCode._from_name('F6', 'KEY_F6')
    f7 = KeyCode._from_name('F7', 'KEY_F7')
    f8 = KeyCode._from_name('F8', 'KEY_F8')
    f9 = KeyCode._from_name('F9', 'KEY_F9')
    f10 = KeyCode._from_name('F10', 'KEY_F10')
    f11 = KeyCode._from_name('F11', 'KEY_F11')
    f12 = KeyCode._from_name('F12', 'KEY_F12')
    f13 = KeyCode._from_name('F13', 'KEY_F13')
    f14 = KeyCode._from_name('F14', 'KEY_F14')
    f15 = KeyCode._from_name('F15', 'KEY_F15')
    f16 = KeyCode._from_name('F16', 'KEY_F16')
    f17 = KeyCode._from_name('F17', 'KEY_F17')
    f18 = KeyCode._from_name('F18', 'KEY_F18')
    f19 = KeyCode._from_name('F19', 'KEY_F19')
    f20 = KeyCode._from_name('F20', 'KEY_F20')
    home = KeyCode._from_name('Home', 'KEY_HOME')
    left = KeyCode._from_name('Left', 'KEY_LEFT')
    page_down = KeyCode._from_name('Page_Down', 'KEY_PAGEDOWN')
    page_up = KeyCode._from_name('Page_Up', 'KEY_PAGEUP')
    right = KeyCode._from_name('Right', 'KEY_RIGHT')
    shift = KeyCode._from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_l = KeyCode._from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_r = KeyCode._from_name('Shift_R', 'KEY_RIGHTSHIFT')
    space = KeyCode._from_name('space', 'KEY_SPACE', char=' ')
    tab = KeyCode._from_name('Tab', 'KEY_TAB', char='\t')
    up = KeyCode._from_name('Up', 'KEY_UP')

    media_play_pause = KeyCode._from_name('Play', 'KEY_PLAYPAUSE')
    media_volume_mute = KeyCode._from_name('Mute', 'KEY_MUTE')
    media_volume_down = KeyCode._from_name('LowerVolume', 'KEY_VOLUMEDOWN')
    media_volume_up = KeyCode._from_name('RaiseVolume', 'KEY_VOLUMEUP')
    media_previous = KeyCode._from_name('Prev', 'KEY_PREVIOUSSONG')
    media_next = KeyCode._from_name('Next', 'KEY_NEXTSONG')

    insert = KeyCode._from_name('Insert', 'KEY_INSERT')
    menu = KeyCode._from_name('Menu', 'KEY_MENU')
    num_lock = KeyCode._from_name('Num_Lock', 'KEY_NUMLOCK')
    pause = KeyCode._from_name('Pause', 'KEY_PAUSE')
    print_screen = KeyCode._from_name('Print', 'KEY_SYSRQ')
    scroll_lock = KeyCode._from_name('Scroll_Lock', 'KEY_SCROLLLOCK')
# pylint: enable=W0212


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        # TODO: Implement
        raise NotImplementedError()

    def _handle(self, key, is_press):
        # TODO: Implement
        raise NotImplementedError()


class Listener(ListenerMixin, _base.Listener):
    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        # TODO: Implement
        raise NotImplementedError()
