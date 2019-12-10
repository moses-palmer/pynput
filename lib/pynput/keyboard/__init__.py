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
The module containing keyboard classes.

See the documentation for more information.
"""

# pylint: disable=C0103
# KeyCode, Key, Controller and Listener are not constants

import os
import sys

if os.environ.get('__PYNPUT_GENERATE_DOCUMENTATION') == 'yes':
    from ._base import KeyCode, Key, Controller, Listener
else:
    KeyCode = None
    Key = None
    Controller = None
    Listener = None

from pynput._util import Events


if sys.platform == 'darwin':
    if not KeyCode and not Key and not Controller and not Listener:
        from ._darwin import KeyCode, Key, Controller, Listener

elif sys.platform == 'win32':
    if not KeyCode and not Key and not Controller and not Listener:
        from ._win32 import KeyCode, Key, Controller, Listener

else:
    if not KeyCode and not Key and not Controller and not Listener:
        try:
            from ._xorg import KeyCode, Key, Controller, Listener
        except ImportError:
            # For now, since we only support Xlib anyway, we re-raise these
            # errors to allow users to determine the cause of failures to import
            raise


if not KeyCode or not Key or not Controller or not Listener:
    raise ImportError('this platform is not supported')


class Events(Events):
    """A keyboard event listener supporting synchronous iteration over the
    events.

    Possible events are:

    :class:`Events.Press`
        A key was pressed.

    :class:`Events.Release`
        A key was releesed.
    """
    _Listener = Listener

    class Press(Events.Event):
        """A key press event.
        """
        def __init__(self, key):
            #: The key.
            self.key = key

    class Release(Events.Event):
        """A key release event.
        """
        def __init__(self, key):
            #: The key.
            self.key = key

    def __init__(self):
        super(Events, self).__init__(
            on_press=self.Press,
            on_release=self.Release)
