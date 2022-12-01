
# insert in front of sys.path because of system package already installed
import os
import sys
sys.path.insert(0,
    os.path.join(os.path.dirname(__file__), '..', 'lib'))

from pynput import keyboard

"""
I was looking for a way to use both HotKeys and regular callabacks
(i.e. on_press and on_release) and still being able to pass the
suppress argument to the Listener.

The main issue here is the call for keyboard.Listener.canonical.
"""

def on_ctrl_c():
    print("=> HotKey('<ctrl>+c')")
    raise keyboard.Listener.StopException()

hotkeys = [
    keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+c'),
        on_ctrl_c)
]

def on_press(key):
    print("=> {}".format(key))
    can_key = keyboard.Listener.canonical(key)
    for hk in hotkeys:
        hk.press(can_key)

def on_release(key):
    print("=< {}".format(key))
    if key == keyboard.Key.esc:
        return False
    can_key = keyboard.Listener.canonical(key)
    for hk in hotkeys:
        hk.release(can_key)


with keyboard.Listener(
        on_press=on_press,
        on_release=on_release,
        suppress=True) as listener:
    print("Press ESC or Ctrl-C to exit")
    listener.join()
