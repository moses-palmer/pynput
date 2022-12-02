
# insert in front of sys.path because of system package already installed
import os
import sys
sys.path.insert(0,
    os.path.join(os.path.dirname(__file__), '..', 'lib'))

import functools

from pynput import keyboard

"""
I was looking for a way to use both HotKeys and regular callabacks
(i.e. on_press and on_release) and still being able to pass the
suppress argument to the Listener.

The main issue here is the call for keyboard.Listener.canonical.
"""

# these might be provided by the package
def notify_hotkeys(hotkeys, is_press):
    """Decorator to add HotKey capabilities to event callbacks.
    """
    def decorator_factory(callback):
        @functools.wraps(callback)
        def wrapper(key):
            if callback(key) is False:
                return False
            can_key = keyboard.Listener.canonical(key)
            hot_callback = 'press' if is_press else 'release'
            for hk in hotkeys:
                getattr(hk, hot_callback)(can_key)
        return wrapper
    return decorator_factory

def activate_hotkeys(hotkeys):
    return notify_hotkeys(hotkeys, True)

def deactivate_hotkeys(hotkeys):
    return notify_hotkeys(hotkeys, False)


def on_ctrl_c():
    print("=> HotKey('<ctrl>+c')")
    # here return False should work as for other callbacks
    raise keyboard.Listener.StopException()

hotkeys = [
    keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+c'),
        on_ctrl_c)
]

@activate_hotkeys(hotkeys)
def on_press(key):
    print("=> {}".format(key))

@deactivate_hotkeys(hotkeys)
def on_release(key):
    print("=< {}".format(key))
    if key == keyboard.Key.esc:
        return False


with keyboard.Listener(
        on_press=on_press,
        on_release=on_release,
        suppress=True) as listener:
    print("Press ESC or Ctrl-C to exit")
    listener.join()
