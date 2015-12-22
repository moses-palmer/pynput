Controlling the keyboard
------------------------

Use ``pynput.keyboard.Controller`` like this::

    from pynput.keyboard import Key, Controller

    d = Controller()

    # Press and release space
    d.press(Key.space)
    d.release(Key.space)

    # Type a lower case A; this will work even if no key on the physical
    # keyboard is labelled 'A'
    d.press('a')
    d.release('a')

    # Type two upper case As
    d.press('A')
    d.release('A')
    with d.pressed(Key.shift):
        d.press('a')
        d.release('a')

    # Type 'Hello World' using the shortcut type method
    d.type('Hello World')
