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
    # TODO: Implement!
    _PLATFORM_EXTENSIONS = tuple()


# pylint: disable=W0212
class Key(enum.Enum):
    # TODO: Implement!
    # Default keys
    alt = None
    alt_l = None
    alt_r = None
    alt_gr = None
    backspace = None
    caps_lock = None
    cmd = None
    cmd_l = None
    cmd_r = None
    ctrl = None
    ctrl_l = None
    ctrl_r = None
    delete = None
    down = None
    end = None
    enter = None
    esc = None
    f1 = None
    f2 = None
    f3 = None
    f4 = None
    f5 = None
    f6 = None
    f7 = None
    f8 = None
    f9 = None
    f10 = None
    f11 = None
    f12 = None
    f13 = None
    f14 = None
    f15 = None
    f16 = None
    f17 = None
    f18 = None
    f19 = None
    f20 = None
    home = None
    left = None
    page_down = None
    page_up = None
    right = None
    shift = None
    shift_l = None
    shift_r = None
    space = None
    tab = None
    up = None

    media_play_pause = None
    media_volume_mute = None
    media_volume_down = None
    media_volume_up = None
    media_previous = None
    media_next = None

    insert = None
    menu = None
    num_lock = None
    pause = None
    print_screen = None
    scroll_lock = None
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
