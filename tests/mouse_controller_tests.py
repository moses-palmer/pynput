# coding=utf-8
# pystray
# Copyright (C) 2015-2022 Moses Palmér
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

import numbers
import pynput.mouse
import time

from . import EventTest


class MouseControllerTest(EventTest):
    NOTIFICATION = (
        'This test case is non-interactive, so you must not use the mouse.\n'
        'You may need to keep the mouse pointer away from this window to '
        'avoid interference.')
    CONTROLLER_CLASS = pynput.mouse.Controller
    LISTENER_CLASS = pynput.mouse.Listener

    def assert_movement(self, failure_message, d):
        """Asserts that movement results in corresponding change of pointer
        position.

        :param str failure_message: The message to display upon failure.

        :param tuple d: The movement vector.
        """
        pos = self.controller.position
        self.controller.move(*d)
        time.sleep(1)
        self.assertEqual(
            self.controller.position,
            tuple(o + n for o, n in zip(pos, d)),
            failure_message)

    def test_buttons(self):
        """Asserts that all buttons defined for the base mouse interface are
        defined for the current platform"""
        from pynput.mouse._base import Button
        for button in Button:
            self.assertTrue(
                hasattr(pynput.mouse.Button, button.name),
                '%s is not defined for the current platform' % button.name)

    def test_position_get(self):
        """Tests that reading the position returns consistent values"""
        position = self.controller.position

        self.assertTrue(
            all(isinstance(i, numbers.Number) for i in position),
            'Not all coordinates in %s are numbers' % str(position))

        self.assertEqual(
            position,
            self.controller.position,
            'Second read of position returned different value')

    def test_position_set(self):
        """Tests that writing the position updates the position value"""
        position = self.controller.position
        new_position = tuple(i + 1 for i in position)

        self.controller.position = new_position
        time.sleep(1)

        self.assertEqual(
            new_position,
            self.controller.position,
            'Updating position failed')

    def test_position_set_float(self):
        """Tests that writing a floating point position does not crash"""
        position = self.controller.position
        new_position = tuple(i + 1.5 for i in position)

        self.controller.position = new_position

    def test_press(self):
        """Tests that press works"""
        for b in (
                pynput.mouse.Button.left,
                pynput.mouse.Button.right):
            with self.assert_event(
                    'Failed to send press event',
                    on_click=lambda x, y, button, pressed:
                    button == b and pressed):
                self.controller.press(b)
            self.controller.release(b)

    def test_release(self):
        """Tests that release works"""
        for b in (
                pynput.mouse.Button.left,
                pynput.mouse.Button.right):
            self.controller.press(b)
            with self.assert_event(
                    'Failed to send release event',
                    on_click=lambda x, y, button, pressed:
                    button == b and not pressed):
                self.controller.release(b)

    def test_left(self):
        """Tests that moving left works"""
        ox, oy = self.controller.position
        with self.assert_event(
                'Failed to send move left event',
                on_move=lambda x, y: x < ox):
            self.assert_movement(
                'Pointer did not move',
                (-1, 0))

    def test_right(self):
        """Tests that moving right works"""
        ox, oy = self.controller.position
        with self.assert_event(
                'Failed to send move right event',
                on_move=lambda x, y: x > ox):
            self.assert_movement(
                'Pointer did not move',
                (1, 0))

    def test_up(self):
        """Tests that moving up works"""
        ox, oy = self.controller.position
        with self.assert_event(
                'Failed to send move up event',
                on_move=lambda x, y: y < oy):
            self.assert_movement(
                'Pointer did not move',
                (0, -1))

    def test_down(self):
        """Tests that moving down works"""
        ox, oy = self.controller.position
        with self.assert_event(
                'Failed to send move down event',
                on_move=lambda x, y: y > oy):
            self.assert_movement(
                'Pointer did not move',
                (0, 1))

    def test_click(self):
        """Tests that click works"""
        for b in (
                pynput.mouse.Button.left,
                pynput.mouse.Button.right):
            events = [True, False]
            events.reverse()

            def on_click(x, y, button, pressed):
                if button == b:
                    self.assertEqual(
                        pressed,
                        events.pop(),
                        'Unexpected event')
                return len(events) == 0

            with self.assert_event(
                    'Failed to send click events',
                    on_click=on_click):
                self.controller.click(b)

    def test_scroll_up(self):
        """Tests that scrolling up works"""
        with self.assert_event(
                'Failed to send scroll up event',
                on_scroll=lambda x, y, dx, dy: dy > 0):
            self.controller.scroll(0, 1)

    def test_scroll_down(self):
        """Tests that scrolling down works"""
        with self.assert_event(
                'Failed to send scroll down event',
                on_scroll=lambda x, y, dx, dy: dy < 0):
            self.controller.scroll(0, -1)
