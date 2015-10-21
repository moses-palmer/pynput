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


class Controller(_base.Controller):
    class Button(enum.Enum):
        """The various buttons.
        """
        left = (MOUSEINPUT.LEFTUP, MOUSEINPUT.LEFTDOWN)
        middle = (MOUSEINPUT.MIDDLEUP, MOUSEINPUT.MIDDLEDOWN)
        right = (MOUSEINPUT.RIGHTUP, MOUSEINPUT.RIGHTDOWN)

    __GetCursorPos = windll.user32.GetCursorPos
    __SetCursorPos = windll.user32.SetCursorPos

    def _position_get(self):
        point = wintypes.POINT()
        if self.__GetCursorPos(ctypes.byref(point)):
            return (point.x, point.y)
        else:
            return None

    def _position_set(self, pos):
        self.__SetCursorPos(*pos)
        self._notify('on_move', *pos)

    def _scroll(self, dx, dy):
        if dy:
            SendInput(
                1,
                ctypes.byref(INPUT(
                    type=INPUT.MOUSE,
                    value=INPUT_union(
                        mouse=MOUSEINPUT(
                            dwFlags=MOUSEINPUT.WHEEL,
                            mouseData=dy)))),
                ctypes.sizeof(INPUT))

        if dx:
            SendInput(
                1,
                ctypes.byref(INPUT(
                    type=INPUT.MOUSE,
                    value=INPUT_union(
                        mouse=MOUSEINPUT(
                            dwFlags=MOUSEINPUT.HWHEEL,
                            mouseData=dy)))),
                ctypes.sizeof(INPUT))

        if dx or dy:
            self._notify('on_scroll', dx, dy)

    def _press(self, button):
        SendInput(
            1,
            ctypes.byref(INPUT(
                type=INPUT.MOUSE,
                value=INPUT_union(
                    mouse=MOUSEINPUT(
                        dwFlags=button.value[0])))),
            ctypes.sizeof(INPUT))
        x, y = self.position
        self._notify('on_click', x, y, button, True)

    def _release(self, button):
        SendInput(
            1,
            ctypes.byref(INPUT(
                type=INPUT.MOUSE,
                value=INPUT_union(
                    mouse=MOUSEINPUT(
                        dwFlags=button.value[1])))),
            ctypes.sizeof(INPUT))
        x, y = self.position
        self._notify('on_click', x, y, button, False)

    def _notify(self, action, *args):
        """Sends a notification to all currently running instances of
        :class:`Listener`.

        This method will ensure that listeners that raise
        :class:`StopException` are stopped.

        :param str action: The name of the notification.

        :param args: The arguments to pass.
        """
        stopped = []
        for listener in Listener.listeners():
            try:
                getattr(listener, action)(*args)
            except Listener.StopException:
                stopped.append(listener)
        for listener in stopped:
            listener.stop()


class Listener(_base.Listener):
    #: The Windows hook ID for low level mouse events
    WH_MOUSE_LL = 14

    HC_ACTION = 0
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_MOUSEMOVE = 0x0200
    WM_MOUSEWHEEL = 0x020A
    WM_MOUSEHWHEEL = 0x020E
    WM_RBUTTONDOWN = 0x0204
    WM_RBUTTONUP = 0x0205

    WHEEL_DELTA = 120

    #: A mapping from messages to button events
    CLICK_BUTTONS = {
        WM_LBUTTONDOWN: (Controller.Button.left, True),
        WM_LBUTTONUP: (Controller.Button.left, False),
        WM_RBUTTONDOWN: (Controller.Button.right, True),
        WM_RBUTTONUP: (Controller.Button.right, False)}

    #: A mapping from messages to scroll vectors
    SCROLL_BUTTONS = {
        WM_MOUSEWHEEL: (0, 1),
        WM_MOUSEHWHEEL: (1, 0)}

    #: The currently running listeners
    __listeners = set()

    #: The lock protecting access to the :attr:`_listeners`
    __listener_lock = threading.Lock()

    class MSLLHOOKSTRUCT(ctypes.Structure):
        """Contains information about a mouse event passed to a ``WH_MOUSE_LL``
        hook procedure, ``MouseProc``.
        """
        _fields_ = [
            ('pt', wintypes.POINT),
            ('mouseData', wintypes.DWORD),
            ('flags', wintypes.DWORD),
            ('time', wintypes.DWORD),
            ('dwExtraInfo', ctypes.c_void_p)]

    #: A pointer to a :class:`MSLLHOOKSTRUCT`
    LPMSLLHOOKSTRUCT = ctypes.POINTER(MSLLHOOKSTRUCT)

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)

        self._message_loop = MessageLoop()

    def _run(self):
        self.__add_listener(self)
        try:
            self._message_loop.start()

            with SystemHook(self.WH_MOUSE_LL, self._handler):
                # Just pump messages
                for msg in self._message_loop:
                    if not self.running:
                        break

        finally:
            self.__remove_listener(self)

    def _stop(self):
        self._message_loop.stop()

    @_base.Listener._emitter
    def _handler(self, code, msg, lpdata):
        """The callback registered with *Windows* for mouse events.

        This method will call the callbacks registered on initialisation.
        """
        if code != self.HC_ACTION:
            return

        data = ctypes.cast(lpdata, self.LPMSLLHOOKSTRUCT).contents

        if msg == self.WM_MOUSEMOVE:
            self.on_move(data.pt.x, data.pt.y)

        elif msg in self.CLICK_BUTTONS:
            button, pressed = self.CLICK_BUTTONS[msg]
            self.on_click(data.pt.x, data.pt.y, button, pressed)

        elif msg in self.SCROLL_BUTTONS:
            mx, my = self.SCROLL_BUTTONS[msg]
            d = wintypes.SHORT(data.mouseData >> 16).value // self.WHEEL_DELTA
            self.on_scroll(data.pt.x, data.pt.y, d * mx, d * my)

    @classmethod
    def __add_listener(self, listener):
        """Adds a listener to the set of running listeners.

        :param Listener listener: The listener to add.
        """
        with self.__listener_lock:
            self.__listeners.add(listener)

    @classmethod
    def __remove_listener(self, listener):
        """Removes a listener from the set of running listeners.

        :param Listener listener: The listener to remove.
        """
        with self.__listener_lock:
            self.__listeners.remove(listener)

    @classmethod
    def listeners(self):
        """Iterates over the set of running listeners.

        This method will quit without acquiring the lock if the set is empty,
        so there is potential for race conditions. This is an optimisation,
        since :class:`Controller` will need to call this method for every
        control event.
        """
        if not self.__listeners:
            return
        with self.__listener_lock:
            for listener in self.__listeners:
                yield listener
