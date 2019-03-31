Controlling the mouse
---------------------

Use ``pynput.mouse.Controller`` like this::

    from pynput.mouse import Button, Controller

    mouse = Controller()

    # Read pointer position
    print('The current pointer position is {0}'.format(
        mouse.position))

    # Set pointer position
    mouse.position = (10, 20)
    print('Now we have moved it to {0}'.format(
        mouse.position))

    # Move pointer relative to current position
    mouse.move(5, -5)

    # Press and release
    mouse.press(Button.left)
    mouse.release(Button.left)

    # Double click; this is different from pressing and releasing
    # twice on Mac OSX
    mouse.click(Button.left, 2)

    # Scroll two steps down
    mouse.scroll(0, 2)


Monitoring the mouse
--------------------

Use ``pynput.mouse.Listener`` like this::

    from pynput import mouse

    def on_move(x, y):
        print('Pointer moved to {0}'.format(
            (x, y)))

    def on_click(x, y, button, pressed):
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)))
        if not pressed:
            # Stop listener
            return False

    def on_scroll(x, y, dx, dy):
        print('Scrolled {0} at {1}'.format(
            'down' if dy < 0 else 'up',
            (x, y)))

    # Collect events until released
    with mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()

    # ...or, in a non-blocking fashion:
    listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll)
    listener.start()

A mouse listener is a ``threading.Thread``, and all callbacks will be invoked
from the thread.

Call ``pynput.mouse.Listener.stop`` from anywhere, raise ``StopException`` or
return ``False`` from a callback to stop the listener.


The mouse listener thread
~~~~~~~~~~~~~~~~~~~~~~~~~

The listener callbacks are invoked directly from an operating thread on some
platforms, notably *Windows*.

This means that long running procedures and blocking operations should not be
invoked from the callback, as this risks freezing input for all processes.

A possible workaround is to just dispatch incoming messages to a queue, and let
a separate thread handle them.


Handling mouse listener errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a callback handler raises an exception, the listener will be stopped. Since
callbacks run in a dedicated thread, the exceptions will not automatically be
reraised.

To be notified about callback errors, call ``Thread.join`` on the listener
instance::

    from pynput import mouse

    class MyException(Exception): pass

    def on_click(x, y, button, pressed):
        if button == mouse.Button.left:
            raise MyException(button)

    # Collect events until released
    with mouse.Listener(
            on_click=on_click) as listener:
        try:
            listener.join()
        except MyException as e:
            print('{0} was clicked'.format(e.args[0]))


Toggling event listening
~~~~~~~~~~~~~~~~~~~~~~~~

Once :method:`pynput.mouse.Listener.stop` has been called, the listener cannot
be restarted, since listeners are instances of :class:`threading.Thread`.

If your application requires toggling listening events, you must either add an
internal flag to ignore events when not required, or create a new listener when
resuming listening.
