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
The keyboard implementation for *OSX*.
"""

# pylint: disable=C0111
# The documentation is extracted from the base classes

# pylint: disable=R0903
# We implement stubs

import enum

import Quartz

from pynput._util.darwin import (
    get_unicode_to_keycode_map,
    keycode_context,
    ListenerMixin)
from . import _base

'''
#https://gist.github.com/nevyn/764542/dc1f7117a656314accb4ae206f7483fc1513180b
#https://weblog.rogueamoeba.com/2007/09/29/apple-keyboard-media-key-event-handling/
#https://chromium.googlesource.com/experimental/chromium/src/+/refs/wip/bajones/
    webvr/chrome/browser/extensions/global_shortcut_listener_mac.mm
'''
kSystemDefinedEventMediaKeysSubtype = 8

#iokit hidsystem/ev_keymap.h
tKeyNameToCode = {
    'NX_NOSPECIALKEY': 0xFFFF,
    'NX_KEYTYPE_SOUND_UP': 0,
    'NX_KEYTYPE_SOUND_DOWN': 1,
    'NX_KEYTYPE_BRIGHTNESS_UP': 2,
    'NX_KEYTYPE_BRIGHTNESS_DOWN': 3,
    'NX_KEYTYPE_CAPS_LOCK': 4,
    'NX_KEYTYPE_HELP': 5,
    'NX_POWER_KEY': 6,
    'NX_KEYTYPE_MUTE': 7,
    'NX_UP_ARROW_KEY': 8,
    'NX_DOWN_ARROW_KEY': 9,
    'NX_KEYTYPE_NUM_LOCK': 10,
    'NX_KEYTYPE_CONTRAST_UP': 11,
    'NX_KEYTYPE_CONTRAST_DOWN': 12,
    'NX_KEYTYPE_LAUNCH_PANEL': 13,
    'NX_KEYTYPE_EJECT': 14,
    'NX_KEYTYPE_VIDMIRROR': 15,
    'NX_KEYTYPE_PLAY': 16,
    'NX_KEYTYPE_NEXT': 17,
    'NX_KEYTYPE_PREVIOUS': 18,
    'NX_KEYTYPE_FAST': 19,
    'NX_KEYTYPE_REWIND': 20,
    'NX_KEYTYPE_ILLUMINATION_UP': 21,
    'NX_KEYTYPE_ILLUMINATION_DOWN': 22,
    'NX_KEYTYPE_ILLUMINATION_TOGGLE': 23
}


class KeyCode(_base.KeyCode):
    _PLATFORM_EXTENSIONS = (
            # Whether this is a media key
            '_is_media',
    )

    def _event(self, modifiers, mapping, is_pressed):
        """This key as a *Quartz* event.

        :param set modifiers: The currently active modifiers.

        :param mapping: The current keyboard mapping.

        :param bool is_press: Whether to generate a press event.

        :return: a *Quartz* event
        """
        vk = self.vk or mapping.get(self.char)
        if self._is_media:
            result = getattr(
                    Quartz.NSEvent,
                    'otherEventWithType_'
                    'location_'
                    'modifierFlags_'
                    'timestamp_'
                    'windowNumber_'
                    'context_'
                    'subtype_'
                    'data1_'
                    'data2_')(
                Quartz.NSSystemDefined,
                (0, 0),
                0xa00 if is_pressed else 0xb00,
                0,
                0,
                0,
                8,
                (self.vk << 16) | ((0xa if is_pressed else 0xb) << 8),
                -1)
            result = result.CGEvent()
        else:
            result = Quartz.CGEventCreateKeyboardEvent(
                None, 0 if vk is None else vk, is_pressed)

        Quartz.CGEventSetFlags(
            result,
            0
            | (Quartz.kCGEventFlagMaskAlternate
               if Key.alt in modifiers else 0)

            | (Quartz.kCGEventFlagMaskCommand
               if Key.cmd in modifiers else 0)

            | (Quartz.kCGEventFlagMaskControl
               if Key.ctrl in modifiers else 0)

            | (Quartz.kCGEventFlagMaskShift
               if Key.shift in modifiers else 0))

        if vk is None and self.char is not None:
            Quartz.CGEventKeyboardSetUnicodeString(
                result, len(self.char), self.char)

        return result


class Key(enum.Enum):
    # Default keys
    alt = KeyCode.from_vk(0x3A)
    alt_l = KeyCode.from_vk(0x3A)
    alt_r = KeyCode.from_vk(0x3D)
    alt_gr = KeyCode.from_vk(0x3D)
    backspace = KeyCode.from_vk(0x33)
    caps_lock = KeyCode.from_vk(0x39)
    cmd = KeyCode.from_vk(0x37)
    cmd_l = KeyCode.from_vk(0x37)
    cmd_r = KeyCode.from_vk(0x36)
    ctrl = KeyCode.from_vk(0x3B)
    ctrl_l = KeyCode.from_vk(0x3B)
    ctrl_r = KeyCode.from_vk(0x3E)
    delete = KeyCode.from_vk(0x75)
    down = KeyCode.from_vk(0x7D)
    end = KeyCode.from_vk(0x77)
    enter = KeyCode.from_vk(0x24)
    esc = KeyCode.from_vk(0x35)
    f1 = KeyCode.from_vk(0x7A)
    f2 = KeyCode.from_vk(0x78)
    f3 = KeyCode.from_vk(0x63)
    f4 = KeyCode.from_vk(0x76)
    f5 = KeyCode.from_vk(0x60)
    f6 = KeyCode.from_vk(0x61)
    f7 = KeyCode.from_vk(0x62)
    f8 = KeyCode.from_vk(0x64)
    f9 = KeyCode.from_vk(0x65)
    f10 = KeyCode.from_vk(0x6D)
    f11 = KeyCode.from_vk(0x67)
    f12 = KeyCode.from_vk(0x6F)
    f13 = KeyCode.from_vk(0x69)
    f14 = KeyCode.from_vk(0x6B)
    f15 = KeyCode.from_vk(0x71)
    f16 = KeyCode.from_vk(0x6A)
    f17 = KeyCode.from_vk(0x40)
    f18 = KeyCode.from_vk(0x4F)
    f19 = KeyCode.from_vk(0x50)
    f20 = KeyCode.from_vk(0x5A)
    home = KeyCode.from_vk(0x73)
    left = KeyCode.from_vk(0x7B)
    page_down = KeyCode.from_vk(0x79)
    page_up = KeyCode.from_vk(0x74)
    right = KeyCode.from_vk(0x7C)
    shift = KeyCode.from_vk(0x38)
    shift_l = KeyCode.from_vk(0x38)
    shift_r = KeyCode.from_vk(0x3C)
    space = KeyCode.from_vk(0x31, char=' ')
    tab = KeyCode.from_vk(0x30)
    up = KeyCode.from_vk(0x7E)

    media_play_pause = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_PLAY'], _is_media=True)
    media_volume_mute = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_MUTE'], _is_media=True)
    media_volume_down = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_SOUND_DOWN'], _is_media=True)
    media_volume_up = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_SOUND_UP'], _is_media=True)
    media_previous = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_PREVIOUS'], _is_media=True)
    media_next = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_NEXT'], _is_media=True)
    media_brightness_up = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_BRIGHTNESS_UP'], _is_media=True)
    media_brightness_down = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_BRIGHTNESS_DOWN'], _is_media=True)
    #media_caps_lock = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_CAPS_LOCK'], _is_media=True)
    media_help = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_HELP'], _is_media=True)
    media_power_ley = KeyCode.from_vk(tKeyNameToCode['NX_POWER_KEY'], _is_media=True)
    media_arrow_up = KeyCode.from_vk(tKeyNameToCode['NX_UP_ARROW_KEY'], _is_media=True)
    media_arrow_down = KeyCode.from_vk(tKeyNameToCode['NX_DOWN_ARROW_KEY'], _is_media=True)
    media_num_lock = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_NUM_LOCK'], _is_media=True)
    media_contrast_up = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_CONTRAST_UP'], _is_media=True)
    media_contrast_down = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_CONTRAST_DOWN'], _is_media=True)
    media_launch_panel = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_LAUNCH_PANEL'], _is_media=True)
    media_eject = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_EJECT'], _is_media=True)
    media_vidmirror = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_VIDMIRROR'], _is_media=True)
    media_fast = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_FAST'], _is_media=True)
    media_rewind = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_REWIND'], _is_media=True)
    media_illumination_up = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_ILLUMINATION_UP'], _is_media=True)
    media_illumination_down = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_ILLUMINATION_DOWN'], _is_media=True)
    media_illumination_toggle = KeyCode.from_vk(tKeyNameToCode['NX_KEYTYPE_ILLUMINATION_TOGGLE'], _is_media=True)


class Controller(_base.Controller):
    _KeyCode = KeyCode
    _Key = Key

    def __init__(self):
        super(Controller, self).__init__()
        self._mapping = get_unicode_to_keycode_map()

    def _handle(self, key, is_press):
        with self.modifiers as modifiers:
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                (key if key not in (k for k in Key) else key.value)._event(
                    modifiers, self._mapping, is_press))


class Listener(ListenerMixin, _base.Listener):
    #: The events that we listen to
    _EVENTS = (
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp) |
        Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged) |
        Quartz.CGEventMaskBit(Quartz.NSSystemDefined)
    )

    #: A mapping from keysym to special key
    _SPECIAL_KEYS = {
        (key.value.vk, key.value._is_media): key
        for key in Key}

    #: The event flags set for the various modifier keys
    _MODIFIER_FLAGS = {
        Key.alt: Quartz.kCGEventFlagMaskAlternate,
        Key.alt_l: Quartz.kCGEventFlagMaskAlternate,
        Key.alt_r: Quartz.kCGEventFlagMaskAlternate,
        Key.cmd: Quartz.kCGEventFlagMaskCommand,
        Key.cmd_l: Quartz.kCGEventFlagMaskCommand,
        Key.cmd_r: Quartz.kCGEventFlagMaskCommand,
        Key.ctrl: Quartz.kCGEventFlagMaskControl,
        Key.ctrl_l: Quartz.kCGEventFlagMaskControl,
        Key.ctrl_r: Quartz.kCGEventFlagMaskControl,
        Key.shift: Quartz.kCGEventFlagMaskShift,
        Key.shift_l: Quartz.kCGEventFlagMaskShift,
        Key.shift_r: Quartz.kCGEventFlagMaskShift}

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self._flags = 0
        self._context = None
        self._intercept = self._options.get(
            'intercept',
            None)

    def _run(self):
        with keycode_context() as context:
            self._context = context
            try:
                super(Listener, self)._run()
            finally:
                self._context = None

    def _handle(self, dummy_proxy, event_type, event, dummy_refcon):
        # Convert the event to a KeyCode; this may fail, and in that case we
        # pass None
        try:
            key = self._event_to_key(event)
        except IndexError:
            key = None

        try:
            if event_type == Quartz.kCGEventKeyDown:
                # This is a normal key press
                self.on_press(key)

            elif event_type == Quartz.kCGEventKeyUp:
                # This is a normal key release
                self.on_release(key)

            elif key == Key.caps_lock:
                # We only get an event when caps lock is toggled, so we fake
                # press and release
                self.on_press(key)
                self.on_release(key)
            
            elif event_type == Quartz.NSSystemDefined: #sys key, we can't trust _event_to_key
                sysEvent = Quartz.NSEvent.eventWithCGEvent_(event)
                is_media = True if sysEvent.subtype() == kSystemDefinedEventMediaKeysSubtype else False
                if( is_media ):
                    keyCode = (( sysEvent.data1() & 0xFFFF0000) >> 16);
                    key = (keyCode, is_media)
                    if key in self._SPECIAL_KEYS:
                        key = self._SPECIAL_KEYS[ key ]
                        keyFlags = ( sysEvent.data1() & 0x0000FFFF);
                        #keyRepeat = (keyFlags & 0x1);
                        is_press = (((keyFlags & 0xFF00) >> 8)) == 0xA;
                        if is_press:
                            self.on_press(key)
                        else:
                            self.on_release(key)

            else:
                # This is a modifier event---excluding caps lock---for which we
                # must check the current modifier state to determine whether
                # the key was pressed or released
                flags = Quartz.CGEventGetFlags(event)
                is_press = flags & self._MODIFIER_FLAGS.get(key, 0)
                if is_press:
                    self.on_press(key)
                else:
                    self.on_release(key)

        finally:
            # Store the current flag mask to be able to detect modifier state
            # changes
            self._flags = Quartz.CGEventGetFlags(event)

    def _event_to_key(self, event):
        """Converts a *Quartz* event to a :class:`KeyCode`.

        :param event: The event to convert.

        :return: a :class:`pynput.keyboard.KeyCode`

        :raises IndexError: if the key code is invalid
        """
        vk = Quartz.CGEventGetIntegerValueField(
            event, Quartz.kCGKeyboardEventKeycode)
        event_type = Quartz.CGEventGetType(event)
        is_media = True if event_type == Quartz.NSSystemDefined else None

        # First try special keys...
        key = (vk, is_media)
        if key in self._SPECIAL_KEYS:
            return self._SPECIAL_KEYS[key]

        # ...then try characters...
        length, chars = Quartz.CGEventKeyboardGetUnicodeString(
            event, 100, None, None)
        if length > 0:
            return KeyCode.from_char(chars, vk=vk)

        # ...and fall back on a virtual key code
        return KeyCode.from_vk(vk)
