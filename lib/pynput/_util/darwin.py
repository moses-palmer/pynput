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

import contextlib
import ctypes
import ctypes.util
import six

import objc
import CoreFoundation


#: The objc module as a library handle
_objc = ctypes.PyDLL(objc._objc.__file__)

_objc.PyObjCObject_New.restype = ctypes.py_object
_objc.PyObjCObject_New.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]


def _wrap_value(value):
    """Converts a pointer to a *Python objc* value.

    :param value: The pointer to convert.

    :return: a wrapped value
    """
    return _objc.PyObjCObject_New(value, 0, 1)


@contextlib.contextmanager
def _wrapped(value):
    """A context manager that converts a raw pointer to a *Python objc* value.

    When the block is exited, the value is released.

    :param value: The raw value to wrap.
    """
    wrapped_value = _wrap_value(value)

    try:
        yield value
    finally:
        CoreFoundation.CFRelease(wrapped_value)


class CarbonExtra(object):
    """A class exposing some missing functionality from *Carbon* as class
    attributes.
    """
    _Carbon = ctypes.cdll.LoadLibrary(ctypes.util.find_library('Carbon'))

    _Carbon.TISCopyCurrentKeyboardInputSource.argtypes = []
    _Carbon.TISCopyCurrentKeyboardInputSource.restype = ctypes.c_void_p

    _Carbon.TISGetInputSourceProperty.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p]
    _Carbon.TISGetInputSourceProperty.restype = ctypes.c_void_p

    _Carbon.LMGetKbdType.argtypes = []
    _Carbon.LMGetKbdType.restype = ctypes.c_uint32

    _Carbon.UCKeyTranslate.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint16,
        ctypes.c_uint16,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint8,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_uint16 * 4]
    _Carbon.UCKeyTranslate.restype = ctypes.c_uint32

    TISCopyCurrentKeyboardInputSource = \
        _Carbon.TISCopyCurrentKeyboardInputSource

    kTISPropertyUnicodeKeyLayoutData = ctypes.c_void_p.in_dll(
        _Carbon, 'kTISPropertyUnicodeKeyLayoutData')

    TISGetInputSourceProperty = \
        _Carbon.TISGetInputSourceProperty

    LMGetKbdType = \
        _Carbon.LMGetKbdType

    kUCKeyActionDisplay = 3
    kUCKeyTranslateNoDeadKeysBit = 0

    UCKeyTranslate = \
        _Carbon.UCKeyTranslate


def get_unicode_to_keycode_map():
    LENGTH = 4

    with _wrapped(CarbonExtra.TISCopyCurrentKeyboardInputSource()) as keyboard:
        keyboard_type = CarbonExtra.LMGetKbdType()
        layout = _wrap_value(CarbonExtra.TISGetInputSourceProperty(
                keyboard,
                CarbonExtra.kTISPropertyUnicodeKeyLayoutData))
        data = layout.bytes().tobytes()

        def keycode_to_string(keycode):
            dead_key_state = ctypes.c_uint32()
            length = ctypes.c_uint8()
            unicode_string = (ctypes.c_uint16 * LENGTH)()
            CarbonExtra.UCKeyTranslate(
                data,
                keycode,
                CarbonExtra.kUCKeyActionDisplay,
                0,
                keyboard_type,
                CarbonExtra.kUCKeyTranslateNoDeadKeysBit,
                ctypes.byref(dead_key_state),
                LENGTH,
                ctypes.byref(length),
                unicode_string)
            return u''.join(
                six.unichr(unicode_string[i])
                for i in range(length.value))

        return {
            keycode_to_string(keycode): keycode
            for keycode in range(128)}
