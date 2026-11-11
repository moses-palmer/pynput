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
Utility functions and classes for the *libei* backend.

This is the *Wayland* counterpart to the *Xorg* backend. Under *Wayland* a
client cannot reach the input stack directly: ``XTEST`` exists only inside
``Xwayland``, so events injected through it are invisible to native clients,
and ``uinput`` requires write access to ``/dev/uinput``, which a stock system
grants only to *root*.

The remaining route is the compositor itself, reached in two steps:

1. ``org.freedesktop.portal.RemoteDesktop`` is used to ask the user for
   permission. The compositor owns the dialog, and ``persist_mode`` together
   with ``restore_token`` makes the grant survive across runs, so the user is
   asked once rather than on every script.

2. ``ConnectToEIS`` on the granted session returns a file descriptor speaking
   the *EI* protocol, and the events themselves go over that, through *libei*.

The portal also exposes ``NotifyPointerMotionAbsolute`` and friends, which
look like the simpler route and are not used here: measured against the same
harness they lost about one button event in ten, where the *libei* transport
lost none. *libei* has an explicit emulation session and groups events into
frames, so the compositor can tell where one logical input report ends;
``Notify*`` has no equivalent and appears to coalesce a press and release that
arrive together. *libei* is also cheaper per event, and carries its own
coordinate regions, so no screen cast stream is needed and the user is not
asked for permission to see the screen.

Both the mouse and the keyboard backend share a single session, since
``SelectDevices`` grants pointer and keyboard together and two sessions would
ask the user twice for the same permission.
"""

# pylint: disable=R0903
# We implement minimal mixins

import errno
import json
import os
import threading
import time


def is_wayland():
    """Returns whether this appears to be a *Wayland* session.

    This backend reaches native *Wayland* clients, which the *Xorg* backend
    cannot, but it has nothing to offer a real *X* session: there the
    ``RemoteDesktop`` portal is usually absent, and ``XTEST`` reaches
    everything in any case.

    :return: whether to prefer this backend
    """
    return bool(os.environ.get('WAYLAND_DISPLAY')) \
        or os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland'


# Checked before the imports below, so that an X session is told it is an X
# session rather than told which package it is missing
if not is_wayland():
    raise ImportError(
        'the libei backend is only useful under Wayland; under X the xorg '
        'backend reaches every client')

try:
    from jeepney import DBusAddress, MatchRule, message_bus, new_method_call
    from jeepney.io.blocking import Proxy, open_dbus_connection
except ImportError as e:
    raise ImportError(
        'the package jeepney is required for the libei backend: ' + str(e))

try:
    # Not only ImportError: the bindings raise LibraryNotFoundError when the
    # system libei is missing, which is an ordinary way for this backend to be
    # unavailable
    from libei import ei
except Exception as e:  # pylint: disable=W0703
    raise ImportError(
        'the package python-libei and the system library libei are required '
        'for the libei backend: ' + str(e))


#: The bus name of the desktop portal
BUS_NAME = 'org.freedesktop.portal.Desktop'

#: The object path of the desktop portal
OBJECT_PATH = '/org/freedesktop/portal/desktop'

#: The interface used to request permission to inject input
INTERFACE = 'org.freedesktop.portal.RemoteDesktop'

#: The device types passed to ``SelectDevices``
DEVICE_KEYBOARD = 1
DEVICE_POINTER = 2

#: The ``persist_mode`` keeping a grant until the user revokes it
PERSIST_UNTIL_REVOKED = 2

#: The number of seconds to wait for *libei* to hand us our devices
DEVICE_TIMEOUT = 10.0

#: The number of seconds to wait for the user to answer the portal dialog
DIALOG_TIMEOUT = 300.0

#: The value of one scroll detent.
#:
#: *libei* counts discrete scrolling in 120ths of a detent, following the
#: high resolution scroll wheel convention, and warns when passed a value
#: smaller than this.
SCROLL_DETENT = 120

#: The offset between an *XKB* keycode and the *evdev* keycode for the same
#: physical key.
#:
#: *XKB* inherits the *X11* convention of reserving the first eight codes;
#: *libei*, like the kernel, does not.
XKB_KEYCODE_OFFSET = 8

#: The environment variable overriding where the portal restore token is kept.
#:
#: Setting this to an empty value stops the token being stored at all, at the
#: cost of the user being asked for permission on every run.
TOKEN_PATH_VARIABLE = 'PYNPUT_LIBEI_RESTORE_TOKEN'


def token_path():
    """Returns the path of the file in which to keep the portal restore token.

    :return: a path, or ``None`` if the token should not be stored
    """
    override = os.environ.get(TOKEN_PATH_VARIABLE)
    if override is not None:
        return override or None
    return os.path.join(
        os.environ.get('XDG_DATA_HOME')
        or os.path.join(os.path.expanduser('~'), '.local', 'share'),
        'pynput',
        'libei-restore-token')


class Session(object):
    """A single ``RemoteDesktop`` grant, shared by all controllers.

    The session is created lazily: merely importing *pynput* must not raise a
    permission dialog, so the user is asked the first time something is
    actually injected.
    """

    class Error(Exception):
        """The exception raised when a session cannot be established."""

    def __init__(self):
        self._lock = threading.RLock()
        self._connection = None
        self._session_handle = None
        self._context = None
        self._pointer = None
        self._pointer_relative = None
        self._keyboard = None
        self._keymap = None
        self._bounds = None
        self._started = False
        self._failure = None
        self._tokens = 0

    @property
    def bounds(self):
        """The area the pointer can be moved within.

        This is the tuple ``(x, y, width, height)``, in the logical pixel
        coordinate space absolute pointer events use, or ``None`` if no
        absolute pointer is available.
        """
        with self._lock:
            self._ensure()
            return self._bounds

    @property
    def keymap(self):
        """The keyboard layout assigned by the compositor.

        This is an instance of :class:`Keymap`, or ``None`` if no keyboard is
        available or the layout could not be read.
        """
        with self._lock:
            self._ensure()
            return self._keymap

    def pointer_motion_absolute(self, x, y):
        """Moves the pointer to an absolute position.

        :param x: The horizontal position.

        :param y: The vertical position.
        """
        with self._lock:
            self._ensure()
            self._emit(self._pointer, 'pointer_motion_absolute', float(x),
                       float(y))

    def pointer_motion(self, dx, dy):
        """Moves the pointer relative to its current position.

        :param dx: The horizontal offset.

        :param dy: The vertical offset.
        """
        with self._lock:
            self._ensure()
            # A compositor need not offer a relative pointer; an absolute one
            # cannot stand in for it, since nothing in this protocol can read
            # the position to offset from
            if self._pointer_relative is None:
                raise self.Error('this compositor offers no relative pointer')
            self._emit(self._pointer_relative, 'pointer_motion', float(dx),
                       float(dy))

    def button(self, button, is_press):
        """Presses or releases a pointer button.

        :param int button: The kernel ``BTN_*`` code of the button.

        :param bool is_press: Whether this is a press.
        """
        with self._lock:
            self._ensure()
            self._emit(self._pointer, 'button', button, is_press)

    def scroll_discrete(self, dx, dy):
        """Scrolls by a number of detents.

        The sign is the kernel's: positive values scroll right and down.

        :param int dx: The horizontal number of detents.

        :param int dy: The vertical number of detents.
        """
        with self._lock:
            self._ensure()
            self._emit(
                self._pointer, 'scroll_discrete',
                int(dx) * SCROLL_DETENT, int(dy) * SCROLL_DETENT)

    def keyboard_key(self, keycode, is_press):
        """Presses or releases a key.

        :param int keycode: The kernel ``KEY_*`` code of the key. *libei*
            speaks key positions, not characters; see :class:`Keymap`.

        :param bool is_press: Whether this is a press.
        """
        with self._lock:
            self._ensure()
            if self._keyboard is None:
                raise self.Error('this compositor offers no keyboard')
            self._emit(self._keyboard, 'keyboard_key', keycode, is_press)

    def close(self):
        """Releases the session.

        This is safe to call more than once, and on a session that was never
        started.
        """
        with self._lock:
            for device in (
                    self._pointer, self._pointer_relative, self._keyboard):
                if device is not None:
                    self._suppress(device.stop_emulating)
            self._pointer = None
            self._pointer_relative = None
            self._keyboard = None
            if self._context is not None:
                self._suppress(self._context.disconnect)
                self._context = None
            if self._connection is not None:
                self._suppress(self._connection.close)
                self._connection = None
            self._session_handle = None
            self._started = False

    @staticmethod
    def _suppress(action):
        """Performs an action, ignoring any failure.

        This is used when tearing a session down, where nothing can be done
        about a failure and the remaining steps still have to run.

        :param action: The action to perform.
        """
        # pylint: disable=W0702; we want to suppress exceptions
        try:
            action()
        except:
            pass
        # pylint: enable=W0702

    def _emit(self, device, method, *args):
        """Queues one event and sends it.

        Every event is committed as its own frame and flushed immediately:
        *libei* writes to the connection only when dispatched, so an
        undispatched frame never happens at all.

        :param device: The device to send the event on.

        :param str method: The name of the *libei* method to call.

        :param args: The arguments to pass to it.
        """
        try:
            getattr(device, method)(*args)
            device.frame()
            self._dispatch()
        except Exception as e:
            self._fail(e)
            raise self.Error(str(e))

    def _dispatch(self):
        """Writes queued events and reads whatever has arrived.

        Reading in the same breath is what keeps a disconnection from going
        unnoticed; there is deliberately no separate pump, so everything
        touching the context happens on whichever thread holds the lock.
        """
        self._context.dispatch()
        for event in self._context.events:
            if event.event_type == ei.EventType.DISCONNECT:
                raise self.Error('the compositor closed the connection')
            elif event.event_type == ei.EventType.DEVICE_RESUMED:
                # A device that was paused, by a lock screen or a seat
                # switch, needs its emulation session opened again
                self._adopt(event.device)

    def _fail(self, reason):
        """Marks this session as unusable.

        :param reason: The reason.
        """
        if self._failure is None:
            self._failure = str(reason)
        self.close()

    def _ensure(self):
        """Makes sure the session is usable, creating it if necessary.

        :raises Session.Error: if the session cannot be established
        """
        if self._started:
            return
        if self._failure is not None:
            # A failed session is not retried: the usual reasons are that the
            # user said no or that the portal is not there, and neither is
            # improved by asking again on every event
            raise self.Error(self._failure)
        try:
            self._start()
            self._started = True
        except Exception as e:
            self._fail(e)
            raise self.Error(str(e))

    def _start(self):
        """Performs the portal handshake and brings up the *libei* devices."""
        # enable_fds, since ConnectToEIS answers with a file descriptor
        self._connection = open_dbus_connection(
            bus='SESSION', enable_fds=True)

        handle_token = self._token()
        code, results = self._request(
            'CreateSession', 'a{sv}', ({
                'handle_token': ('s', handle_token),
                'session_handle_token': ('s', self._token())},),
            handle_token)
        if code != 0:
            raise self.Error('CreateSession failed with code {}'.format(code))
        self._session_handle = results['session_handle']

        # The persistence options belong on RemoteDesktop.SelectDevices; the
        # specification forbids ScreenCast.SelectSources' equivalents on a
        # remote desktop session, and some portals reject them outright
        handle_token = self._token()
        options = {
            'handle_token': ('s', handle_token),
            'types': ('u', DEVICE_KEYBOARD | DEVICE_POINTER),
            'persist_mode': ('u', PERSIST_UNTIL_REVOKED)}
        restore_token = self._load_token()
        if restore_token:
            options['restore_token'] = ('s', restore_token)
        code, _ = self._request(
            'SelectDevices', 'oa{sv}', (self._session_handle, options),
            handle_token)
        if code != 0:
            raise self.Error('SelectDevices failed with code {}'.format(code))

        handle_token = self._token()
        code, results = self._request(
            'Start', 'osa{sv}',
            (self._session_handle, '', {'handle_token': ('s', handle_token)}),
            handle_token, DIALOG_TIMEOUT)
        if code != 0:
            raise self.Error('permission to control input was not granted')

        # Re-saved on every start: the specification describes these as single
        # use, and some portals do rotate them
        if results.get('restore_token'):
            self._save_token(results['restore_token'])

        self._connect_to_eis()

    def _token(self):
        """Returns a token unique within this process.

        :return: a token
        """
        self._tokens += 1
        return 'pynput{}u{}'.format(os.getpid(), self._tokens)

    def _request(self, method, signature, body, handle_token,
                 timeout=DIALOG_TIMEOUT):
        """Calls a portal method and waits for its response signal.

        The match rule is added *before* the call is issued: the portal may
        answer before the method reply arrives, so subscribing afterwards is a
        race rather than a matter of style.

        :param str method: The method to call.

        :param str signature: The *D-Bus* signature of ``body``.

        :param tuple body: The arguments.

        :param str handle_token: The token identifying this request, used to
            derive the object path the response will arrive on.

        :param timeout: The number of seconds to wait for the response.

        :return: the tuple ``(code, results)``
        """
        sender = self._connection.unique_name.lstrip(':').replace('.', '_')
        rule = MatchRule(
            type='signal',
            interface='org.freedesktop.portal.Request',
            member='Response',
            path='{}/request/{}/{}'.format(OBJECT_PATH, sender, handle_token))
        Proxy(message_bus, self._connection).AddMatch(rule)
        address = DBusAddress(
            OBJECT_PATH, bus_name=BUS_NAME, interface=INTERFACE)
        with self._connection.filter(rule) as responses:
            reply = self._connection.send_and_get_reply(
                new_method_call(address, method, signature, body))
            if reply.header.message_type.name == 'error':
                raise self.Error('{} failed: {}'.format(method, reply.body))
            response = self._connection.recv_until_filtered(
                responses, timeout=timeout)
        code, results = response.body
        # Portal results arrive as a map of variants, which jeepney hands over
        # as (signature, value) pairs
        return code, {
            key: value[1]
            for key, value in results.items()}

    def _connect_to_eis(self):
        """Asks the portal for an *EI* file descriptor and sets up its devices.
        """
        address = DBusAddress(
            OBJECT_PATH, bus_name=BUS_NAME, interface=INTERFACE)
        reply = self._connection.send_and_get_reply(
            new_method_call(
                address, 'ConnectToEIS', 'oa{sv}',
                (self._session_handle, {})))
        if reply.header.message_type.name == 'error':
            raise self.Error('ConnectToEIS failed: {}'.format(reply.body))
        handle = reply.body[0]
        self._setup_devices(
            handle.to_raw_fd()
            if hasattr(handle, 'to_raw_fd')
            else int(handle))

    def _setup_devices(self, fd):
        """Binds the capabilities we need and waits for the devices.

        The handshake is asynchronous: the server announces a seat, we ask it
        for capabilities, and it answers with one device per group. A device
        arrives paused, so nothing may be sent until it has been resumed.

        :param int fd: The file descriptor returned by ``ConnectToEIS``.
        """
        self._context = ei.Sender.create_for_fd(fd, name='pynput')
        capabilities = (
            ei.DeviceCapability.POINTER,
            ei.DeviceCapability.POINTER_ABSOLUTE,
            ei.DeviceCapability.BUTTON,
            ei.DeviceCapability.SCROLL,
            ei.DeviceCapability.KEYBOARD)
        deadline = time.time() + DEVICE_TIMEOUT
        while time.time() < deadline:
            # Dispatched here rather than through _dispatch(), which drains
            # the same queue looking for a disconnection and would leave
            # nothing for this loop to read
            self._context.dispatch()
            for event in self._context.events:
                if event.event_type == ei.EventType.SEAT_ADDED:
                    event.seat.bind(capabilities)
                elif event.event_type == ei.EventType.DEVICE_RESUMED:
                    self._adopt(event.device)
                elif event.event_type == ei.EventType.DISCONNECT:
                    raise self.Error('the compositor closed the connection')
            if self._pointer is not None and self._keyboard is not None:
                break
            time.sleep(0.02)

        # An absolute pointer is the one device with no substitute: without it
        # the position cannot be set at all
        if self._pointer is None:
            raise self.Error('the compositor offered no absolute pointer')

    def _adopt(self, device):
        """Takes a resumed device into use.

        A device may be paused and resumed again while the session lives, for
        instance when the screen is locked or the session switches away from
        this seat, and a resumed device needs ``start_emulating`` called on it
        afresh. So this runs on every resume, not only the first: without it
        the session would survive a lock screen but silently stop sending.

        :param device: The device.
        """
        capabilities = device.capabilities
        if ei.DeviceCapability.POINTER_ABSOLUTE in capabilities:
            if self._pointer is not None and self._pointer != device:
                return
            self._pointer = device
            # The compositor's own coordinate space, rather than one guessed
            # from the size of the screen; these are logical pixels, which on
            # a scaled display are not device pixels.
            #
            # Absolute coordinates are desktop wide rather than relative to
            # any one region, so with several monitors the usable area is the
            # rectangle covering all of them. It may be larger than their sum
            # if the monitors are not laid out edge to edge, which is why this
            # is only used to reject coordinates that cannot be on any screen
            if device.regions:
                edges = [
                    region.position + region.dimension
                    for region in device.regions]
                left = min(x for x, _, _, _ in edges)
                top = min(y for _, y, _, _ in edges)
                self._bounds = (
                    left, top,
                    max(x + w for x, _, w, _ in edges) - left,
                    max(y + h for _, y, _, h in edges) - top)
        elif ei.DeviceCapability.POINTER in capabilities:
            if self._pointer_relative is not None \
                    and self._pointer_relative != device:
                return
            self._pointer_relative = device
        elif ei.DeviceCapability.KEYBOARD in capabilities:
            if self._keyboard is not None and self._keyboard != device:
                return
            self._keyboard = device
            if self._keymap is None:
                self._keymap = Keymap.load(device)
        else:
            return
        device.start_emulating()

    def _load_token(self):
        """Reads the stored portal restore token.

        :return: a token, or ``None``
        """
        path = token_path()
        if path is None:
            return None
        try:
            with open(path, 'rb') as f:
                return json.loads(f.read().decode('utf-8'))['token']
        except (IOError, OSError, ValueError, KeyError):
            # A missing or damaged token costs one dialog and nothing else
            return None

    def _save_token(self, token):
        """Stores the portal restore token, so the user is asked only once.

        :param str token: The token.
        """
        path = token_path()
        if path is None:
            return
        try:
            directory = os.path.dirname(path)
            if directory:
                try:
                    os.makedirs(directory)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
            with open(path, 'wb') as f:
                f.write(json.dumps({'token': token}).encode('utf-8'))
        except (IOError, OSError):
            # Not fatal: the session just granted is still usable, and only
            # the next run pays for this with a dialog
            pass


class Keymap(object):
    """The keyboard layout the compositor has assigned.

    *libei*, like the kernel, identifies keys by position rather than by the
    character they produce, so a character can be typed only once the layout
    is known. The compositor passes its layout along with the keyboard device,
    which makes it the authoritative answer rather than a guess, but reading
    it requires *libxkbcommon*. Where its *Python* bindings are missing, keys
    with a known position still work and characters do not.
    """

    def __init__(self, table):
        self._table = table

    @classmethod
    def load(cls, device):
        """Reads the layout assigned to a keyboard device.

        :param device: The *libei* device.

        :return: a keymap, or ``None`` if the layout is unavailable or cannot
            be interpreted
        """
        try:
            from xkbcommon import xkb
        except ImportError:
            return None
        try:
            keymap = device.keymap
            if keymap is None:
                return None
            with keymap.fd as f:
                data = f.read(keymap.size)
            return cls(cls._read(xkb, xkb.Context().keymap_new_from_buffer(
                data)))
        except Exception:  # pylint: disable=W0703
            # The layout is a convenience: without it this backend still sends
            # every key whose position is known
            return None

    @staticmethod
    def _read(xkb, keymap):
        """Builds a mapping from character to key position and modifiers.

        :param xkb: The ``xkbcommon.xkb`` module.

        :param keymap: The compiled keymap.

        :return: a mapping from character to the tuple ``(keycode, shifted)``
        """
        table = {}
        for keycode in range(keymap.min_keycode(), keymap.max_keycode() + 1):
            try:
                levels = keymap.num_levels_for_key(keycode, 0)
            except Exception:  # pylint: disable=W0703
                continue
            for level in range(levels):
                try:
                    symbols = keymap.key_get_syms_by_level(keycode, 0, level)
                except Exception:  # pylint: disable=W0703
                    continue
                for symbol in symbols:
                    try:
                        character = xkb.keysym_to_string(symbol)
                    except Exception:  # pylint: disable=W0703
                        continue
                    # Only the first key able to produce a character is kept,
                    # so that a character on the main block is not displaced
                    # by the same character on the keypad
                    if character and len(character) == 1 \
                            and character not in table:
                        table[character] = (
                            keycode - XKB_KEYCODE_OFFSET,
                            Keymap._needs_shift(keymap, keycode, level))
        return table

    @staticmethod
    def _needs_shift(keymap, keycode, level):
        """Returns whether reaching a shift level requires the shift modifier.

        A level may be reachable through several combinations of modifiers;
        ``shift`` is the only one this backend can press by itself, so the
        others are treated as unreachable.

        :param keymap: The compiled keymap.

        :param int keycode: The *XKB* keycode.

        :param int level: The shift level.

        :return: whether shift is required
        """
        try:
            masks = keymap.key_get_mods_for_level(keycode, 0, level)
        except Exception:  # pylint: disable=W0703
            return level != 0
        if not masks:
            return level != 0
        shift = 1 << keymap.mod_get_index('Shift')
        return any(mask & shift for mask in masks)

    def get(self, character):
        """Looks up a character.

        :param str character: The character.

        :return: the tuple ``(keycode, shifted)``, or ``None`` if the
            character cannot be typed with this layout
        """
        return self._table.get(character)


class ListenerMixin(object):
    """A mixin for non-functional *libei* event listeners.

    Monitoring input is a separate problem from injecting it, solved by the
    ``org.freedesktop.portal.InputCapture`` portal rather than by
    ``RemoteDesktop``, and this backend does not implement it. Set
    ``$PYNPUT_BACKEND_KEYBOARD`` or ``$PYNPUT_BACKEND_MOUSE`` to ``xorg`` to
    monitor input from *Xwayland* clients.
    """

    def _run(self):
        raise NotImplementedError(
            'monitoring input is not supported by the libei backend; it '
            'requires the InputCapture portal')

    def _stop_platform(self):
        pass


#: The session shared by every controller
_SESSION = None

#: The lock held while creating :attr:`_SESSION`
_SESSION_LOCK = threading.Lock()


def session():
    """Returns the session shared by every controller.

    There is only one: ``SelectDevices`` grants the pointer and the keyboard
    together, so a session for each would ask the user twice for the same
    permission.

    :return: a session
    """
    global _SESSION
    with _SESSION_LOCK:
        if _SESSION is None:
            _SESSION = Session()
        return _SESSION
