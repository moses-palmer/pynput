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
import Quartz
import threading

from AppKit import NSEvent, NSScreen

from . import _base


def _button_value(base_name, mouse_button):
    """Generates the value tuple for a :class:`Controller.Button` value.

    :param str base_name: The base name for the button. This shuld be a string
        like ``'kCGEventLeftMouse'``.

    :param int mouse_button: The mouse button ID.

    :return: a value tuple
    """
    return (
        tuple(
            getattr(Quartz, '%sMouse%s' % (base_name, name))
            for name in ('Down', 'Up', 'Dragged')),
        mouse_button)


class Controller(_base.Controller):
    class Button(enum.Enum):
        """The various buttons.
        """
        left = _button_value('kCGEventLeft', 0)
        middle = _button_value('kCGEventOther', 2)
        right = _button_value('kCGEventRight', 1)

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self._click = None
        self._drag_button = None

    def _position_get(self):
        pos = NSEvent.mouseLocation()

        return pos.x, Quartz.CGDisplayPixelsHigh(0) - pos.y

    def _position_set(self, pos):
        try:
            (_, _, mouse_type), mouse_button = self._drag_button
        except TypeError:
            mouse_type = Quartz.kCGEventMouseMoved
            mouse_button = 0

        Quartz.CGEventPost(
            Quartz.kCGHIDEventTap,
            Quartz.CGEventCreateMouseEvent(
                None,
                mouse_type,
                pos,
                mouse_button))

    def _scroll(self, dx, dy):
        while dx != 0 or dy != 0:
            xval = 1 if dx > 0 else -1 if dx < 0 else 0
            dx -= xval
            yval = 1 if dy > 0 else -1 if dy < 0 else 0
            dy -= yval

            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                Quartz.CGEventCreateScrollWheelEvent(
                    None,
                    Quartz.kCGScrollEventUnitPixel,
                    2,
                    yval * 1,
                    xval * 1))

    def _press(self, button):
        (press, release, drag), mouse_button = button.value
        event = Quartz.CGEventCreateMouseEvent(
            None,
            press,
            self.position,
            mouse_button)

        # If we are performing a click, we need to set this state flag
        if self._click is not None:
            self._click += 1
            Quartz.CGEventSetIntegerValueField(
                event,
                Quartz.kCGMouseEventClickState,
                self._click)

        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

        # Store the button to enable dragging
        self._drag_button = button

    def _release(self, button):
        (press, release, drag), mouse_button = button.value
        event = Quartz.CGEventCreateMouseEvent(
            None,
            release,
            self.position,
            mouse_button)

        # If we are performing a click, we need to set this state flag
        if self._click is not None:
            Quartz.CGEventSetIntegerValueField(
                event,
                Quartz.kCGMouseEventClickState,
                self._click)

        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

        if button == self._drag_button:
            self._drag_button = None

    def __enter__(self):
        self._click = 0
        return self

    def __exit__(self, type, value, traceback):
        self._click = None


class Listener(_base.Listener):
    #: The events that we listen to
    _TAP_EVENTS = (
        0
        | Quartz.CGEventMaskBit(Quartz.kCGEventMouseMoved)
        | Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDown)
        | Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseUp)
        | Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseDown)
        | Quartz.CGEventMaskBit(Quartz.kCGEventRightMouseUp)
        | Quartz.CGEventMaskBit(Quartz.kCGEventOtherMouseDown)
        | Quartz.CGEventMaskBit(Quartz.kCGEventOtherMouseUp)
        | Quartz.CGEventMaskBit(Quartz.kCGEventScrollWheel))

    def __init__(self, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)

        self._loop = None

    def _run(self):
        try:
            tap = Quartz.CGEventTapCreate(
                Quartz.kCGSessionEventTap,
                Quartz.kCGHeadInsertEventTap,
                Quartz.kCGEventTapOptionDefault,
                self._TAP_EVENTS,
                self._handler,
                None)

            loop_source = Quartz.CFMachPortCreateRunLoopSource(
                None, tap, 0)
            self._loop = Quartz.CFRunLoopGetCurrent()

            Quartz.CFRunLoopAddSource(
                self._loop, loop_source, Quartz.kCFRunLoopDefaultMode)
            Quartz.CGEventTapEnable(tap, True)

            while True:
                result = Quartz.CFRunLoopRunInMode(
                    Quartz.kCFRunLoopDefaultMode, 1, False)
                if result != Quartz.kCFRunLoopRunTimedOut:
                    break

        finally:
            self._loop = None

    def _stop(self):
        # The base class sets the running flag to False; this will cause the
        # loop around run loop invocations to terminate and set this event
        Quartz.CFRunLoopStop(self._loop)

    @_base.Listener._emitter
    def _handler(self, proxy, event_type, event, refcon):
        """The callback registered with *Mac OSX* for mouse events.

        This method will call the callbacks registered on initialisation.
        """
        (x, y) = Quartz.CGEventGetLocation(event)

        try:
            # Quickly detect the most common event type
            if event_type == Quartz.kCGEventMouseMoved:
                self.on_move(x, y)

            elif event_type == Quartz.kCGEventScrollWheel:
                dx = Quartz.CGEventGetIntegerValueField(
                    event,
                    Quartz.kCGScrollWheelEventDeltaAxis2)
                dy = Quartz.CGEventGetIntegerValueField(
                    event,
                    Quartz.kCGScrollWheelEventDeltaAxis1)
                self.on_scroll(x, y, dx, dy)

            else:
                for button in Controller.Button:
                    (press, release, drag), mouse_button = button.value

                    # Press and release generate click events, and drag
                    # generates move events
                    if event_type in (press, release):
                        self.on_click(x, y, button, event_type == press)
                    elif event_type == drag:
                        self.on_move(x, y)

        except self.StopException:
            self.stop()

        return event
