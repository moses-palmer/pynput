Release Notes
=============

v1.1.4 - Small bugfixes
-----------------------
*  Corrected error generation when ``GetKeyboardState`` fails.
*  Make sure to apply shift state to borrowed keys on *X*.
*  Use *pylint*.


v1.1.3 - Changed Xlib backend library
-------------------------------------
*  Changed *Xlib* library.


v1.1.2 - Added missing type for Python 2
----------------------------------------
*  Added missing ``LPDWORD`` for *Python 2* on *Windows*.


v1.1.1 - Fixes for listeners and controllers on Windows
-------------------------------------------------------
*  Corrected keyboard listener on *Windows*. Modifier keys and other keys
   changing the state of the keyboard are now handled correctly.
*  Corrected mouse click and release on *Windows*.
*  Corrected code samples.


v1.1 - Simplified usage on Linux
--------------------------------
*  Propagate import errors raised on Linux to help troubleshoot missing
   ``Xlib`` module.
*  Declare ``python3-xlib`` as dependency on *Linux* for *Python 3*.


v1.0.6 - Universal wheel
------------------------
*  Make sure to build a universal wheel for all python versions.


v1.0.5 - Fixes for dragging on OSX
----------------------------------
*  Corrected dragging on *OSX*.
*  Added scroll speed constant for *OSX* to correct slow scroll speed.


v1.0.4 - Fixes for clicking and scrolling on Windows
----------------------------------------------------
*  Corrected name of mouse input field when sending click and scroll events.


v1.0.3 - Fixes for Python 3 on Windows
--------------------------------------
*  Corrected use of ``ctypes`` on Windows.


v1.0.2 - Fixes for thread identifiers
-------------------------------------
*  Use thread identifiers to identify threads, not Thread instances.


v1.0.1 - Fixes for Python 3
---------------------------
*  Corrected bugs which prevented the library from being used on *Python 3*.


v1.0 - Stable Release
---------------------
*  Changed license to *LGPL*.
*  Corrected minor bugs and inconsistencies.
*  Corrected and extended documentation.


v0.6 - Keyboard Monitor
-----------------------
*  Added support for monitoring the keyboard.
*  Corrected wheel packaging.
*  Corrected deadlock when stopping a listener in some cases on *X*.
*  Corrected key code constants on *Mac OSX*.
*  Do not intercept events on *Mac OSX*.


v0.5.1 - Do not die on dead keys
--------------------------------
*  Corrected handling of dead keys.
*  Corrected documentation.


v0.5 - Keyboard Modifiers
-------------------------
*  Added support for modifiers.


v0.4 - Keyboard Controller
--------------------------
*  Added keyboard controller.


v0.3 - Cleanup
------------------------------------------------------------
*  Moved ``pynput.mouse.Controller.Button`` to top-level.


v0.2 - Initial Release
----------------------
*  Support for controlling the mouse on *Linux*, *Mac OSX* and *Windows*.
*  Support for monitoring the mouse on *Linux*, *Mac OSX* and *Windows*.
