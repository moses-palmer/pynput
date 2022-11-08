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

import contextlib
import six
import six.moves.queue as queue
import time
import threading

import pynput.keyboard

from . import EventTest, darwin, win32, xorg

from six.moves import input


class KeyboardListenerTest(EventTest):
    NOTIFICATION = (
        'This test case is interactive, so you must follow the instructions '
        'on screen')
    LISTENER_CLASS = pynput.keyboard.Listener

    @contextlib.contextmanager
    def events(self, timeout=5.0):
        """A context manager that yields keyboard events.

        The context object is a generator that yields the actual events. An
        event is the tuple ``(key, pressed)``.

        The generator is stopped whenever the timeout is triggered. If this
        happens, ``None`` will be yielded as the last event.

        :param timeout: The number of seconds to wait for a key event.
        """
        def generator(q):
            while True:
                try:
                    yield q.get(timeout=timeout)
                except queue.Empty:
                    yield None
                    break

        # Yield the generator and allow the client to capture events
        q = queue.Queue()
        with self.listener(
                on_press=lambda k: q.put((k, True)),
                on_release=lambda k: q.put((k, False))):
            yield generator(q)

    def assert_keys(self, failure_message, *args):
        """Asserts that the list of key events is emitted.

        :param str failure_message: The message to display upon failure.

        :param expected: A sequence of the tuple ``(key, pressed)``, where
            ``key`` is the key and ``pressed`` whether it was pressed.

            ``key`` may be either a string, a :class:`~pynput.keyboard.Key` or
            a :class:`~pynput.keyboard.KeyCode`.

            The tuple may only be a tuple of tuples, in which case any of the
            values will be accepted.
        """
        def normalize(event):
            if not isinstance(event[0], tuple):
                return normalize(((event[0],), event[1]))
            key, is_pressed = event
            return (
                tuple(
                    pynput.keyboard.KeyCode.from_char(key)
                    if isinstance(key, six.string_types)
                    else key.value if key in pynput.keyboard.Key
                    else key
                    for key in event[0]),
                is_pressed)

        original_expected = [normalize(arg) for arg in args]
        remaining = list(original_expected)

        time.sleep(1)

        actual = []
        try:
            with self.events() as events:
                for event in events:
                    if event is None:
                        break

                    expected = remaining.pop(0)
                    current = normalize(event)
                    actual.append(current)
                    self.assertIn(
                        current[0][0],
                        expected[0],
                        '%s was not found in %s' % (
                            expected[0],
                            current[0][0]))
                    self.assertEqual(
                        current[1],
                        expected[1],
                        'Pressed state for %s was incorrect' % (
                            str(current[0][0])))

                    if not remaining:
                        break

            # Ensure that no keys remain
            self.assertSequenceEqual(
                [],
                remaining,
                '%s ([%s] != [%s])' % (
                    failure_message,
                    ' '.join(str(e) for e in original_expected),
                    ' '.join(str(a) for a in actual)))

        finally:
            self.notify('Press <enter> to continue...', delay=0)
            result = input()
            time.sleep(1)
            return result

    def string_to_events(self, s):
        """Yields all events necessary to type a string.

        :param str s: The string.
        """
        for c in s:
            yield (c, True)
            yield (c, False)

    def test_tap(self):
        """Tests that a single key can be tapped"""
        self.notify('Press and release "a"')
        self.assert_keys(
            'Failed to register event',
            ('a', True), ('a', False))

    def test_enter(self):
        """Tests that the enter key can be tapped"""
        self.notify('Press <enter>')
        self.assert_keys(
            'Failed to register event',
            (pynput.keyboard.Key.enter, True))

    def test_modifier(self):
        """Tests that the modifier keys can be tapped"""
        from pynput.keyboard import Key
        for key in (
                (Key.alt, Key.alt_l, Key.alt_r),
                (Key.ctrl, Key.ctrl_l, Key.ctrl_r),
                (Key.shift, Key.shift_l, Key.shift_r)):
            self.notify('Press <%s>' % key[0].name)
            self.assert_keys(
                'Failed to register event',
                (key, True))

    def test_order(self):
        """Tests that the order of key events is correct"""
        self.notify('Type "hello world"')
        self.assert_keys(
            'Failed to register event',
            *tuple(self.string_to_events('hello world')))

    def test_shift(self):
        """Tests that <shift> yields capital letters"""
        self.notify('Type "TEST" with <shift> pressed')
        self.assert_keys(
            'Failed to register event',
            (
                (
                    pynput.keyboard.Key.shift,
                    pynput.keyboard.Key.shift_l,
                    pynput.keyboard.Key.shift_r),
                True),
            *tuple(self.string_to_events('TEST')))

    def test_modifier_and_normal(self):
        """Tests that the modifier keys do not stick"""
        from pynput.keyboard import Key
        self.notify('Press a, <ctrl>, a')
        self.assert_keys(
            'Failed to register event',
            ('a', True),
            ('a', False),
            ((Key.ctrl, Key.ctrl_l, Key.ctrl_r), True),
            ((Key.ctrl, Key.ctrl_l, Key.ctrl_r), False),
            ('a', True),
            ('a', False))

    def test_suppress(self):
        """Tests that passing ``suppress`` prevents events from propagating"""
        self.suppress = True
        self.notify('Type "hello world"')
        self.assertEqual(
            '',
            self.assert_keys(
                'Failed to register event',
                *tuple(self.string_to_events('hello world'))).strip())

    def test_reraise(self):
        """Tests that exception are reraised"""
        class MyException(Exception): pass

        def on_press(key):
            raise MyException()

        with self.assertRaises(MyException):
            with pynput.keyboard.Listener(
                    on_press=on_press) as l:
                self.notify('Press any key')
                l.join()

    def test_stop(self):
        """Tests that stop works from a separate thread"""
        self.notify('Do not touch the keyboard')

        with pynput.keyboard.Listener() as l:
            def runner():
                time.sleep(1)
                l.stop()

            threading.Thread(target=runner).start()
            l.join(2.0)
            self.assertFalse(
                l.is_alive(),
                'Listener did not stop')

    @darwin
    def test_options_darwin(self):
        """Tests that options are correctly set on OSX"""
        self.assertTrue(
            pynput.keyboard.Listener(
                darwin_test=True,
                win32_test=False,
                xorg_test=False)._options['test'])

    @win32
    def test_options_win32(self):
        """Tests that options are correctly set on Windows"""
        self.assertTrue(
            pynput.keyboard.Listener(
                darwin_test=False,
                win32_test=True,
                xorg_test=False)._options['test'])

    @xorg
    def test_options_xorg(self):
        """Tests that options are correctly set on Linux"""
        self.assertTrue(
            pynput.keyboard.Listener(
                darwin_test=False,
                win32_test=False,
                xorg_test=True)._options['test'])

    def test_events(self):
        """Tests that events are correctly yielded"""
        from pynput.keyboard import Key, KeyCode, Events
        self.notify('Press a, b, a, <esc>')

        with Events() as events:
            result = []
            for event in events:
                if event.key == Key.esc:
                    break
                else:
                    result.append(event)

        self.assertSequenceEqual(
            result,
            [
                Events.Press(KeyCode.from_char('a')),
                Events.Release(KeyCode.from_char('a')),
                Events.Press(KeyCode.from_char('b')),
                Events.Release(KeyCode.from_char('b')),
                Events.Press(KeyCode.from_char('a')),
                Events.Release(KeyCode.from_char('a')),
            ])

        self.notify('Do not touch the keyboard', delay=2.0)
        with Events() as events:
            self.assertIsNone(events.get(1.0))
