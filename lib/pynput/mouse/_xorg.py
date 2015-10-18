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
import Xlib.display
import Xlib.ext
import Xlib.ext.xtest
import Xlib.X
import Xlib.protocol

from pynput._util.xorg import *
from . import _base


# Create a display to verify that we have an X connection
display = Xlib.display.Display()
display.close()
del display


class Controller(_base.Controller):
    class Button(enum.Enum):
        """The various buttons.
        """
        left = 1
        middle = 2
        right = 3
        scroll_up = 4
        scroll_down = 5
        scroll_left = 6
        scroll_right = 7

    def __init__(self):
        self._display = Xlib.display.Display()

    def _position_get(self):
        with display_manager(self._display) as d:
            data = d.screen().root.query_pointer()._data
            return (data["root_x"], data["root_y"])

    def _position_set(self, pos):
        x, y = pos
        with display_manager(self._display) as d:
            Xlib.ext.xtest.fake_input(d, Xlib.X.MotionNotify, x=x, y=y)

    def _scroll(self, dx, dy):
        if dy:
            self.click(
                button=self.Button.scroll_up if dy > 0
                else self.Button.scroll_down,
                count=abs(dy))

        if dx:
            self.click(
                button=self.Button.scroll_right if dx > 0
                else self.Button.scroll_left,
                count=abs(dx))

    def _press(self, button):
        with display_manager(self._display) as d:
            Xlib.ext.xtest.fake_input(d, Xlib.X.ButtonPress, button.value)

    def _release(self, button):
        with display_manager(self._display) as d:
            Xlib.ext.xtest.fake_input(d, Xlib.X.ButtonRelease, button.value)


class Listener(_base.Listener):
    #: A mapping from button values to scroll directions
    SCROLL_BUTTONS = {
        Controller.Button.scroll_up.value: (0, 1),
        Controller.Button.scroll_down.value: (0, -1),
        Controller.Button.scroll_right.value: (1, 0),
        Controller.Button.scroll_left.value: (-1, 0)}

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._display_stop = Xlib.display.Display()
        self._display_record = Xlib.display.Display()
        with display_manager(self._display_record) as d:
            self._context = d.record_create_context(
                0,
                [Xlib.ext.record.AllClients],
                [{
                        'core_requests': (0, 0),
                        'core_replies': (0, 0),
                        'ext_requests': (0, 0, 0, 0),
                        'ext_replies': (0, 0, 0, 0),
                        'delivered_events': (0, 0),
                        'device_events': (
                            Xlib.X.ButtonPressMask,
                            Xlib.X.ButtonReleaseMask),
                        'errors': (0, 0),
                        'client_started': False,
                        'client_died': False}])

    def _run(self):
        with display_manager(self._display_record) as d:
            d.record_enable_context(
                self._context, self._handler)
            d.record_free_context(self._context)

    def _stop(self):
        self._display_stop.sync()
        with display_manager(self._display_stop) as d:
            d.record_disable_context(self._context)

    @_base.Listener._emitter
    def _handler(self, events):
        """The callback registered with *X* for mouse events.

        This method will parse the response and call the callbacks registered
        on initialisation.
        """
        # We use this instance for parsing the binary data
        e = Xlib.protocol.rq.EventField(None)

        data = events.data

        while len(data):
            event, data = e.parse_binary_value(
                data, self._display_record.display, None, None)

            x = event.root_x
            y = event.root_y

            if event.type == Xlib.X.ButtonPress:
                # Scroll events are sent as button presses with the scroll
                # button codes
                scroll = self.SCROLL_BUTTONS.get(event.detail, None)
                if scroll:
                    self.on_scroll(x, y, *scroll)
                else:
                    self.on_click(x, y, Controller.Button(event.detail), True)

            elif event.type == Xlib.X.ButtonRelease:
                # Send an event only if this was not a scroll event
                if event.detail not in self.SCROLL_BUTTONS:
                    self.on_click(x, y, Controller.Button(event.detail), False)

            else:
                self.on_move(x, y)
