# coding=utf-8
# pynput
# Copyright (C) 2015-2024 Moses Palmér
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
The mouse implementation for *libei*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import enum

from pynput._util.libei import ListenerMixin, session
from . import _base


# pylint: disable=C0103
#: The various buttons.
#:
#: The values are the kernel ``BTN_*`` codes, which *libei* takes directly.
#: They are spelled out rather than read from ``evdev.ecodes`` because they
#: are a stable kernel *ABI*, and because this backend exists for the case
#: where the *evdev* device cannot be opened at all.
#:
#: There is no equivalent of the *Xorg* backend's ``scroll_up`` and friends:
#: under *X* a scroll is a button press, whereas *libei* has scroll events of
#: its own, which is what :meth:`Controller.scroll` uses.
Button = enum.Enum(
    'Button',
    module=__name__,
    names=[
        ('unknown', None),
        ('left', 0x110),
        ('right', 0x111),
        ('middle', 0x112),
        ('side', 0x113),
        ('extra', 0x114),
        ('forward', 0x115),
        ('back', 0x116),
        ('task', 0x117),
    ],
)
# pylint: enable=C0103


class Controller(_base.Controller):
    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self._session = session()
        self._position = None

    def _position_get(self):
        # Nothing in this protocol can read the pointer position: the portal
        # grants the right to inject input, not to observe it, and the
        # alternative source, a screen cast stream carrying cursor metadata,
        # would mean asking the user for permission to see the screen.
        #
        # What this controller set itself is remembered, so that code which
        # sets a position and reads it back gets the right answer, and so that
        # move() works. Anything else is a guess, and a plausible but wrong
        # coordinate is worse than a refusal to answer.
        if self._position is None:
            raise NotImplementedError(
                'the libei backend cannot read the pointer position; it is '
                'known only once this controller has set it')
        return self._position

    def _position_set(self, pos):
        x, y = self._check(pos)
        bounds = self._session.bounds
        if bounds is not None:
            left, top, width, height = bounds
            # Rejected rather than clamped, because the most likely reason for
            # an out of bounds coordinate is that the caller measured the
            # screen in device pixels: these are logical pixels, which on a
            # display scaled by 1.25 are 80% as many. Clamping would move the
            # pointer to the edge and look like a rounding error
            if not (left <= x < left + width and top <= y < top + height):
                raise ValueError(pos)
        self._session.pointer_motion_absolute(x, y)
        self._position = (x, y)

    def _scroll(self, dx, dy):
        dx, dy = self._check((dx, dy))
        # The sign is the kernel's below this point, where positive is down,
        # and pynput's above it, where positive is up
        self._session.scroll_discrete(dx, -dy)

    def _press(self, button):
        self._session.button(button.value, True)

    def _release(self, button):
        self._session.button(button.value, False)

    def move(self, dx, dy):
        # Overridden because the base implementation offsets the position it
        # reads back, which this backend cannot do. libei has a relative
        # pointer device of its own, which needs no starting point.
        dx, dy = self._check((dx, dy))
        self._session.pointer_motion(dx, dy)
        if self._position is not None:
            self._position = (self._position[0] + dx, self._position[1] + dy)

    @staticmethod
    def _check(value):
        """Validates a coordinate pair.

        :param value: The pair.

        :return: the pair, as a tuple of ``int``

        :raises ValueError: if either value is not a number
        """
        try:
            x, y = value
            return int(x), int(y)
        except (TypeError, ValueError):
            raise ValueError(value)


class Listener(ListenerMixin, _base.Listener):
    pass
