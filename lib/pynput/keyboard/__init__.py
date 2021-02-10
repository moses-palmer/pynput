# coding=utf-8
# pynput
# Copyright (C) 2015-2021 Moses Palmér
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

import itertools

from pynput._util import backend, Events


backend = backend(__name__)
KeyCode = backend.KeyCode
Key = backend.Key
Controller = backend.Controller
Listener = backend.Listener
del backend


# pylint: disable=C0326; it is easier to read column aligned keys
#: The keys used as modifiers; the first value in each tuple is the
#: base modifier to use for subsequent modifiers.
_MODIFIER_KEYS = (
    (Key.alt_gr, (Key.alt_gr.value,)),
    (Key.alt,    (Key.alt.value,   Key.alt_l.value,   Key.alt_r.value)),
    (Key.cmd,    (Key.cmd.value,   Key.cmd_l.value,   Key.cmd_r.value)),
    (Key.ctrl,   (Key.ctrl.value,  Key.ctrl_l.value,  Key.ctrl_r.value)),
    (Key.shift,  (Key.shift.value, Key.shift_l.value, Key.shift_r.value)))

#: Normalised modifiers as a mapping from virtual key code to basic modifier.
_NORMAL_MODIFIERS = {
    value: key
    for combination in _MODIFIER_KEYS
    for key, value in zip(
        itertools.cycle((combination[0],)),
        combination[1])}

#: Control codes to transform into key codes when typing
_CONTROL_CODES = {
    '\n': Key.enter,
    '\r': Key.enter,
    '\t': Key.tab}
# pylint: enable=C0326


class Events(Events):
    """A keyboard event listener supporting synchronous iteration over the
    events.

    Possible events are:

    :class:`Events.Press`
        A key was pressed.

    :class:`Events.Release`
        A key was released.
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


class HotKey(object):
    """A combination of keys acting as a hotkey.

    This class acts as a container of hotkey state for a keyboard listener.

    :param set keys: The collection of keys that must be pressed for this
        hotkey to activate. Please note that a common limitation of the
        hardware is that at most three simultaneously pressed keys are
        supported, so using more keys may not work.

    :param callable on_activate: The activation callback.
    """
    def __init__(self, keys, on_activate):
        self._state = set()
        self._keys = set(keys)
        self._on_activate = on_activate

    @staticmethod
    def parse(keys):
        """Parses a key combination string.

        Key combination strings are sequences of key identifiers separated by
        ``'+'``. Key identifiers are either single characters representing a
        keyboard key, such as ``'a'``, or special key names identified by names
        enclosed by brackets, such as ``'<ctrl>'``.

        Keyboard keys are case-insensitive.

        :raises ValueError: if a part of the keys string is invalid, or if it
            contains multiple equal parts
        """
        def parts():
            start = 0
            for i, c in enumerate(keys):
                if c == '+' and i != start:
                    yield keys[start:i]
                    start = i + 1
            if start == len(keys):
                raise ValueError(keys)
            else:
                yield keys[start:]

        def parse(s):
            if len(s) == 1:
                return KeyCode.from_char(s.lower())
            elif len(s) > 2 and (s[0], s[-1]) == ('<', '>'):
                p = s[1:-1]
                try:
                    return Key[p.lower()]
                except KeyError:
                    try:
                        return KeyCode.from_vk(int(p))
                    except ValueError:
                        raise ValueError(s)
            else:
                raise ValueError(s)

        # Split the string and parse the individual parts
        raw_parts = list(parts())
        parsed_parts = [
            parse(s)
            for s in raw_parts]

        # Ensure no duplicate parts
        if len(parsed_parts) != len(set(parsed_parts)):
            raise ValueError(keys)
        else:
            return parsed_parts

    def press(self, key):
        """Updates the hotkey state for a pressed key.

        If the key is not currently pressed, but is the last key for the full
        combination, the activation callback will be invoked.

        Please note that the callback will only be invoked once.

        :param key: The key being pressed.
        :type key: Key or KeyCode
        """
        if key in self._keys and key not in self._state:
            self._state.add(key)
            if self._state == self._keys:
                self._on_activate()

    def release(self, key):
        """Updates the hotkey state for a released key.

        :param key: The key being released.
        :type key: Key or KeyCode
        """
        if key in self._state:
            self._state.remove(key)


class GlobalHotKeys(Listener):
    """A keyboard listener supporting a number of global hotkeys.

    This is a convenience wrapper to simplify registering a number of global
    hotkeys.

    :param dict hotkeys: A mapping from hotkey description to hotkey action.
        Keys are strings passed to :meth:`HotKey.parse`.

    :raises ValueError: if any hotkey description is invalid
    """
    def __init__(self, hotkeys, *args, **kwargs):
        self._hotkeys = [
            HotKey(HotKey.parse(key), value)
            for key, value in hotkeys.items()]
        super(GlobalHotKeys, self).__init__(
            on_press=self._on_press,
            on_release=self._on_release,
            *args,
            **kwargs)

    def _on_press(self, key):
        """The press callback.

        This is automatically registered upon creation.

        :param key: The key provided by the base class.
        """
        for hotkey in self._hotkeys:
            hotkey.press(self.canonical(key))

    def _on_release(self, key):
        """The release callback.

        This is automatically registered upon creation.

        :param key: The key provided by the base class.
        """
        for hotkey in self._hotkeys:
            hotkey.release(self.canonical(key))
