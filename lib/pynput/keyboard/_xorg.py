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

import enum
import threading

import Xlib.display
import Xlib.ext
import Xlib.ext.xtest
import Xlib.X
import Xlib.XK
import Xlib.protocol

from pynput._util.xorg import *
from . import _base


class KeyCode(_base.KeyCode):
    @classmethod
    def from_symbol(self, symbol):
        """Creates a key from a symbol.

        :param str symbol: The symbol name.

        :return: a key code
        """
        # First try simple translation
        keysym = Xlib.XK.string_to_keysym(symbol)
        if keysym:
            return self.from_vk(keysym)

        # If that fails, try checking a module attribute of Xlib.keysymdef.xkb
        if not keysym:
            try:
                return self.from_vk(
                    getattr(Xlib.keysymdef.xkb, 'XK_' + symbol, 0))
            except:
                return self.from_vk(
                    SYMBOLS.get(symbol, (0,))[0])


class Key(enum.Enum):
    # Default keys
    alt = KeyCode.from_symbol('Alt_L')
    alt_l = KeyCode.from_symbol('Alt_L')
    alt_r = KeyCode.from_symbol('Alt_R')
    alt_gr = KeyCode.from_symbol('Mode_switch')
    backspace = KeyCode.from_symbol('BackSpace')
    caps_lock = KeyCode.from_symbol('Caps_Lock')
    cmd = KeyCode.from_symbol('Super_L')
    cmd_l = KeyCode.from_symbol('Super_L')
    cmd_r = KeyCode.from_symbol('Super_R')
    ctrl = KeyCode.from_symbol('Control_L')
    ctrl_l = KeyCode.from_symbol('Control_L')
    ctrl_r = KeyCode.from_symbol('Control_R')
    delete = KeyCode.from_symbol('Delete')
    down = KeyCode.from_symbol('Down')
    end = KeyCode.from_symbol('End')
    enter = KeyCode.from_symbol('Return')
    esc = KeyCode.from_symbol('Escape')
    f1 = KeyCode.from_symbol('F1')
    f2 = KeyCode.from_symbol('F2')
    f3 = KeyCode.from_symbol('F3')
    f4 = KeyCode.from_symbol('F4')
    f5 = KeyCode.from_symbol('F5')
    f6 = KeyCode.from_symbol('F6')
    f7 = KeyCode.from_symbol('F7')
    f8 = KeyCode.from_symbol('F8')
    f9 = KeyCode.from_symbol('F9')
    f10 = KeyCode.from_symbol('F10')
    f11 = KeyCode.from_symbol('F11')
    f12 = KeyCode.from_symbol('F12')
    f13 = KeyCode.from_symbol('F13')
    f14 = KeyCode.from_symbol('F14')
    f15 = KeyCode.from_symbol('F15')
    f16 = KeyCode.from_symbol('F16')
    f17 = KeyCode.from_symbol('F17')
    f18 = KeyCode.from_symbol('F18')
    f19 = KeyCode.from_symbol('F19')
    f20 = KeyCode.from_symbol('F20')
    home = KeyCode.from_symbol('Home')
    left = KeyCode.from_symbol('Left')
    page_down = KeyCode.from_symbol('Page_Down')
    page_up = KeyCode.from_symbol('Page_Up')
    right = KeyCode.from_symbol('Right')
    shift = KeyCode.from_symbol('Shift_L')
    shift_l = KeyCode.from_symbol('Shift_L')
    shift_r = KeyCode.from_symbol('Shift_R')
    space = KeyCode(vk=Xlib.XK.string_to_keysym('space'), char=' ')
    tab = KeyCode.from_symbol('Tab')
    up = KeyCode.from_symbol('Up')

    insert = KeyCode.from_symbol('Insert')
    menu = KeyCode.from_symbol('Menu')
    num_lock = KeyCode.from_symbol('Num_Lock')
    pause = KeyCode.from_symbol('Pause')
    print_screen = KeyCode.from_symbol('Print')
    scroll_lock = KeyCode.from_symbol('Scroll_Lock')


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    #: The shift mask for :attr:`Key.ctrl`
    CTRL_MASK = Xlib.X.ControlMask

    #: The shift mask for :attr:`Key.shift`
    SHIFT_MASK = Xlib.X.ShiftMask

    def __init__(self):
        super(Controller, self).__init__()
        self._display = Xlib.display.Display()
        self._keyboard_mapping = None
        self._borrows = {}
        self._borrow_lock = threading.RLock()

        self.ALT_MASK = alt_mask(self._display)
        self.ALT_GR_MASK = alt_gr_mask(self._display)

    def __del__(self):
        if self._display:
            self._display.close()

    @property
    def keyboard_mapping(self):
        """A mapping from *keysyms* to *key codes*.

        Each value is the tuple ``(key_code, shift_state)``. By sending an
        event with the specified *key code* and shift state, the specified
        *keysym* will be touched.
        """
        if not self._keyboard_mapping:
            self._update_keyboard_mapping()
        return self._keyboard_mapping

    def _handle(self, key, is_press):
        """Resolves a key identifier and sends a keyboard event.

        :param event: The *X* keyboard event.

        :param int keysym: The keysym to handle.
        """
        event = Xlib.display.event.KeyPress if is_press \
            else Xlib.display.event.KeyRelease
        keysym = self._keysym(key)

        # Make sure to verify that the key was resolved
        if keysym is None:
            raise self.InvalidKeyException(key)

        try:
            keycode, shift_state = self.keyboard_mapping[keysym]
            self._send_key(event, keycode, shift_state)

        except KeyError:
            with self._borrow_lock:
                keycode, index, count = self._borrows[keysym]
                self._send_key(
                    event, keycode, index_to_shift(self._display, index))
                count += 1 if is_press else -1
                self._borrows[keysym] = (keycode, index, count)

    def _keysym(self, key):
        """Converts a key to a *keysym*.

        :param KeyCode key: The key code to convert.
        """
        return self._resolve_dead(key) if key.is_dead else None \
            or self._resolve_special(key) \
            or self._resolve_normal(key) \
            or self._resolve_borrowed(key) \
            or self._resolve_borrowing(key)

    def _send_key(self, event, keycode, shift_state):
        """Sends a single keyboard event.

        :param event: The *X* keyboard event.

        :param int keycode: The keycode.

        :param int shift_state: The shift state. The actual value used is
            :attr:`shift_state` or'd with this value.
        """
        with display_manager(self._display) as d, self.modifiers as modifiers:
            window = d.get_input_focus().focus
            window.send_event(event(
                detail=keycode,
                state=shift_state | self._shift_mask(modifiers),
                time=0,
                root=d.screen().root,
                window=window,
                same_screen=0,
                child=Xlib.X.NONE,
                root_x=0, root_y=0, event_x=0, event_y=0))

    def _resolve_dead(self, key):
        """Tries to resolve a dead key.

        :param str identifier: The identifier to resolve.
        """
        try:
            keysym, _ = SYMBOLS[CHARS[key.combining]]
        except:
            return None

        if keysym not in self.keyboard_mapping:
            return None

        return keysym

    def _resolve_special(self, key):
        """Tries to resolve a special key.

        A special key has the :attr:`~KeyCode.vk` attribute set.

        :param KeyCode key: The key to resolve.
        """
        if not key.vk:
            return None

        return key.vk

    def _resolve_normal(self, key):
        """Tries to resolve a normal key.

        A normal key exists on the keyboard, and is typed by pressing
        and releasing a simple key, possibly in combination with a modifier.

        :param KeyCode key: The key to resolve.
        """
        keysym = self._key_to_keysym(key)
        if keysym is None:
            return None

        if keysym not in self.keyboard_mapping:
            return None

        return keysym

    def _resolve_borrowed(self, key):
        """Tries to resolve a key by looking up the already borrowed *keysyms*.

        A borrowed *keysym* does not exist on the keyboard, but has been
        temporarily added to the layout.

        :param KeyCode key: The key to resolve.
        """
        keysym = self._key_to_keysym(key)
        if keysym is None:
            return None

        with self._borrow_lock:
            if keysym not in self._borrows:
                return None

        return keysym

    def _resolve_borrowing(self, key):
        """Tries to resolve a key by modifying the layout temporarily.

        A borrowed *keysym* does not exist on the keyboard, but is temporarily
        added to the layout.

        :param KeyCode key: The key to resolve.
        """
        keysym = self._key_to_keysym(key)
        if keysym is None:
            return None

        keyboard_mapping = self._display.get_keyboard_mapping(8, 255 - 8)

        def i2kc(index):
            return index + 8

        def kc2i(keycode):
            return keycode - 8

        #: Finds a keycode and index by looking at already used keycodes
        def reuse():
            for keysym, (keycode, _, _) in self._borrows.items():
                keycodes = keyboard_mapping[kc2i(keycode)]

                # Only the first four items are addressable by X
                for index in range(4):
                    if not keycodes[index]:
                        return keycode, index

        #: Finds a keycode and index by using a new keycode
        def borrow():
            for i, keycodes in enumerate(keyboard_mapping):
                if not any(keycodes):
                    return i2kc(i), 0

        #: Finds a keycode and index by reusing an old, unused one
        def overwrite():
            for keysym, (keycode, index, count) in self._borrows.items():
                if count < 1:
                    del self._borrows[keysym]
                    return keycode, index

        #: Registers a keycode for a specific key and modifier state
        def register(keycode, index):
            i = kc2i(keycode)
            keyboard_mapping[i][index] = keysym
            d.change_keyboard_mapping(
                keycode,
                keyboard_mapping[i:i + 1])
            self._borrows[keysym] = (keycode, index, 0)

        try:
            with display_manager(self._display) as d, self._borrow_lock:
                # First try an already used keycode, then try a new one, and
                # fall back on reusing one that is not currently pressed
                register(*(
                    reuse() or
                    borrow() or
                    overwrite()))
            return keysym

        except TypeError:
            return None

    def _key_to_keysym(self, key):
        """Converts a character key code to a *keysym*.

        :param KeyCode key: The key code.

        :return: a keysym if found
        :rtype: int or None
        """
        symbol = CHARS.get(key.char, None)
        if symbol is None:
            return None

        try:
            return symbol_to_keysym(symbol)
        except:
            try:
                return SYMBOLS[symbol][0]
            except:
                return None

    def _shift_mask(self, modifiers):
        """The *X* modifier mask to apply for a set of modifiers.

        :param set modifiers: A set of active modifiers for which to get the
            shift mask.
        """
        return (
            (self.ALT_MASK
                if Key.alt in modifiers else 0) |

            (self.ALT_GR_MASK
                if Key.alt_gr in modifiers else 0) |

            (self.CTRL_MASK
                if Key.ctrl in modifiers else 0) |

            (self.SHIFT_MASK
                if Key.shift in modifiers else 0))

    def _update_keyboard_mapping(self):
        """Updates the keyboard mapping.
        """
        with display_manager(self._display) as d:
            self._keyboard_mapping = keyboard_mapping(d)
