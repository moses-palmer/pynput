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
Utility functions and classes for the *uinput* backend.
"""

# pylint: disable=R0903
# We implement stubs


# Check that we have permissions to continue
def _check():
    # TODO: Implement!
    pass
_check()
del _check


class ListenerMixin(object):
    """A mixin for *uinput* event listeners.

    Subclasses should set a value for :attr:`_EVENTS` and implement
    :meth:`_handle`.
    """
    #: The events for which to listen
    _EVENTS = tuple()

    def _run(self):
        # TODO: Implement!
        raise NotImplementedError()

    def _stop_platform(self):
        # TODO: Implement!
        raise NotImplementedError()
