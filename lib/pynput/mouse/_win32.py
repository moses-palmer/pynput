# coding=utf-8
# pynput
# Copyright (C) 2015-2019 Moses Palmér
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
The mouse implementation for *Windows*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import ctypes
import enum

from ctypes import (
    windll,
    wintypes)

from pynput._util import NotifierMixin
from pynput._util.win32 import (
    INPUT,
    INPUT_union,
    ListenerMixin,
    MOUSEINPUT,
    SendInput,
    SystemHook)
from . import _base


class Button(enum.Enum):
    """The various buttons.
    """
    unknown = None
    left = (MOUSEINPUT.LEFTUP, MOUSEINPUT.LEFTDOWN)
    middle = (MOUSEINPUT.MIDDLEUP, MOUSEINPUT.MIDDLEDOWN)
    right = (MOUSEINPUT.RIGHTUP, MOUSEINPUT.RIGHTDOWN)


class Controller(NotifierMixin, _base.Controller):
    __GetCursorPos = windll.user32.GetCursorPos
    __SetCursorPos = windll.user32.SetCursorPos

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)

    def _position_get(self):
        point = wintypes.POINT()
        if self.__GetCursorPos(ctypes.byref(point)):
            return (point.x, point.y)
        else:
            return None

    def _position_set(self, pos):
        pos = int(pos[0]), int(pos[1])
        self.__SetCursorPos(*pos)
        self._emit('on_move', *pos)

    def _scroll(self, dx, dy):
        if dy:
            SendInput(
                1,
                ctypes.byref(INPUT(
                    type=INPUT.MOUSE,
                    value=INPUT_union(
                        mi=MOUSEINPUT(
                            dwFlags=MOUSEINPUT.WHEEL,
                            mouseData=int(dy))))),
                ctypes.sizeof(INPUT))

        if dx:
            SendInput(
                1,
                ctypes.byref(INPUT(
                    type=INPUT.MOUSE,
                    value=INPUT_union(
                        mi=MOUSEINPUT(
                            dwFlags=MOUSEINPUT.HWHEEL,
                            mouseData=int(dx))))),
                ctypes.sizeof(INPUT))

        if dx or dy:
            px, py = self._position_get()
            self._emit('on_scroll', px, py, dx, dy)

    def _press(self, button):
        SendInput(
            1,
            ctypes.byref(INPUT(
                type=INPUT.MOUSE,
                value=INPUT_union(
                    mi=MOUSEINPUT(
                        dwFlags=button.value[1])))),
            ctypes.sizeof(INPUT))

    def _release(self, button):
        SendInput(
            1,
            ctypes.byref(INPUT(
                type=INPUT.MOUSE,
                value=INPUT_union(
                    mi=MOUSEINPUT(
                        dwFlags=button.value[0])))),
            ctypes.sizeof(INPUT))


@Controller._receiver
class Listener(ListenerMixin, _base.Listener):
    #: The Windows hook ID for low level mouse events, ``WH_MOUSE_LL``
    _EVENTS = 14

    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_MBUTTONDOWN = 0x0207
    WM_MBUTTONUP = 0x0208
    WM_MOUSEMOVE = 0x0200
    WM_MOUSEWHEEL = 0x020A
    WM_MOUSEHWHEEL = 0x020E
    WM_RBUTTONDOWN = 0x0204
    WM_RBUTTONUP = 0x0205

    _WHEEL_DELTA = 120

    #: A mapping from messages to button events
    CLICK_BUTTONS = {
        WM_LBUTTONDOWN: (Button.left, True),
        WM_LBUTTONUP: (Button.left, False),
        WM_MBUTTONDOWN: (Button.middle, True),
        WM_MBUTTONUP: (Button.middle, False),
        WM_RBUTTONDOWN: (Button.right, True),
        WM_RBUTTONUP: (Button.right, False)}

    #: A mapping from messages to scroll vectors
    SCROLL_BUTTONS = {
        WM_MOUSEWHEEL: (0, 1),
        WM_MOUSEHWHEEL: (1, 0)}

    _HANDLED_EXCEPTIONS = (
        SystemHook.SuppressException,)

    class _MSLLHOOKSTRUCT(ctypes.Structure):
        """Contains information about a mouse event passed to a ``WH_MOUSE_LL``
        hook procedure, ``MouseProc``.
        """
        _fields_ = [
            ('pt', wintypes.POINT),
            ('mouseData', wintypes.DWORD),
            ('flags', wintypes.DWORD),
            ('time', wintypes.DWORD),
            ('dwExtraInfo', ctypes.c_void_p)]

    #: A pointer to a :class:`_MSLLHOOKSTRUCT`
    _LPMSLLHOOKSTRUCT = ctypes.POINTER(_MSLLHOOKSTRUCT)

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._event_filter = self._options.get(
            'event_filter',
            lambda msg, data: True)

    def _handle(self, code, msg, lpdata):
        if code != SystemHook.HC_ACTION:
            return

        data = ctypes.cast(lpdata, self._LPMSLLHOOKSTRUCT).contents

        # Suppress further propagation of the event if it is filtered
        if self._event_filter(msg, data) is False:
            return

        if msg == self.WM_MOUSEMOVE:
            self.on_move(data.pt.x, data.pt.y)

        elif msg in self.CLICK_BUTTONS:
            button, pressed = self.CLICK_BUTTONS[msg]
            self.on_click(data.pt.x, data.pt.y, button, pressed)

        elif msg in self.SCROLL_BUTTONS:
            mx, my = self.SCROLL_BUTTONS[msg]
            dd = wintypes.SHORT(data.mouseData >> 16).value // self._WHEEL_DELTA
            self.on_scroll(data.pt.x, data.pt.y, dd * mx, dd * my)
