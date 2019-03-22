Release Notes
=============

v1.4.2 - Corrected keybord listener on macOS
--------------------------------------------
*  Use ``CGEventKeyboardGetUnicodeString`` in *macOS* keyboard listener to send
   correct characters.
*  Include keysym instead of key code in *Xorg* keyboard listener.
*  Corrected logging to not include expected ``StopException``.
*  Updated and corrected documentation.


v1.4.1 - Logging
----------------
*  Log unhandled exceptions raised by listener callbacks.


v1.4 - Event suppression
------------------------
*  Added possibility to fully suppress events when listening.
*  Added support for typing some control characters.
*  Added support for mouse drag events on *OSX*. Thanks to *jungledrum*!
*  Include the key code in keyboard listener events.
*  Correctly handle the numeric key pad on *Xorg* with *num lock* active.
   Thanks to *TheoRet*!
*  Corrected handling of current thread keyboard layout on *Windows*. Thanks to
   *Schmettaling*!
*  Corrected stopping of listeners on *Xorg*.
*  Corrected import of ``Xlib.keysymdef.xkb`` on *Xorg*. Thanks to *Glandos*!


v1.3.10 - Do not crash under *Xephyr*
-------------------------------------
*  Do not crash when ``Xlib.display.Display.get_input_focus`` returns an
   integer, as it may when running under *Xephyr*. Thanks to *Eli Skeggs*!


v1.3.9 - Correctly handle the letter *A* on *OSX*
-------------------------------------------------
*  Corrected check for virtual key code when generating keyboard events on
   *OSX*. This fixes an issue where pressing *A* with *shift* explicitly pressed
   would still type a miniscule letter.


v1.3.8 - Do not crash on some keyboard layouts on *OSX*
-------------------------------------------------------
*  Fall back on a different method to retrieve the keyboard layout on *OSX*.
   This helps for some keyboard layouts, such as *Chinese*. Thanks to
   *haoflynet*!


v1.3.7 - *Xorg* corrections
---------------------------
*  Include mouse buttons up to *30* for *Xorg*.


v1.3.6 - *win32* corrections
----------------------------
*  Corrected double delivery of fake keyboard events on *Windows*.
*  Corrected handling of synthetic unicode keys on *Windows*.


v1.3.5 - Corrected dependencies again
-------------------------------------
*  Reverted changes in *1.3.3*.
*  Corrected platform specifier for *Python 2* on *Linux*.


v1.3.4 - *Xorg* corrections
---------------------------
*  Corrected bounds check for values on *Xorg*.


v1.3.3 - Make dependencies non-optional
---------------------------------------
*  Made platform depdendencies non-optional.


v1.3.2 - Fix for button click on Mac
------------------------------------
*  Corrected regression from previous release where button clicks would
   crash the *Mac* mouse listener.


v1.3.1 - Fixes for unknown buttons on Linux
-------------------------------------------
*  Fall back on `Button.unknown` for unknown mouse buttons in *Xorg* mouse
   listener.


v1.3 - Platform specific features
---------------------------------
*  Added ability to stop event propagation on *Windows*. This will prevent
   events from reaching other applications.
*  Added ability to ignore events on *Windows*. This is a workaround for systems
   where the keyboard monitor interferes with normal keyboard events.
*  Added ability to modify events on *OSX*. This allows intercepting and
   altering input events before they reach other applications.
*  Corrected crash on *OSX* when some types of third party input sources are
   installed.


v1.2 - Improved error handling
------------------------------
*  Allow catching exceptions thrown from listener callbacks. This changes the
   API, as joining a listener now potentially raises unhandled exceptions,
   and unhandled exceptions will stop listeners.
*  Added support for the numeric keypad on *Linux*.
*  Improved documentation.
*  Thanks to *jollysean* and *gilleswijnker* for their input!


v1.1.7 - Handle middle button on Windows
----------------------------------------
*  Listen for and dispatch middle button mouse clicks on *Windows*.


v1.1.6 - Corrected context manager for pressing keys
----------------------------------------------------
*  Corrected bug in ``pynput.keyboard.Controller.pressed`` which caused it to
   never release the key. Many thanks to Toby Southwell!


v1.1.5 - Corrected modifier key combinations on Linux
-----------------------------------------------------
*  Corrected handling of modifier keys to allow them to be composable on
   *Linux*.


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
