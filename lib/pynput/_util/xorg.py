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
Utility functions and classes for the *Xorg* backend.
"""

# pylint: disable=R0903
# We implement stubs

import contextlib
import functools
import itertools
import operator
import Xlib.display
import Xlib.threaded
import Xlib.XK

from . import AbstractListener
from .xorg_keysyms import SYMBOLS


# Create a display to verify that we have an X connection
def _check():
    display = Xlib.display.Display()
    display.close()
_check()
del _check


class X11Error(Exception):
    """An error that is thrown at the end of a code block managed by a
    :func:`display_manager` if an *X11* error occurred.
    """
    pass


@contextlib.contextmanager
def display_manager(display):
    """Traps *X* errors and raises an :class:``X11Error`` at the end if any
    error occurred.

    This handler also ensures that the :class:`Xlib.display.Display` being
    managed is sync'd.

    :param Xlib.display.Display display: The *X* display.

    :return: the display
    :rtype: Xlib.display.Display
    """
    errors = []

    def handler(*args):
        """The *Xlib* error handler.
        """
        errors.append(args)

    old_handler = display.set_error_handler(handler)
    try:
        yield display
        display.sync()
    finally:
        display.set_error_handler(old_handler)
    if errors:
        raise X11Error(errors)


def _find_mask(display, symbol):
    """Returns the mode flags to use for a modifier symbol.

    :param Xlib.display.Display display: The *X* display.

    :param str symbol: The name of the symbol.

    :return: the modifier mask
    """
    # Get the key code for the symbol
    modifier_keycode = display.keysym_to_keycode(
        Xlib.XK.string_to_keysym(symbol))

    for index, keycodes in enumerate(display.get_modifier_mapping()):
        for keycode in keycodes:
            if keycode == modifier_keycode:
                return 1 << index

    return 0


def alt_mask(display):
    """Returns the *alt* mask flags.

    The first time this function is called for a display, the value is cached.
    Subsequent calls will return the cached value.

    :param Xlib.display.Display display: The *X* display.

    :return: the modifier mask
    """
    if not hasattr(display, '__alt_mask'):
        display.__alt_mask = _find_mask(display, 'Alt_L')
    return display.__alt_mask


def alt_gr_mask(display):
    """Returns the *alt* mask flags.

    The first time this function is called for a display, the value is cached.
    Subsequent calls will return the cached value.

    :param Xlib.display.Display display: The *X* display.

    :return: the modifier mask
    """
    if not hasattr(display, '__altgr_mask'):
        display.__altgr_mask = _find_mask(display, 'Mode_switch')
    return display.__altgr_mask


def numlock_mask(display):
    """Returns the *numlock* mask flags.

    The first time this function is called for a display, the value is cached.
    Subsequent calls will return the cached value.

    :param Xlib.display.Display display: The *X* display.

    :return: the modifier mask
    """
    if not hasattr(display, '__numlock_mask'):
        display.__numlock_mask = _find_mask(display, 'Num_Lock')
    return display.__numlock_mask


def keysym_is_latin_upper(keysym):
    """Determines whether a *keysym* is an upper case *latin* character.

    This is true only if ``XK_A`` <= ``keysym`` <= ` XK_Z``.

    :param in keysym: The *keysym* to check.
    """
    return Xlib.XK.XK_A <= keysym <= Xlib.XK.XK_Z


def keysym_is_latin_lower(keysym):
    """Determines whether a *keysym* is a lower case *latin* character.

    This is true only if ``XK_a`` <= ``keysym`` <= ` XK_z``.

    :param in keysym: The *keysym* to check.
    """
    return Xlib.XK.XK_a <= keysym <= Xlib.XK.XK_z


def keysym_group(ks1, ks2):
    """Generates a group from two *keysyms*.

    The implementation of this function comes from:

        Within each group, if the second element of the group is ``NoSymbol``,
        then the group should be treated as if the second element were the same
        as the first element, except when the first element is an alphabetic
        *KeySym* ``K`` for which both lowercase and uppercase forms are
        defined.

        In that case, the group should be treated as if the first element were
        the lowercase form of ``K`` and the second element were the uppercase
        form of ``K``.

    This function assumes that *alphabetic* means *latin*; this assumption
    appears to be consistent with observations of the return values from
    ``XGetKeyboardMapping``.

    :param ks1: The first *keysym*.

    :param ks2: The second *keysym*.

    :return: a tuple conforming to the description above
    """
    if ks2 == Xlib.XK.NoSymbol:
        if keysym_is_latin_upper(ks1):
            return (Xlib.XK.XK_a + ks1 - Xlib.XK.XK_A, ks1)
        elif keysym_is_latin_lower(ks1):
            return (ks1, Xlib.XK.XK_A + ks1 - Xlib.XK.XK_a)
        else:
            return (ks1, ks1)
    else:
        return (ks1, ks2)


def keysym_normalize(keysym):
    """Normalises a list of *keysyms*.

    The implementation of this function comes from:

        If the list (ignoring trailing ``NoSymbol`` entries) is a single
        *KeySym* ``K``, then the list is treated as if it were the list
        ``K NoSymbol K NoSymbol``.

        If the list (ignoring trailing ``NoSymbol`` entries) is a pair of
        *KeySyms* ``K1 K2``, then the list is treated as if it were the list
        ``K1 K2 K1 K2``.

        If the list (ignoring trailing ``NoSymbol`` entries) is a triple of
        *KeySyms* ``K1 K2 K3``, then the list is treated as if it were the list
        ``K1 K2 K3 NoSymbol``.

    This function will also group the *keysyms* using :func:`keysym_group`.

    :param keysyms: A list of keysyms.

    :return: the tuple ``(group_1, group_2)`` or ``None``
    """
    # Remove trailing NoSymbol
    stripped = list(reversed(list(
        itertools.dropwhile(
            lambda n: n == Xlib.XK.NoSymbol,
            reversed(keysym)))))

    if not stripped:
        return

    elif len(stripped) == 1:
        return (
            keysym_group(stripped[0], Xlib.XK.NoSymbol),
            keysym_group(stripped[0], Xlib.XK.NoSymbol))

    elif len(stripped) == 2:
        return (
            keysym_group(stripped[0], stripped[1]),
            keysym_group(stripped[0], stripped[1]))

    elif len(stripped) == 3:
        return (
            keysym_group(stripped[0], stripped[1]),
            keysym_group(stripped[2], Xlib.XK.NoSymbol))

    elif len(stripped) >= 6:
        # TODO: Find out why this is necessary; using only the documented
        # behaviour may lead to only a US layout being used?
        return (
            keysym_group(stripped[0], stripped[1]),
            keysym_group(stripped[4], stripped[5]))

    else:
        return (
            keysym_group(stripped[0], stripped[1]),
            keysym_group(stripped[2], stripped[3]))


def index_to_shift(display, index):
    """Converts an index in a *key code* list to the corresponding shift state.

    :param Xlib.display.Display display: The display for which to retrieve the
        shift mask.

    :param int index: The keyboard mapping *key code* index.

    :return: a shift mask
    """
    return (
        (1 << 0 if index & 1 else 0) |
        (alt_gr_mask(display) if index & 2 else 0))


def shift_to_index(display, shift):
    """Converts an index in a *key code* list to the corresponding shift state.

    :param Xlib.display.Display display: The display for which to retrieve the
        shift mask.

    :param int index: The keyboard mapping *key code* index.

    :retur: a shift mask
    """
    return (
        (1 if shift & 1 else 0) +
        (2 if shift & alt_gr_mask(display) else 0))


def keyboard_mapping(display):
    """Generates a mapping from *keysyms* to *key codes* and required
    modifier shift states.

    :param Xlib.display.Display display: The display for which to retrieve the
        keyboard mapping.

    :return: the keyboard mapping
    """
    mapping = {}

    shift_mask = 1 << 0
    group_mask = alt_gr_mask(display)

    # Iterate over all keysym lists in the keyboard mapping
    min_keycode = display.display.info.min_keycode
    keycode_count = display.display.info.max_keycode - min_keycode + 1
    for index, keysyms in enumerate(display.get_keyboard_mapping(
            min_keycode, keycode_count)):
        key_code = index + min_keycode

        # Normalise the keysym list to yield a tuple containing the two groups
        normalized = keysym_normalize(keysyms)
        if not normalized:
            continue

        # Iterate over the groups to extract the shift and modifier state
        for groups, group in zip(normalized, (False, True)):
            for keysym, shift in zip(groups, (False, True)):
                if not keysym:
                    continue
                shift_state = 0 \
                    | (shift_mask if shift else 0) \
                    | (group_mask if group else 0)

                # Prefer already known lesser shift states
                if keysym in mapping and mapping[keysym][1] < shift_state:
                    continue
                mapping[keysym] = (key_code, shift_state)

    return mapping


def char_to_keysym(char):
    """Converts a unicode character to a *keysym*.

    :param str char: The unicode character.

    :return: the corresponding *keysym*, or ``0`` if it cannot be found
    """
    ordinal = ord(char)
    if ordinal < 0x100:
        return ordinal
    else:
        return ordinal | 0x01000000


def symbol_to_keysym(symbol):
    """Converts a symbol name to a *keysym*.

    :param str symbol: The name of the symbol.

    :return: the corresponding *keysym*, or ``0`` if it cannot be found
    """
    # First try simple translation, and if that fails, try checking a module
    # attribute of Xlib.keysymdef.xkb
    keysym = Xlib.XK.string_to_keysym(symbol)
    if keysym:
        return keysym
    else:
        try:
            return getattr(Xlib.keysymdef.xkb, 'XK_' + symbol, 0)
        except AttributeError:
            return SYMBOLS.get(symbol, (0,))[0]


class ListenerMixin(object):
    """A mixin for *X* event listeners.

    Subclasses should set a value for :attr:`_EVENTS` and implement
    :meth:`_handle`.
    """
    #: The events for which to listen
    _EVENTS = tuple()

    #: We use this instance for parsing the binary data
    _EVENT_PARSER = Xlib.protocol.rq.EventField(None)

    def _run(self):
        self._display_stop = Xlib.display.Display()
        self._display_record = Xlib.display.Display()
        with display_manager(self._display_stop) as dm:
            self._context = dm.record_create_context(
                0,
                [Xlib.ext.record.AllClients],
                [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': self._EVENTS,
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False}])

        # pylint: disable=W0702; we want to silence errors
        try:
            self._initialize(self._display_stop)
            self._mark_ready()
            if self.suppress:
                with display_manager(self._display_record) as dm:
                    self._suppress_start(dm)
            self._display_record.record_enable_context(
                self._context, self._handler)
        except:
            # This exception will have been passed to the main thread
            pass
        finally:
            if self.suppress:
                with display_manager(self._display_stop) as dm:
                    self._suppress_stop(dm)
            self._display_record.record_free_context(self._context)
            self._display_stop.close()
            self._display_record.close()
        # pylint: enable=W0702

    def _stop_platform(self):
        if not hasattr(self, '_context'):
            self.wait()
        # pylint: disable=W0702; we must ignore errors
        try:
            with display_manager(self._display_stop) as dm:
                dm.record_disable_context(self._context)
        except:
            pass
        # pylint: enable=W0702

    def _suppress_start(self, display):
        """Starts suppressing events.

        :param Xlib.display.Display display: The display for which to suppress
            events.
        """
        raise NotImplementedError()

    def _suppress_stop(self, display):
        """Starts suppressing events.

        :param Xlib.display.Display display: The display for which to suppress
            events.
        """
        raise NotImplementedError()

    @property
    def _event_mask(self):
        """The event mask.
        """
        return functools.reduce(operator.__or__, self._EVENTS, 0)

    @AbstractListener._emitter
    def _handler(self, events):
        """The callback registered with *X* for mouse events.

        This method will parse the response and call the callbacks registered
        on initialisation.

        :param events: The events passed by *X*. This is a binary block
            parsable by :attr:`_EVENT_PARSER`.
        """
        if not self.running:
            raise self.StopException()

        data = events.data

        while data and len(data):
            event, data = self._EVENT_PARSER.parse_binary_value(
                data, self._display_record.display, None, None)
            self._handle(self._display_stop, event)

    def _initialize(self, display):
        """Initialises this listener.

        This method is called immediately before the event loop, from the
        handler thread.

        :param display: The display being used.
        """
        pass

    def _handle(self, display, event):
        """The device specific callback handler.

        This method calls the appropriate callback registered when this
        listener was created based on the event.

        :param display: The display being used.

        :param event: The event.
        """
        pass
