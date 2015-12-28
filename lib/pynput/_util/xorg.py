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

import itertools
import Xlib.display
import Xlib.XK

from .xorg_keysyms import *


# Create a display to verify that we have an X connection
display = Xlib.display.Display()
display.close()
del display


class X11Error(Exception):
    """An error that is thrown at the end of a code block managed by a
    :func:`display_manager` if an *X11* error occurred.
    """
    pass


def display_manager(display):
    """Traps *X* errors and raises an :class:``X11Error`` at the end if any
    error occurred.

    This handler also ensures that the :class:`Xlib.display.Display` being
    managed is sync'd.

    :param Xlib.display.Display display: The *X* display.

    :return: the display
    :rtype: Xlib.display.Display
    """
    from contextlib import contextmanager

    @contextmanager
    def manager():
        errors = []

        def handler(*args):
            errors.append(args)

        old_handler = display.set_error_handler(handler)
        yield display
        display.sync()
        display.set_error_handler(old_handler)
        if errors:
            raise X11Error(errors)

    return manager()


def _find_mask(display, symbol):
    """Returns the mode flags to use for a modiofier symbol.
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
    """
    return _find_mask(display, 'Alt_L')


def alt_gr_mask(display):
    """Returns the *alt* mask flags.
    """
    return _find_mask(display, 'Mode_switch')


def keysym_is_latin_upper(keysym):
    """Determines whether a *keysym* is an upper case *latin* character.
    """
    return Xlib.XK.XK_A <= keysym <= Xlib.XK.XK_Z


def keysym_is_latin_lower(keysym):
    """Determines whether a *keysym* is a lower case *latin* character.
    """
    return Xlib.XK.XK_a <= keysym <= Xlib.XK.XK_z


def keysym_group(a, b):
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

    :param a: The first *keysym*.

    :param b: The second *keysym*.

    :return: a tuple conforming to the description above
    """
    if b == Xlib.XK.NoSymbol:
        if keysym_is_latin_upper(a):
            return (Xlib.XK.XK_a + a - Xlib.XK.XK_A, a)
        elif keysym_is_latin_lower(a):
            return (a, Xlib.XK.XK_A + a - Xlib.XK.XK_a)
        else:
            return (a, a)
    else:
        return (a, b)


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

    :retur: a shift mask
    """
    return 0 \
        | 1 << 0 if index & 1 else 0 \
        | alt_gr_mask(display) if index & 2 else 0


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
        key_code = index + display.display.info.min_keycode

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
                if keysym in mapping and mapping[keysym][1] < shift_state:
                    continue
                mapping[keysym] = (key_code, shift_state)

    return mapping


def symbol_to_keysym(symbol):
    """Converts a symbol name to a *keysym*.

    :param str symbol: The name of the symbol.

    :return: the corresponding *keysym*, or ``0`` if it cannot be found
    """
    # First try simple translation
    keysym = Xlib.XK.string_to_keysym(symbol)
    if keysym:
        return keysym

    # If that fails, try checking a module attribute of Xlib.keysymdef.xkb
    if not keysym:
        try:
            return getattr(Xlib.keysymdef.xkb, 'XK_' + symbol, 0)
        except:
            return SYMBOLS.get(symbol, (0,))[0]
