Handling the mouse
==================

The package ``pynput.mouse`` contains classes for contolling and monitoring the
mouse.


Controlling the mouse
---------------------

Use :class:`pynput.mouse.Controller` like this::

    from pynput.mouse import Controller, Listener

    d = Controller()

    # Read pointer position
    print('The current pointer position is {0}'.format(
        d.position))

    # Set pointer position
    d.position = (10, 20)
    print('Now we have moved it to {0}'.format(
        d.position))

    # Move pointer relative to current position
    d.move(5, -5)

    # Press and release
    d.press(d.Button.left)
    d.release(d.Button.left)

    # Double click; this is different from pressing and releasing twice on Mac
    # OSX
    d.click(d.Button.left, 2)

    # Scroll two steps down
    d.scroll(0, 2)


Monitoring the mouse
--------------------

Use :class:`pynput.mouse.Listener` like this::

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

    def on_scroll(dx, dy):
        print('Scrolled {0}'.format(
            (x, y)))

    # Collect events until released
    with Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as l:
        l.join()

A mouse listener is a :class:`threading.Thread`, and all callbacks will be
invoked from the thread.

Call :meth:`pynput.mouse.Listener.stop` from anywhere, or raise
:class:`pynput.mouse.Listener.StopException` or return ``False`` from a
callback to stop the listener.


Reference
---------

.. autoclass:: pynput.mouse.Controller
    :members:

.. autoclass:: pynput.mouse.Listener
    :members:
