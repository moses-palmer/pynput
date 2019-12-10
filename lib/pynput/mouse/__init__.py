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
The module containing mouse classes.

See the documentation for more information.
"""

# pylint: disable=C0103
# Button, Controller and Listener are not constants

import os
import sys

if os.environ.get('__PYNPUT_GENERATE_DOCUMENTATION') == 'yes':
    from ._base import Button, Controller, Listener
else:
    Button = None
    Controller = None
    Listener = None

from pynput._util import Events


if sys.platform == 'darwin':
    if not Button and not Controller and not Listener:
        from ._darwin import Button, Controller, Listener

elif sys.platform == 'win32':
    if not Button and not Controller and not Listener:
        from ._win32 import Button, Controller, Listener

else:
    if not Button and not Controller and not Listener:
        try:
            from ._xorg import Button, Controller, Listener
        except ImportError:
            # For now, since we only support Xlib anyway, we re-raise these
            # errors to allow users to determine the cause of failures to import
            raise


if not Button or not Controller or not Listener:
    raise ImportError('this platform is not supported')


class Events(Events):
    """A mouse event listener supporting synchronous iteration over the events.

    Possible events are:

    :class:`Events.Move`
        The mouse was moved.

    :class:`Events.Click`
        A mouse button was pressed or released.

    :class:`Events.Scroll`
        The device was scrolled.
    """
    _Listener = Listener

    class Move(Events.Event):
        """A move event.
        """
        def __init__(self, x, y):
            #: The X screen coordinate.
            self.x = x

            #: The Y screen coordinate.
            self.y = y

    class Click(Events.Event):
        """A click event.
        """
        def __init__(self, x, y, button, pressed):
            #: The X screen coordinate.
            self.x = x

            #: The Y screen coordinate.
            self.y = y

            #: The button.
            self.button = button

            #: Whether the button was pressed.
            self.pressed = pressed

    class Scroll(Events.Event):
        """A scoll event.
        """
        def __init__(self, x, y, dx, dy):
            #: The X screen coordinate.
            self.x = x

            #: The Y screen coordinate.
            self.y = y

            #: The number of horisontal steps.
            self.dx = dx

            #: The number of vertical steps.
            self.dy = dy

    def __init__(self):
        super(Events, self).__init__(
            on_move=self.Move,
            on_click=self.Click,
            on_scroll=self.Scroll)
