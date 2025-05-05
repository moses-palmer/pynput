Controlling the mouse
---------------------

Use ``pynput.mouse.Controller`` like this::

    from pynput.mouse import Button, Controller

    mouse = Controller()

    # Read pointer position
    print('The current pointer position is {}'.format(
        mouse.position))

    # Set pointer position
    mouse.position = (10, 20)
    print('Now we have moved it to {}'.format(
        mouse.position))

    # Move pointer relative to current position
    mouse.move(5, -5)

    # Press and release
    mouse.press(Button.left)
    mouse.release(Button.left)

    # Double click; this is different from pressing and releasing
    # twice on macOS
    mouse.click(Button.left, 2)

    # Scroll two steps down
    mouse.scroll(0, 2)


Monitoring the mouse
--------------------

Use ``pynput.mouse.Listener`` like this::

    from pynput import mouse

    def on_move(x, y, injected):
        print('Pointer moved to {}; it was {}'.format(
            (x, y, 'faked' if injected else 'not faked')))

    def on_click(x, y, button, pressed, injected):
        print('{} at {}; it was {}'.format(
            'Pressed' if pressed else 'Released',
            (x, y, 'faked' if injected else 'not faked')))
        if not pressed:
            # Stop listener
            return False

    def on_scroll(x, y, dx, dy, injected):
        print('Scrolled {} at {}; it was {}'.format(
            'down' if dy < 0 else 'up',
            (x, y, 'faked' if injected else 'not faked')))

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

When using the non-blocking version above, the current thread will continue
executing. This might be necessary when integrating with other GUI frameworks
that incorporate a main-loop, but when run from a script, this will cause the
program to terminate immediately.


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
            print('{} was clicked'.format(e.args[0]))


Toggling event listening for the mouse listener
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once ``pynput.mouse.Listener.stop`` has been called, the listener cannot be
restarted, since listeners are instances of ``threading.Thread``.

If your application requires toggling listening events, you must either add an
internal flag to ignore events when not required, or create a new listener when
resuming listening.


Synchronous event listening for the mouse listener
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To simplify scripting, synchronous event listening is supported through the
utility class ``pynput.mouse.Events``. This class supports reading single
events in a non-blocking fashion, as well as iterating over all events.

To read a single event, use the following code::

    from pynput import mouse

    # The event listener will be running in this block
    with mouse.Events() as events:
        # Block at most one second
        event = events.get(1.0)
        if event is None:
            print('You did not interact with the mouse within one second')
        else:
            print('Received event {}'.format(event))

To iterate over mouse events, use the following code::

    from pynput import mouse

    # The event listener will be running in this block
    with mouse.Events() as events:
        for event in events:
            if event.button == mouse.Button.right:
                break
            else:
                print('Received event {}'.format(event))

Please note that the iterator method does not support non-blocking operation,
so it will wait for at least one mouse event.

The events will be instances of the inner classes found in
``pynput.mouse.Events``.


Ensuring consistent coordinates between listener and controller on Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recent versions of _Windows_ support running legacy applications scaled when
the system scaling has been increased beyond 100%. This allows old applications
to scale, albeit with a blurry look, and avoids tiny, unusable user interfaces.

This scaling is unfortunately inconsistently applied to a mouse listener and a
controller: the listener will receive physical coordinates, but the controller
has to work with scaled coordinates.

This can be worked around by telling Windows that your application is DPI
aware. This is a process global setting, so _pynput_ cannot do it
automatically. Do enable DPI awareness, run the following code::

   import ctypes


   PROCESS_PER_MONITOR_DPI_AWARE = 2

   ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
