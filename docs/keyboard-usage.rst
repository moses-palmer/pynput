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

    from pynput.keyboard import Key, Listener

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
        if key == Key.esc:
            # Stop listener
            return False

    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

A keyboard listener is a ``threading.Thread``, and all callbacks will be
invoked from the thread.

Call ``pynput.keyboard.Listener.stop`` from anywhere, raise ``StopException``
or return ``False`` from a callback to stop the listener.

Starting a keyboard listener may be subject to some restrictions on your
platform.

On *Mac OSX*, one of the following must be true:

*  The process must run as root.

*  Your application must be white listed under *Enable access for assistive
   devices*. Note that this might require that you package your application,
   since otherwise the entire *Python* installation must be white listed.

On *Windows*, virtual events sent by *other* processes may not be received.
This library takes precautions, however, to dispatch any virtual events
generated to all currently running listeners of the current process.
