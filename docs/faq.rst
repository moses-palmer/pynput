Frequently asked question
-------------------------

How do I suppress specific events only?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Passing the ``suppress=True`` flag to listeners will suppress all events
system-wide. If this is not what you want, you will have to employ different
solutions for different backends.

If your backend of choice is not listed below, it does not support suppression
of specific events.

macOS
^^^^^

For *macOS*, pass the named argument ``darwin_intercept`` to the listener
constructor. This argument should be a callable taking the arguments
``(event_type, event)``, where ``event_type`` is any mouse related event type
constant, and ``event`` is a `CGEventRef`_. The ``event`` argument can be
manipulated by the functions found on the `Apple documentation`_.

If the interceptor function determines that the event should be suppressed,
return ``None``, otherwise return the ``event``, which you may modify.

Here is a keyboard example::

    def darwin_intercept(event_type, event):
        import Quartz
        length, chars = Quartz.CGEventKeyboardGetUnicodeString(
            event, 100, None, None)
        if length > 0 and chars == 'x':
            # Suppress x
            return None
        elif length > 0 and chars == 'a':
            # Transform a to b
            Quartz.CGEventKeyboardSetUnicodeString(event, 1, 'b')
        else:
            return event


.. _CGEventRef: https://developer.apple.com/documentation/coregraphics/cgeventref?language=objc

.. _Apple documentation: https://developer.apple.com/documentation/coregraphics/quartz_event_services?language=objc


Windows
^^^^^^^

For *Windows*, pass the argument named ``win32_event_filter`` to the listener
constructor. This argument should be a callable taking the arguments
``(msg, data)``, where ``msg`` is the current message, and ``data`` associated
data as a `MSLLHOOKSTRUCT`_ or a `KBDLLHOOKSTRUCT`_, depending on whether you
are creating a mouse or keyboard listener.

If the filter function determines that the event should be suppressed, call
``suppress_event`` on the listener. If you return ``False``, the event will be
hidden from other listener callbacks.

Here is a keyboard example::

    # Values for MSLLHOOKSTRUCT.vkCode can be found here:
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    def win32_event_filter(msg, data):
        if data.vkCode == 0x58:
            # Suppress x
            listener.suppress_event()


.. _MSLLHOOKSTRUCT: https://docs.microsoft.com/en-gb/windows/win32/api/winuser/ns-winuser-msllhookstruct

.. _KBDLLHOOKSTRUCT: https://docs.microsoft.com/en-gb/windows/win32/api/winuser/ns-winuser-kbdllhookstruct

Here is a mouse example::

    from ctypes import wintypes
    from pynput import mouse
    from pynput.mouse._win32 import Listener, WHEEL_DELTA
    
    def win32_event_filter(self, msg, data: Listener._MSLLHOOKSTRUCT):
        # return False: event passed to system, but not passed to the listener
        # self.suppress_event(): event not passed to the system and listener
        #   NOTE: self.suppress_event() raises exception, and you should not catch it
        # raise self.StopException(): stop the listener (same as return False in normal on_click listener)
        
        x: int
        y: int
        button: mouse.Button
        pressed: bool
        
        if msg == self.WM_MOUSEMOVE:
            x, y = data.pt.x, data.pt.y
            # self.on_move(x, y)
        
        elif msg in self.CLICK_BUTTONS:
            button, pressed = self.CLICK_BUTTONS[msg]
            assert isinstance(button, mouse.Button)
            assert isinstance(pressed, bool)
            x, y = data.pt.x, data.pt.y
            # self.on_click(x, y, button, pressed)
            
            if pressed:
                self.pos_press = (x, y)
                self.suppress_event()
            else:
                self.pos_release = (x, y)
                # NOTE: you cannot suppress event when you want to stop listener
                # self.suppress_event()
                raise self.StopException()
            
        elif msg in self.X_BUTTONS:
            button, pressed = self.X_BUTTONS[msg][data.mouseData >> 16]
            assert isinstance(button, mouse.Button)
            assert isinstance(pressed, bool)
            x, y = data.pt.x, data.pt.y
            # self.on_click(x, y, button, pressed)
            
        elif msg in self.SCROLL_BUTTONS:
            mx, my = self.SCROLL_BUTTONS[msg]
            assert isinstance(mx, int)
            assert isinstance(my, int)
            dd = wintypes.SHORT(data.mouseData >> 16).value // WHEEL_DELTA
            x, y = data.pt.x, data.pt.y
            dx: int = dd * mx
            dy: int = dd * my
            # self.on_scroll(x, y, dx, dy)


When using a packager I get an ``ImportError`` on startup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This happens when using a packager, such as *PyInstaller*, to package your
application.

The reason for the error is that the packager attempts to build a dependency
tree of the modules used by inspecting ``import`` statements, and *pynput*
finds the platform dependent backend modules at runtime using ``importlib``.

To solve this problem, please consult the documentation of your tool to find
how to explicitly add modules.

Which modules to add depends on your distribution platform. The backend modules
are those starting with an underscore (``'_'``) in the ``pynput.keyboard`` and
``pynput.mouse`` packages. Additionally, you will need modules with
corresponding names from the ``pynput._util`` package.
