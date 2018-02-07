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
This module contains the base implementation.

The actual interface to keyboard classes is defined here, but the
implementation is located in a platform dependent module.
"""

# pylint: disable=R0903
# We implement stubs

import contextlib
import enum
import threading
import unicodedata

import six

from pynput._util import AbstractListener, prefix
from pynput import _logger


class KeyCode(object):
    """
    A :class:`KeyCode` represents the description of a key code used by the
    operating system.
    """
    #: The names of attributes used as platform extensions.
    _PLATFORM_EXTENSIONS = []

    def __init__(self, vk=None, char=None, is_dead=False, **kwargs):
        self.vk = vk
        self.char = six.text_type(char) if char is not None else None
        self.is_dead = is_dead

        if self.is_dead:
            try:
                self.combining = unicodedata.lookup(
                    'COMBINING ' + unicodedata.name(self.char))
            except KeyError:
                self.is_dead = False
                self.combining = None
            if self.is_dead and not self.combining:
                raise KeyError(char)
        else:
            self.combining = None

        for key in self._PLATFORM_EXTENSIONS:
            setattr(self, key, kwargs.pop(key, None))
        if kwargs:
            raise ValueError(kwargs)


    def __repr__(self):
        if self.is_dead:
            return '[%s]' % repr(self.char)
        if self.char is not None:
            return repr(self.char)
        else:
            return '<%d>' % self.vk

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.char is not None and other.char is not None:
            return self.char == other.char and self.is_dead == other.is_dead
        else:
            return self.vk == other.vk and all(
                getattr(self, f) == getattr(other, f)
                for f in self._PLATFORM_EXTENSIONS)

    def __hash__(self):
        return hash(repr(self))

    def join(self, key):
        """Applies this dead key to another key and returns the result.

        Joining a dead key with space (``' '``) or itself yields the non-dead
        version of this key, if one exists; for example,
        ``KeyCode.from_dead('~').join(KeyCode.from_char(' '))`` equals
        ``KeyCode.from_char('~')`` and
        ``KeyCode.from_dead('~').join(KeyCode.from_dead('~'))``.

        :param KeyCode key: The key to join with this key.

        :return: a key code

        :raises ValueError: if the keys cannot be joined
        """
        # A non-dead key cannot be joined
        if not self.is_dead:
            raise ValueError(self)

        # Joining two of the same keycodes, or joining with space, yields the
        # non-dead version of the key
        if key.char == ' ' or self == key:
            return self.from_char(self.char)

        # Otherwise we combine the characters
        if key.char is not None:
            combined = unicodedata.normalize(
                'NFC',
                key.char + self.combining)
            if combined:
                return self.from_char(combined)

        raise ValueError(key)

    @classmethod
    def from_vk(cls, vk, **kwargs):
        """Creates a key from a virtual key code.

        :param vk: The virtual key code.

        :param kwargs: Any other parameters to pass.

        :return: a key code
        """
        return cls(vk=vk, **kwargs)

    @classmethod
    def from_char(cls, char, **kwargs):
        """Creates a key from a character.

        :param str char: The character.

        :return: a key code
        """
        return cls(char=char, **kwargs)

    @classmethod
    def from_dead(cls, char, **kwargs):
        """Creates a dead key.

        :param char: The dead key. This should be the unicode character
            representing the stand alone character, such as ``'~'`` for
            *COMBINING TILDE*.

        :return: a key code
        """
        return cls(char=char, is_dead=True, **kwargs)


class Key(enum.Enum):
    """A class representing various buttons that may not correspond to
    letters. This includes modifier keys and function keys.

    The actual values for these items differ between platforms. Some platforms
    may have additional buttons, but these are guaranteed to be present
    everywhere.
    """
    #: A generic Alt key. This is a modifier.
    alt = KeyCode.from_vk(0)

    #: The left Alt key. This is a modifier.
    alt_l = KeyCode.from_vk(0)

    #: The right Alt key. This is a modifier.
    alt_r = KeyCode.from_vk(0)

    #: The AltGr key. This is a modifier.
    alt_gr = KeyCode.from_vk(0)

    #: The Backspace key.
    backspace = KeyCode.from_vk(0)

    #: The CapsLock key.
    caps_lock = KeyCode.from_vk(0)

    #: A generic command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd = KeyCode.from_vk(0)

    #: The left command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd_l = KeyCode.from_vk(0)

    #: The right command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd_r = KeyCode.from_vk(0)

    #: A generic Ctrl key. This is a modifier.
    ctrl = KeyCode.from_vk(0)

    #: The left Ctrl key. This is a modifier.
    ctrl_l = KeyCode.from_vk(0)

    #: The right Ctrl key. This is a modifier.
    ctrl_r = KeyCode.from_vk(0)

    #: The Delete key.
    delete = KeyCode.from_vk(0)

    #: A down arrow key.
    down = KeyCode.from_vk(0)

    #: The End key.
    end = KeyCode.from_vk(0)

    #: The Enter or Return key.
    enter = KeyCode.from_vk(0)

    #: The Esc key.
    esc = KeyCode.from_vk(0)

    #: The function keys. F1 to F20 are defined.
    f1 = KeyCode.from_vk(0)
    f2 = KeyCode.from_vk(0)
    f3 = KeyCode.from_vk(0)
    f4 = KeyCode.from_vk(0)
    f5 = KeyCode.from_vk(0)
    f6 = KeyCode.from_vk(0)
    f7 = KeyCode.from_vk(0)
    f8 = KeyCode.from_vk(0)
    f9 = KeyCode.from_vk(0)
    f10 = KeyCode.from_vk(0)
    f11 = KeyCode.from_vk(0)
    f12 = KeyCode.from_vk(0)
    f13 = KeyCode.from_vk(0)
    f14 = KeyCode.from_vk(0)
    f15 = KeyCode.from_vk(0)
    f16 = KeyCode.from_vk(0)
    f17 = KeyCode.from_vk(0)
    f18 = KeyCode.from_vk(0)
    f19 = KeyCode.from_vk(0)
    f20 = KeyCode.from_vk(0)

    #: The Home key.
    home = KeyCode.from_vk(0)

    #: A left arrow key.
    left = KeyCode.from_vk(0)

    #: The PageDown key.
    page_down = KeyCode.from_vk(0)

    #: The PageUp key.
    page_up = KeyCode.from_vk(0)

    #: A right arrow key.
    right = KeyCode.from_vk(0)

    #: A generic Shift key. This is a modifier.
    shift = KeyCode.from_vk(0)

    #: The left Shift key. This is a modifier.
    shift_l = KeyCode.from_vk(0)

    #: The right Shift key. This is a modifier.
    shift_r = KeyCode.from_vk(0)

    #: The Space key.
    space = KeyCode.from_vk(0)

    #: The Tab key.
    tab = KeyCode.from_vk(0)

    #: An up arrow key.
    up = KeyCode.from_vk(0)

    #: The play/pause toggle.
    media_play_pause = KeyCode.from_vk(0)

    #: The volume mute button.
    media_volume_mute = KeyCode.from_vk(0)

    #: The volume down button.
    media_volume_down = KeyCode.from_vk(0)

    #: The volume up button.
    media_volume_up = KeyCode.from_vk(0)

    #: The previous track button.
    media_previous = KeyCode.from_vk(0)

    #: The next track button.
    media_next = KeyCode.from_vk(0)

    #: The Insert key. This may be undefined for some platforms.
    insert = KeyCode.from_vk(0)

    #: The Menu key. This may be undefined for some platforms.
    menu = KeyCode.from_vk(0)

    #: The NumLock key. This may be undefined for some platforms.
    num_lock = KeyCode.from_vk(0)

    #: The Pause/Break key. This may be undefined for some platforms.
    pause = KeyCode.from_vk(0)

    #: The PrintScreen key. This may be undefined for some platforms.
    print_screen = KeyCode.from_vk(0)

    #: The ScrollLock key. This may be undefined for some platforms.
    scroll_lock = KeyCode.from_vk(0)


class Controller(object):
    """A controller for sending virtual keyboard events to the system.
    """
    #: The virtual key codes
    _KeyCode = KeyCode

    #: The various keys.
    _Key = Key

    class InvalidKeyException(Exception):
        """The exception raised when an invalid ``key`` parameter is passed to
        either :meth:`Controller.press` or :meth:`Controller.release`.

        Its first argument is the ``key`` parameter.
        """
        pass

    class InvalidCharacterException(Exception):
        """The exception raised when an invalid character is encountered in
        the string passed to :meth:`Controller.type`.

        Its first argument is the index of the character in the string, and the
        second the character.
        """
        pass

    def __init__(self):
        self._log = _logger(self.__class__)
        self._modifiers_lock = threading.RLock()
        self._modifiers = set()
        self._caps_lock = False
        self._dead_key = None

    def press(self, key):
        """Presses a key.

        A key may be either a string of length 1, one of the :class:`Key`
        members or a :class:`KeyCode`.

        Strings will be transformed to :class:`KeyCode` using
        :meth:`KeyCode.char`. Members of :class:`Key` will be translated to
        their :meth:`~Key.value`.

        :param key: The key to press.

        :raises InvalidKeyException: if the key is invalid

        :raises ValueError: if ``key`` is a string, but its length is not ``1``
        """
        resolved = self._resolve(key)
        if resolved is None:
            raise self.InvalidKeyException(key)
        self._update_modifiers(resolved, True)

        # Update caps lock state
        if resolved == self._Key.caps_lock.value:
            self._caps_lock = not self._caps_lock

        # If we currently have a dead key pressed, join it with this key
        original = resolved
        if self._dead_key:
            try:
                resolved = self._dead_key.join(resolved)
            except ValueError:
                self._handle(self._dead_key, True)
                self._handle(self._dead_key, False)

        # If the key is a dead key, keep it for later
        if resolved.is_dead:
            self._dead_key = resolved
            return

        try:
            self._handle(resolved, True)
        except self.InvalidKeyException:
            if resolved != original:
                self._handle(self._dead_key, True)
                self._handle(self._dead_key, False)
                self._handle(original, True)

        self._dead_key = None

    def release(self, key):
        """Releases a key.

        A key may be either a string of length 1, one of the :class:`Key`
        members or a :class:`KeyCode`.

        Strings will be transformed to :class:`KeyCode` using
        :meth:`KeyCode.char`. Members of :class:`Key` will be translated to
        their :meth:`~Key.value`.

        :param key: The key to release. If this is a string, it is passed to
            :meth:`touches` and the returned releases are used.

        :raises InvalidKeyException: if the key is invalid

        :raises ValueError: if ``key`` is a string, but its length is not ``1``
        """
        resolved = self._resolve(key)
        if resolved is None:
            raise self.InvalidKeyException(key)
        self._update_modifiers(resolved, False)

        # Ignore released dead keys
        if resolved.is_dead:
            return

        self._handle(resolved, False)

    def tap(self, key):
        """Presses and releases a key.

        This is equivalent to the following code::

            controller.press(key)
            controller.release(key)

        :param key: The key to press.

        :raises InvalidKeyException: if the key is invalid

        :raises ValueError: if ``key`` is a string, but its length is not ``1``
        """
        self.press(key)
        self.release(key)

    def touch(self, key, is_press):
        """Calls either :meth:`press` or :meth:`release` depending on the value
        of ``is_press``.

        :param key: The key to press or release.

        :param bool is_press: Whether to press the key.

        :raises InvalidKeyException: if the key is invalid
        """
        if is_press:
            self.press(key)
        else:
            self.release(key)

    @contextlib.contextmanager
    def pressed(self, *args):
        """Executes a block with some keys pressed.

        :param keys: The keys to keep pressed.
        """
        for key in args:
            self.press(key)

        try:
            yield
        finally:
            for key in reversed(args):
                self.release(key)

    def type(self, string):
        """Types a string.

        This method will send all key presses and releases necessary to type
        all characters in the string.

        :param str string: The string to type.

        :raises InvalidCharacterException: if an untypable character is
            encountered
        """
        from . import _CONTROL_CODES
        for i, character in enumerate(string):
            key = _CONTROL_CODES.get(character, character)
            try:
                self.press(key)
                self.release(key)

            except (ValueError, self.InvalidKeyException):
                raise self.InvalidCharacterException(i, character)

    @property
    @contextlib.contextmanager
    def modifiers(self):
        """The currently pressed modifier keys.

        Please note that this reflects only the internal state of this
        controller, and not the state of the operating system keyboard buffer.
        This property cannot be used to determine whether a key is physically
        pressed.

        Only the generic modifiers will be set; when pressing either
        :attr:`Key.shift_l`, :attr:`Key.shift_r` or :attr:`Key.shift`, only
        :attr:`Key.shift` will be present.

        Use this property within a context block thus::

            with controller.modifiers as modifiers:
                with_block()

        This ensures that the modifiers cannot be modified by another thread.
        """
        with self._modifiers_lock:
            yield set(
                self._as_modifier(modifier)
                for modifier in self._modifiers)

    @property
    def alt_pressed(self):
        """Whether any *alt* key is pressed.

        Please note that this reflects only the internal state of this
        controller. See :attr:`modifiers` for more information.
        """
        with self.modifiers as modifiers:
            return self._Key.alt in modifiers

    @property
    def alt_gr_pressed(self):
        """Whether *altgr* is pressed.

        Please note that this reflects only the internal state of this
        controller. See :attr:`modifiers` for more information.
        """
        with self.modifiers as modifiers:
            return self._Key.alt_gr in modifiers

    @property
    def ctrl_pressed(self):
        """Whether any *ctrl* key is pressed.

        Please note that this reflects only the internal state of this
        controller. See :attr:`modifiers` for more information.
        """
        with self.modifiers as modifiers:
            return self._Key.ctrl in modifiers

    @property
    def shift_pressed(self):
        """Whether any *shift* key is pressed, or *caps lock* is toggled.

        Please note that this reflects only the internal state of this
        controller. See :attr:`modifiers` for more information.
        """
        if self._caps_lock:
            return True

        with self.modifiers as modifiers:
            return self._Key.shift in modifiers

    def _resolve(self, key):
        """Resolves a key to a :class:`KeyCode` instance.

        This method will convert any key representing a character to uppercase
        if a shift modifier is active.

        :param key: The key to resolve.

        :return: a key code, or ``None`` if it cannot be resolved
        """
        # Use the value for the key constants
        if key in (k for k in self._Key):
            return key.value

        # Convert strings to key codes
        if isinstance(key, six.string_types):
            if len(key) != 1:
                raise ValueError(key)
            return self._KeyCode.from_char(key)

        # Assume this is a proper key
        if isinstance(key, self._KeyCode):
            if key.char is not None and self.shift_pressed:
                return self._KeyCode(vk=key.vk, char=key.char.upper())
            else:
                return key

    def _update_modifiers(self, key, is_press):
        """Updates the current modifier list.

        If ``key`` is not a modifier, no action is taken.

        :param key: The key being pressed or released.
        """
        # Check whether the key is a modifier
        if self._as_modifier(key):
            with self._modifiers_lock:
                if is_press:
                    self._modifiers.add(key)
                else:
                    try:
                        self._modifiers.remove(key)
                    except KeyError:
                        pass

    def _as_modifier(self, key):
        """Returns a key as the modifier used internally if defined.

        This method will convert values like :attr:`Key.alt_r.value` and
        :attr:`Key.shift_l.value` to :attr:`Key.alt` and :attr:`Key.shift`.

        :param key: The possible modifier key.

        :return: the base modifier key, or ``None`` if ``key`` is not a
            modifier
        """
        from . import _NORMAL_MODIFIERS
        return _NORMAL_MODIFIERS.get(key, None)

    def _handle(self, key, is_press):
        """The platform implementation of the actual emitting of keyboard
        events.

        This is a platform dependent implementation.

        :param Key key: The key to handle.

        :param bool is_press: Whether this is a key press event.
        """
        raise NotImplementedError()


# pylint: disable=W0223; This is also an abstract class
class Listener(AbstractListener):
    """A listener for keyboard events.

    Instances of this class can be used as context managers. This is equivalent
    to the following code::

        listener.start()
        try:
            listener.wait()
            with_statements()
        finally:
            listener.stop()

    This class inherits from :class:`threading.Thread` and supports all its
    methods. It will set :attr:`daemon` to ``True`` when created.

    All callback arguments are optional; a callback may take less arguments
    than actually passed, but not more, unless they are optional.

    :param callable on_press: The callback to call when a button is pressed.

        It will be called with the arguments ``(key, injected)``, where ``key``
        is a :class:`KeyCode`, a :class:`Key` or ``None`` if the key is
        unknown, and ``injected`` whether the event was injected and thus not
        generated by an actual input device.

        Please note that not all backends support ``injected`` and will always
        set it to ``False``.

    :param callable on_release: The callback to call when a button is released.

        It will be called with the arguments ``(key, injected)``, where ``key``
        is a :class:`KeyCode`, a :class:`Key` or ``None`` if the key is
        unknown, and ``injected`` whether the event was injected and thus not
        generated by an actual input device.

        Please note that not all backends support ``injected`` and will always
        set it to ``False``.

    :param bool suppress: Whether to suppress events. Setting this to ``True``
        will prevent the input events from being passed to the rest of the
        system.

    :param kwargs: Any non-standard platform dependent options. These should be
        prefixed with the platform name thus: ``darwin_``, ``uinput_``,
        ``xorg_`` or ``win32_``.

        Supported values are:

        ``darwin_intercept``
            A callable taking the arguments ``(event_type, event)``, where
            ``event_type`` is ``Quartz.kCGEventKeyDown`` or
            ``Quartz.kCGEventKeyUp``, and ``event`` is a ``CGEventRef``.

            This callable can freely modify the event using functions like
            ``Quartz.CGEventSetIntegerValueField``. If this callable does not
            return the event, the event is suppressed system wide.

        ``uinput_device_paths``
            A list of device paths.

            If this is specified, *pynput* will limit the number of devices
            checked for the capabilities needed to those passed, otherwise all
            system devices will be used. Passing this might be required if an
            incorrect device is chosen.

        ``win32_event_filter``
            A callable taking the arguments ``(msg, data)``, where ``msg`` is
            the current message, and ``data`` associated data as a
            `KBDLLHOOKSTRUCT <https://docs.microsoft.com/en-gb/windows/win32/api/winuser/ns-winuser-kbdllhookstruct>`_.

            If this callback returns ``False``, the event will not be
            propagated to the listener callback.

            If ``self.suppress_event()`` is called, the event is suppressed
            system wide.
    """
    def __init__(self, on_press=None, on_release=None, suppress=False,
                 **kwargs):
        self._log = _logger(self.__class__)
        option_prefix = prefix(Listener, self.__class__)
        self._options = {
            key[len(option_prefix):]: value
            for key, value in kwargs.items()
            if key.startswith(option_prefix)}
        super(Listener, self).__init__(
            on_press=self._wrap(on_press, 2),
            on_release=self._wrap(on_release, 2),
            suppress=suppress)
# pylint: enable=W0223

    def canonical(self, key):
        """Performs normalisation of a key.

        This method attempts to convert key events to their canonical form, so
        that events will equal regardless of modifier state.

        This method will convert upper case keys to lower case keys, convert
        any modifiers with a right and left version to the same value, and may
        slow perform additional platform dependent normalisation.

        :param key: The key to normalise.
        :type key: Key or KeyCode

        :return: a key
        :rtype: Key or KeyCode
        """
        from pynput.keyboard import Key, KeyCode, _NORMAL_MODIFIERS
        if isinstance(key, KeyCode) and key.char is not None:
            return KeyCode.from_char(key.char.lower())
        elif isinstance(key, Key) and key.value in _NORMAL_MODIFIERS:
            return _NORMAL_MODIFIERS[key.value]
        elif isinstance(key, Key) and key.value.vk is not None:
            return KeyCode.from_vk(key.value.vk)
        else:
            return key
