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
data as a `MSLLHOOKSTRUCT`_ or a `KBDLLHOOKSTRUCT`, depending on whether you
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
            Listener.suppress_event(pynput.keyboard.Listener)

On mouse it is different because the data is a `MSLLHOOKSTRUCT`_ instead of a `KBDLLHOOKSTRUCT`_.
so it is better to listen to the message and suppress the event if needed.

Here is a mouse example::

    #Values for msg can be found here:
    #https://learn.microsoft.com/en-us/windows/win32/inputdev/mouse-input-notifications
    # you can also just use print(msg) to see the messages
    def win32_event_filter(msg,data):
        if(msg == 0x201): 
            #0x21 is the left mouse button down event
            Listener.suppress_event(pynput.mouse.Listener)

You can use the win32_event_filter as such::
    mouse_listen = pynput.mouse.Listener(win32_event_filter=win32_event_filter)


.. _MSLLHOOKSTRUCT: https://docs.microsoft.com/en-gb/windows/win32/api/winuser/ns-winuser-msllhookstruct

.. _KBDLLHOOKSTRUCT: https://docs.microsoft.com/en-gb/windows/win32/api/winuser/ns-winuser-kbdllhookstruct


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
