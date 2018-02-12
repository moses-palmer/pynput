Controlling the keyboard
------------------------

Use ``pynput.keyboard.Controller`` like this::

    from pynput.keyboard import Key, Controller

    keyboard = Controller()

    # Press and release space
    keyboard.press(Key.space)
    keyboard.release(Key.space)

    # Type a lower case A; this will work even if no key on the
    # physical keyboard is labelled 'A'
    keyboard.press('a')
    keyboard.release('a')

    # Type two upper case As
    keyboard.press('A')
    keyboard.release('A')
    with keyboard.pressed(Key.shift):
        keyboard.press('a')
        keyboard.release('a')

    # Type 'Hello World' using the shortcut type method
    keyboard.type('Hello World')


Monitoring the keyboard
-----------------------

Use ``pynput.keyboard.Listener`` like this::

    from pynput import keyboard

    def on_press(key, injected):
        try:
            print('alphanumeric key {} pressed; it was {}'.format(
                key.char, 'faked' if injected else 'not faked'))
        except AttributeError:
            print('special key {} pressed'.format(
                key))

    def on_release(key, injected):
        print('{} released; it was {}'.format(
            key, 'faked' if injected else 'not faked'))
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

    # ...or, in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

A keyboard listener is a ``threading.Thread``, and all callbacks will be
invoked from the thread.

Call ``pynput.keyboard.Listener.stop`` from anywhere, raise ``StopException``
or return ``False`` from a callback to stop the listener.

The ``key`` parameter passed to callbacks is a ``pynput.keyboard.Key``, for
special keys, a ``pynput.keyboard.KeyCode`` for normal alphanumeric keys, or
just ``None`` for unknown keys.

When using the non-blocking version above, the current thread will continue
executing. This might be necessary when integrating with other GUI frameworks
that incorporate a main-loop, but when run from a script, this will cause the
program to terminate immediately.


The keyboard listener thread
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The listener callbacks are invoked directly from an operating thread on some
platforms, notably *Windows*.

This means that long running procedures and blocking operations should not be
invoked from the callback, as this risks freezing input for all processes.

A possible workaround is to just dispatch incoming messages to a queue, and let
a separate thread handle them.


Handling keyboard listener errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a callback handler raises an exception, the listener will be stopped. Since
callbacks run in a dedicated thread, the exceptions will not automatically be
reraised.

To be notified about callback errors, call ``Thread.join`` on the listener
instance::

    from pynput import keyboard

    class MyException(Exception): pass

    def on_press(key):
        if key == keyboard.Key.esc:
            raise MyException(key)

    # Collect events until released
    with keyboard.Listener(
            on_press=on_press) as listener:
        try:
            listener.join()
        except MyException as e:
            print('{} was pressed'.format(e.args[0]))


Toggling event listening for the keyboard listener
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once ``pynput.keyboard.Listener.stop`` has been called, the listener cannot be
restarted, since listeners are instances of ``threading.Thread``.

If your application requires toggling listening events, you must either add an
internal flag to ignore events when not required, or create a new listener when
resuming listening.


Synchronous event listening for the keyboard listener
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To simplify scripting, synchronous event listening is supported through the
utility class ``pynput.keyboard.Events``. This class supports reading single
events in a non-blocking fashion, as well as iterating over all events.

To read a single event, use the following code::

    from pynput import keyboard

    # The event listener will be running in this block
    with keyboard.Events() as events:
        # Block at most one second
        event = events.get(1.0)
        if event is None:
            print('You did not press a key within one second')
        else:
            print('Received event {}'.format(event))

To iterate over keyboard events, use the following code::

    from pynput import keyboard

    # The event listener will be running in this block
    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                break
            else:
                print('Received event {}'.format(event))

Please note that the iterator method does not support non-blocking operation,
so it will wait for at least one keyboard event.

The events will be instances of the inner classes found in
``pynput.keyboard.Events``.


Global hotkeys
~~~~~~~~~~~~~~

A common use case for keyboard monitors is reacting to global hotkeys. Since a
listener does not maintain any state, hotkeys involving multiple keys must
store this state somewhere.

*pynput* provides the class ``pynput.keyboard.HotKey`` for this purpose. It
contains two methods to update the state, designed to be easily interoperable
with a keyboard listener: ``pynput.keyboard.HotKey.press`` and
``pynput.keyboard.HotKey.release`` which can be directly passed as listener
callbacks.

The intended usage is as follows::

    from pynput import keyboard

    def on_activate():
        print('Global hotkey activated!')

    def for_canonical(f):
        return lambda k: f(l.canonical(k))

    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+<alt>+h'),
        on_activate)
    with keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)) as l:
        l.join()

This will create a hotkey, and then use a listener to update its state. Once
all the specified keys are pressed simultaneously, ``on_activate`` will be
invoked.

Note that keys are passed through ``pynput.keyboard.Listener.canonical`` before
being passed to the ``HotKey`` instance. This is to remove any modifier state
from the key events, and to normalise modifiers with more than one physical
button.

The method ``pynput.keyboard.HotKey.parse`` is a convenience function to
transform shortcut strings to key collections. Please see its documentation for
more information.

To register a number of global hotkeys, use the convenience class
``pynput.keyboard.GlobalHotKeys``::

    from pynput import keyboard

    def on_activate_h():
        print('<ctrl>+<alt>+h pressed')

    def on_activate_i():
        print('<ctrl>+<alt>+i pressed')

    with keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+h': on_activate_h,
            '<ctrl>+<alt>+i': on_activate_i}) as h:
        h.join()
