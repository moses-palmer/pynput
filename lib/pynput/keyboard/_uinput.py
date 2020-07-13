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
The keyboard implementation for *uinput*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import enum
import errno
import functools
import os
import re
import subprocess

import evdev

from evdev.events import KeyEvent

from pynput._util import xorg_keysyms
from pynput._util.uinput import ListenerMixin
from . import _base


class KeyCode(_base.KeyCode):
    _PLATFORM_EXTENSIONS = (
        # The name for this key
        '_x_name',
        '_kernel_name',
    )

    # Be explicit about fields
    _x_name = None
    _kernel_name = None
# pylint: enable=W0212

    @classmethod
    def _from_name(cls, x_name, kernel_name, **kwargs):
        """Creates a key from a name.

        :param str x_name: The X name.

        :param str kernel_name: The kernel name.

        :return: a key code
        """
        try:
            vk = getattr(evdev.ecodes, kernel_name)
        except AttributeError:
            vk = None
        return cls.from_vk(
            vk, _x_name=x_name, _kernel_name=kernel_name, **kwargs)


# pylint: disable=W0212
class Key(enum.Enum):
    alt = KeyCode._from_name('Alt_L', 'KEY_LEFTALT')
    alt_l = KeyCode._from_name('Alt_L', 'KEY_LEFTALT')
    alt_r = KeyCode._from_name('Alt_R', 'KEY_RIGHTALT')
    alt_gr = KeyCode._from_name('Mode_switch', 'KEY_RIGHTALT')
    backspace = KeyCode._from_name('BackSpace', 'KEY_BACKSPACE')
    caps_lock = KeyCode._from_name('Caps_Lock', 'KEY_CAPSLOCK')
    cmd = KeyCode._from_name('Super_L', 'KEY_LEFTMETA')
    cmd_l = KeyCode._from_name('Super_L', 'KEY_LEFTMETA')
    cmd_r = KeyCode._from_name('Super_R', 'KEY_RIGHTMETA')
    ctrl = KeyCode._from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_l = KeyCode._from_name('Control_L', 'KEY_LEFTCTRL')
    ctrl_r = KeyCode._from_name('Control_R', 'KEY_RIGHTCTRL')
    delete = KeyCode._from_name('Delete', 'KEY_DELETE')
    down = KeyCode._from_name('Down', 'KEY_DOWN')
    end = KeyCode._from_name('End', 'KEY_END')
    enter = KeyCode._from_name('Return', 'KEY_ENTER')
    esc = KeyCode._from_name('Escape', 'KEY_ESC')
    f1 = KeyCode._from_name('F1', 'KEY_F1')
    f2 = KeyCode._from_name('F2', 'KEY_F2')
    f3 = KeyCode._from_name('F3', 'KEY_F3')
    f4 = KeyCode._from_name('F4', 'KEY_F4')
    f5 = KeyCode._from_name('F5', 'KEY_F5')
    f6 = KeyCode._from_name('F6', 'KEY_F6')
    f7 = KeyCode._from_name('F7', 'KEY_F7')
    f8 = KeyCode._from_name('F8', 'KEY_F8')
    f9 = KeyCode._from_name('F9', 'KEY_F9')
    f10 = KeyCode._from_name('F10', 'KEY_F10')
    f11 = KeyCode._from_name('F11', 'KEY_F11')
    f12 = KeyCode._from_name('F12', 'KEY_F12')
    f13 = KeyCode._from_name('F13', 'KEY_F13')
    f14 = KeyCode._from_name('F14', 'KEY_F14')
    f15 = KeyCode._from_name('F15', 'KEY_F15')
    f16 = KeyCode._from_name('F16', 'KEY_F16')
    f17 = KeyCode._from_name('F17', 'KEY_F17')
    f18 = KeyCode._from_name('F18', 'KEY_F18')
    f19 = KeyCode._from_name('F19', 'KEY_F19')
    f20 = KeyCode._from_name('F20', 'KEY_F20')
    home = KeyCode._from_name('Home', 'KEY_HOME')
    left = KeyCode._from_name('Left', 'KEY_LEFT')
    page_down = KeyCode._from_name('Page_Down', 'KEY_PAGEDOWN')
    page_up = KeyCode._from_name('Page_Up', 'KEY_PAGEUP')
    right = KeyCode._from_name('Right', 'KEY_RIGHT')
    shift = KeyCode._from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_l = KeyCode._from_name('Shift_L', 'KEY_LEFTSHIFT')
    shift_r = KeyCode._from_name('Shift_R', 'KEY_RIGHTSHIFT')
    space = KeyCode._from_name('space', 'KEY_SPACE', char=' ')
    tab = KeyCode._from_name('Tab', 'KEY_TAB', char='\t')
    up = KeyCode._from_name('Up', 'KEY_UP')

    media_play_pause = KeyCode._from_name('Play', 'KEY_PLAYPAUSE')
    media_volume_mute = KeyCode._from_name('Mute', 'KEY_MUTE')
    media_volume_down = KeyCode._from_name('LowerVolume', 'KEY_VOLUMEDOWN')
    media_volume_up = KeyCode._from_name('RaiseVolume', 'KEY_VOLUMEUP')
    media_previous = KeyCode._from_name('Prev', 'KEY_PREVIOUSSONG')
    media_next = KeyCode._from_name('Next', 'KEY_NEXTSONG')

    insert = KeyCode._from_name('Insert', 'KEY_INSERT')
    menu = KeyCode._from_name('Menu', 'KEY_MENU')
    num_lock = KeyCode._from_name('Num_Lock', 'KEY_NUMLOCK')
    pause = KeyCode._from_name('Pause', 'KEY_PAUSE')
    print_screen = KeyCode._from_name('Print', 'KEY_SYSRQ')
    scroll_lock = KeyCode._from_name('Scroll_Lock', 'KEY_SCROLLLOCK')
# pylint: enable=W0212


class Layout(object):
    """A description of the keyboard layout.
    """
    #: A regular expression to parse keycodes in the dumpkeys output
    #:
    #: The groups are: keycode number, key names.
    KEYCODE_RE = re.compile(
        r'keycode\s+(\d+)\s+=(.*)')

    class Key(object):
        """A key in a keyboard layout.
        """
        def __init__(self, normal, shifted, alt, alt_shifted):
            self._values = (
                normal,
                shifted,
                alt,
                alt_shifted)

        def __str__(self):
            return ('<'
                'normal: {}, '
                'shifted: {}, '
                'alternative: {}, '
                'shifted alternative: {}>').format(
                    self.normal, self.shifted, self.alt, self.alt_shifted)

        __repr__ = __str__

        def __iter__(self):
            return iter(self._values)

        def __getitem__(self, i):
            return self._values[i]

        @property
        def normal(self):
            """The normal key.
            """
            return self._values[0]

        @property
        def shifted(self):
            """The shifted key.
            """
            return self._values[1]

        @property
        def alt(self):
            """The alterntive key.
            """
            return self._values[2]

        @property
        def alt_shifted(self):
            """The shifted alternative key.
            """
            return self._values[3]

    def __init__(self):
        def as_char(k):
            return k.value.char if isinstance(k, Key) else k.char
        self._vk_table = self._load()
        self._char_table = {
            as_char(key): (
                vk,
                set()
                    | {Key.shift} if i & 1 else set()
                    | {Key.alt_gr} if i & 2 else set())
            for vk, keys in self._vk_table.items()
            for i, key in enumerate(keys)
            if key is not None and as_char(key) is not None}

    def for_vk(self, vk, modifiers):
        """Reads a key for a virtual key code and modifier state.

        :param int vk: The virtual key code.

        :param set modifiers: A set of modifiers.

        :return: a mapped key

        :raises ValueError: if ``modifiers`` contains keys other than
            :attr:`Key.shift` and :attr:`Key.alt_gr`

        :raises KeyError: if ``vk`` is an unknown key
        """
        if not {Key.shift, Key.alt_gr}.issuperset(modifiers):
            raise ValueError(modifiers)
        else:
            return self._vk_table[vk][
                0
                | (1 if Key.shift in modifiers else 0)
                | (2 if Key.alt_gr in modifiers else 0)]

    def for_char(self, char):
        """Reads a virtual key code and modifier state for a character.

        :param str char: The character.

        :return: the tuple ``(vk, modifiers)``

        :raises KeyError: if ``vk`` is an unknown key
        """
        return self._char_table[char]

    @functools.lru_cache()
    def _load(self):
        """Loads the keyboard layout.

        For simplicity, we call out to the ``dumpkeys`` binary. In the future,
        we may want to implement this ourselves.
        """
        result = {}
        for keycode, names in self.KEYCODE_RE.findall(
                subprocess.check_output(
                    ['dumpkeys', '--full-table']).decode('utf-8')):
            vk = int(keycode)
            keys = tuple(
                self._parse(vk, name)
                for name in names.split()[:4])
            if any(key is not None for key in keys):
                result[vk] = self.Key(*keys)
        return result

    def _parse(self, vk, name):
        """Parses a single key from the ``dumpkeys`` output.

        :param int vk: The key code.

        :param str name: The key name.

        :return: a key representation
        """
        try:
            # First try special keys...
            return next(
                key
                for key in Key
                if key.value._x_name == name)
        except StopIteration:
            # ...then characters...
            try:
                _, char = xorg_keysyms.SYMBOLS[name.lstrip('+')]
                if char:
                    return KeyCode.from_char(char, vk=vk)
            except KeyError:
                pass

            # ...and finally special dumpkeys names
            try:
                return KeyCode.from_char({
                    'one': '1',
                    'two': '2',
                    'three': '3',
                    'four': '4',
                    'five': '5',
                    'six': '6',
                    'seven': '7',
                    'eight': '8',
                    'nine': '9',
                    'zero': '0'}[name])
            except KeyError:
                pass


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self._layout = LAYOUT
        self._dev = evdev.UInput()

    def __del__(self):
        if hasattr(self, '_dev'):
            self._dev.close()

    def _handle(self, key, is_press):
        # Resolve the key to a virtual key code and a possible set of required
        # modifiers
        try:
            vk, required_modifiers = self._to_vk_and_modifiers(key)
        except ValueError:
            raise self.InvalidKeyException(key)

        # Determine how we need to modify the modifier state
        if is_press and required_modifiers is not None:
            with self.modifiers as modifiers:
                vk, required_modifiers = self._layout.for_char(key.char)
                to_press = {
                    getattr(evdev.ecodes, key.value._kernel_name)
                    for key in (required_modifiers - modifiers)}
                to_release = {
                    getattr(evdev.ecodes, key.value._kernel_name)
                    for key in (modifiers - required_modifiers)}
        else:
            to_release = set()
            to_press = set()

        # Update the modifier state, send the key, and finally release any
        # modifiers
        cleanup = []
        try:
            for k in to_release:
                self._send(k, False)
                cleanup.append((k, True))
            for k in to_press:
                self._send(k, True)
                cleanup.append((k, False))

            self._send(vk, is_press)

        finally:
            for e in reversed(cleanup):
                # pylint: disable E722; we want to suppress exceptions
                try:
                    self._send(*e)
                except:
                    pass
                # pylint: enable E722

            self._dev.syn()

    def _to_vk_and_modifiers(self, key):
        """Resolves a key to a virtual key code and a modifier set.

        :param key: The key to resolve.
        :type key: Key or KeyCode

        :return: a virtual key code and possible required modifiers
        """
        if hasattr(key, 'vk') and key.vk is not None:
            return (key.vk, None)
        elif hasattr(key, 'char') and key.char is not None:
            return self._layout.for_char(key.char)
        else:
            raise ValueError(key)

    def _send(self, vk, is_press):
        """Sends a virtual key event.

        This method does not perform ``SYN``.

        :param int vk: The virtual key.

        :param bool is_press: Whether this is a press event.
        """
        self._dev.write(evdev.ecodes.EV_KEY, vk, int(is_press))


class Listener(ListenerMixin, _base.Listener):
    _EVENTS = (
        evdev.ecodes.EV_KEY,)

    #: A
    _MODIFIERS = {
        Key.alt.value.vk: Key.alt,
        Key.alt_l.value.vk: Key.alt,
        Key.alt_r.value.vk: Key.alt,
        Key.alt_gr.value.vk: Key.alt_gr,
        Key.shift.value.vk: Key.shift,
        Key.shift_l.value.vk: Key.shift,
        Key.shift_r.value.vk: Key.shift}

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._layout = LAYOUT
        self._modifiers = set()

    def _handle(self, event):
        is_press = event.value in (KeyEvent.key_down, KeyEvent.key_hold)
        vk = event.code

        # Update the modifier state
        if vk in self._MODIFIERS:
            modifier = self._MODIFIERS[vk]
            if is_press:
                self._modifiers.add(modifier)
            elif modifier in self._modifiers:
                self._modifiers.remove(modifier)

        # Attempt to map the virtual key code to a character
        try:
            char = self._layout.for_vk(vk, self._modifiers)
        except KeyError:
            char = None

        # If we find a character, use that, otherwise try with a special key
        if char is not None:
            key = KeyCode.from_char(char, vk=vk)
        else:
            try:
                key = next(
                    key
                    for key in Key
                    if key.value.vk == vk)
            except StopIteration:
                key = KeyCode.from_vk(vk)

        if is_press:
            self.on_press(key)
        else:
            self.on_release(key)


try:
    #: The keyboard layout.
    LAYOUT = Layout()
except subprocess.CalledProcessError as e:
    raise ImportError('failed to load keyboard layout: "' + str(e) + (
        '"; please make sure you are root' if os.getuid() != 1 else '"'))
except OSError as e:
    raise ImportError({
        errno.ENOENT: 'the binary dumpkeys is not installed'}.get(
            e.args[0],
            str(e)))
