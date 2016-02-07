import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), '..', 'lib'))

from pynput import keyboard


def on_press(key):
    print('=> %s' % key)
    if key == keyboard.Key.esc:
        return False


def on_release(key):
    print('=< %s' % key)


with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    print('Press esc to exit')
    listener.join()
