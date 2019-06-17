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

    def on_press(key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
        except AttributeError:
            print('special key {0} pressed'.format(
                key))

    def on_release(key):
        print('{0} released'.format(
            key))
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
            print('{0} was pressed'.format(e.args[0]))


Toggling event listening
~~~~~~~~~~~~~~~~~~~~~~~~

Once :method:`pynput.keyboard.Listener.stop` has been called, the listener
cannot be restarted, since listeners are instances of
:class:`threading.Thread`.

If your application requires toggling listening events, you must either add an
internal flag to ignore events when not required, or create a new listener when
resuming listening.
