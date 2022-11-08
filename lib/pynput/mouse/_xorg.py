# coding=utf-8
# pynput
# Copyright (C) 2015-2022 Moses Palmér
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
The keyboard implementation for *Xorg*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes


# pylint: disable=E1101,E1102
# We dynamically generate the Button class

# pylint: disable=R0903
# We implement stubs

# pylint: disable=W0611
try:
    import pynput._util.xorg
except Exception as e:
    raise ImportError('failed to acquire X connection: {}'.format(str(e)), e)
# pylint: enable=W0611

import enum
import Xlib.display
import Xlib.ext
import Xlib.ext.xtest
import Xlib.X
import Xlib.protocol

from pynput._util.xorg import (
    display_manager,
    ListenerMixin)
from . import _base


# pylint: disable=C0103
Button = enum.Enum(
    'Button',
    module=__name__,
    names=[
        ('unknown', None),
        ('left', 1),
        ('middle', 2),
        ('right', 3),
        ('scroll_up', 4),
        ('scroll_down', 5),
        ('scroll_left', 6),
        ('scroll_right', 7)] + [
            ('button%d' % i, i)
            for i in range(8, 31)])
# pylint: enable=C0103


class Controller(_base.Controller):
    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self._display = Xlib.display.Display()

    def __del__(self):
        if hasattr(self, '_display'):
            self._display.close()

    def _position_get(self):
        with display_manager(self._display) as dm:
            qp = dm.screen().root.query_pointer()
            return (qp.root_x, qp.root_y)

    def _position_set(self, pos):
        px, py = self._check_bounds(*pos)
        with display_manager(self._display) as dm:
            Xlib.ext.xtest.fake_input(dm, Xlib.X.MotionNotify, x=px, y=py)

    def _scroll(self, dx, dy):
        dx, dy = self._check_bounds(dx, dy)
        if dy:
            self.click(
                button=Button.scroll_up if dy > 0 else Button.scroll_down,
                count=abs(dy))

        if dx:
            self.click(
                button=Button.scroll_right if dx > 0 else Button.scroll_left,
                count=abs(dx))

    def _press(self, button):
        with display_manager(self._display) as dm:
            Xlib.ext.xtest.fake_input(dm, Xlib.X.ButtonPress, button.value)

    def _release(self, button):
        with display_manager(self._display) as dm:
            Xlib.ext.xtest.fake_input(dm, Xlib.X.ButtonRelease, button.value)

    def _check_bounds(self, *args):
        """Checks the arguments and makes sure they are within the bounds of a
        short integer.

        :param args: The values to verify.
        """
        if not all(
                (-0x7fff - 1) <= number <= 0x7fff
                for number in args):
            raise ValueError(args)
        else:
            return tuple(int(p) for p in args)


class Listener(ListenerMixin, _base.Listener):
    #: A mapping from button values to scroll directions
    _SCROLL_BUTTONS = {
        Button.scroll_up.value: (0, 1),
        Button.scroll_down.value: (0, -1),
        Button.scroll_right.value: (1, 0),
        Button.scroll_left.value: (-1, 0)}

    _EVENTS = (
        Xlib.X.ButtonPressMask,
        Xlib.X.ButtonReleaseMask)

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)

    def _handle(self, dummy_display, event, injected):
        px = event.root_x
        py = event.root_y

        if event.type == Xlib.X.ButtonPress:
            # Scroll events are sent as button presses with the scroll
            # button codes
            scroll = self._SCROLL_BUTTONS.get(event.detail, None)
            if scroll:
                self.on_scroll(
                    px, py, scroll[0], scroll[1], injected)
            else:
                self.on_click(
                    px, py, self._button(event.detail), True, injected)

        elif event.type == Xlib.X.ButtonRelease:
            # Send an event only if this was not a scroll event
            if event.detail not in self._SCROLL_BUTTONS:
                self.on_click(
                    px, py, self._button(event.detail), False, injected)

        else:
            self.on_move(px, py, injected)


    def _suppress_start(self, display):
        display.screen().root.grab_pointer(
            True, self._event_mask, Xlib.X.GrabModeAsync, Xlib.X.GrabModeAsync,
            0, 0, Xlib.X.CurrentTime)

    def _suppress_stop(self, display):
        display.ungrab_pointer(Xlib.X.CurrentTime)

    # pylint: disable=R0201
    def _button(self, detail):
        """Creates a mouse button from an event detail.

        If the button is unknown, :attr:`Button.unknown` is returned.

        :param detail: The event detail.

        :return: a button
        """
        try:
            return Button(detail)
        except ValueError:
            return Button.unknown
    # pylint: enable=R0201
