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
Utility functions and classes for the *uinput* backend.
"""

# pylint: disable=R0903
# We implement stubs

import evdev


# Check that we have permissions to continue
def _check():
    # TODO: Implement!
    pass
_check()
del _check


class ListenerMixin(object):
    """A mixin for *uinput* event listeners.

    Subclasses should set a value for :attr:`_EVENTS` and implement
    :meth:`_handle_message`.
    """
    #: The events for which to listen
    _EVENTS = tuple()

    def __init__(self, *args, **kwargs):
        super(ListenerMixin, self).__init__(*args, **kwargs)
        self._dev = self._device(self._options.get(
            'device_paths',
            evdev.list_devices()))
        if self.suppress:
            self._dev.grab()

    def _run(self):
        for event in self._dev.read_loop():
            if event.type in self._EVENTS:
                self._handle_message(event)

    def _stop_platform(self):
        self._dev.close()

    def _device(self, paths):
        """Attempts to load a readable keyboard device.

        :param paths: A list of paths.

        :return: a compatible device
        """
        dev, count = None, 0
        for path in paths:
            # Open the device
            try:
                next_dev = evdev.InputDevice(path)
            except OSError:
                continue

            # Does this device provide more handled event codes?
            capabilities = next_dev.capabilities()
            next_count = sum(
                len(codes)
                for event, codes in capabilities.items()
                if event in self._EVENTS)
            if next_count > count:
                dev = next_dev
                count = next_count
            else:
                next_dev.close()

        if dev is None:
            raise OSError('no keyboard device available')
        else:
            return dev

    def _handle_message(self, event):
        """Handles a single event.

        This method should call one of the registered event callbacks.

        :param event: The event.
        """
        raise NotImplementedError()
