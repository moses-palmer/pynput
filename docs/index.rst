pynput Package Documentation
============================

This library allows you to control and monitor input devices.

It contains subpackages for each type of input device supported:

:mod:`pynput.mouse`
    Contains classes for controlling and monitoring a mouse or trackpad.

:mod:`pynput.keyboard`
    Contains classes for controlling and monitoring the keyboard.

All modules mentioned above are automatically imported into the :mod:`pynput`
package. To use any of them, import them from the main package::

    from pynput import mouse, keyboard


Forcing a specific backend
--------------------------

*pynput* attempts to use the backend suitable for the current platform, but
this automatic choice is possible to override.

If the environment variables ``$PYNPUT_BACKEND_KEYBOARD`` or
``$PYNPUT_BACKEND`` are set, their value will be used as backend name for the
keyboard classes, and if ``$PYNPUT_BACKEND_MOUSE`` or ``$PYNPUT_BACKEND``
are set, their value will be used as backend name for the mouse classes.

Available backends are:

*  ``darwin``, the default for *macOS*.
*  ``win32``, the default for *Windows*.
*  ``uinput``, an optional backend for *Linux* requiring *root* privileges and
   supporting only keyboards.
*  ``xorg``, the default for other operating systems.
*  ``dummy``, a non-functional, but importable, backend. This is useful as
   mouse backend when using the ``uinput`` backend.


Table of contents
-----------------

.. toctree::
   :maxdepth: 2

   mouse

   keyboard

   faq

   limitations


* :ref:`genindex`
