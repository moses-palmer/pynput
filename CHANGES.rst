Release Notes
=============

v1.7.6 (2022-01-01) - Various fixes
-----------------------------------
*  Allow passing virtual key codes to the parser for global hot keys.
*  Stop the recording context asynchronously on *Xorg*.
*  Do not pass ``None`` to ``objc.objc_object``. Thanks to *yejunxi*!
*  Do not crash when pressing the *alt* key on *uinput*. Thanks to *Caldas
   Lopes*!
*  Use the correct option prefix for listeners derived from the backend
   implementations. Thanks to *Yu Wang*!


v1.7.5 (2021-11-19) - Various fixes
-----------------------------------
*  Corrected crashes on *Xorg* when a listener was configured to suppress
   system events. Thanks to *jpramosi*!
*  Improved handling of keyboard controller on *Windows*. The controller now
   has a greater change of working with applications using lower level events.
   Thanks to *bhudax*!
*  Updated *macOS* implementation to use new version of *pyobjc*.


v1.7.4 (2021-10-10) - Various fixes
-----------------------------------
*  Detect whether permissions are lacking on *macOS*. Thanks to *Dane Finlay*!
*  Eagerly import symbols from ``CoreFoundation`` and ``Quartz``. Thanks to
   *Ronald Oussoren*!
*  Improved handling of ``dumpkeys`` utility. Thanks to *Markus Niedermann*!
*  Removed ambiguous license file.


v1.7.3 (2021-02-10) - Various fixes
-----------------------------------
*  Corrected *keysym* handling on *Xorg*; not all groups were loaded, and the
   fallback to our internal tables was never triggered. Thanks to *Philipp
   Klaus*!
*  Updated the version of *Quartz* used for the *macOS* backend to allow
   *pynput* to be installed on *Big Sur*. Thanks to *Michael Madden*!
*  Added missing function keys on *Windows*. Thanks to *Dave Atkinson*!
*  Corrected scroll speed for mouse controller on *macOS*. Thanks to *Albert
   Zeyer*!
*  Corrected media keys for *Xorg*. Thanks to *Gabriele N. Tornetta*!
*  Corrected parameter name in documentation. Thanks to *Jinesi Yelizati*!


v1.7.2 (2020-12-21) - Corrected uinput key mapping
--------------------------------------------------
*  Corrected mapping of virtual key codes to characters for the *uinput*
   backend.
*  Corrected spelling errors. Thanks to *Martin Michlmayr*!
*  Corrected and improved documentation.


v1.7.1 (2020-08-30) - Corrected release notes
---------------------------------------------
*  Corrected thanks for arbitrary unicode character support for *Xorg*.


v1.7.0 (2020-08-30) - A new backend and many new features and bug fixes
-----------------------------------------------------------------------
*  Added a new *uinput* based keyboard backend for *Linux*, when no *X* server
   is available.
*  Allow typing arbitrary unicode characters on *Xorg* backend. Thanks to
   *gdiShun*!
*  Allow overriding the automatically selected backend with an environment
   variable, and added a dummy backend.
*  Added support for mouse side button on *Windows*. Thanks to *danielkovarik*!
*  Added convenience method to tap keys.
*  Allow specifying raw virtual key codes in hotkeys.
*  Improved error messages when a backend cannot be loaded.
*  Include more information in stringification of events.
*  Corrected return value of ``Events.get`` to that specified by the
   documentation.
*  Corrected keyboard listener not to type random characters on certain
   keyboard layouts.
*  Corrected errors when pressing certain keys on *Windows*, where the
   operating system reports that they are dead but no combining version exists.
*  Improved documentation.


v1.6.8 (2020-02-28) - Various fixes
-----------------------------------
*  Updated documentation.
*  Corrected lint warnings and tests.
*  Do not use internal types in ``argtypes`` for ``win32`` functions; this
   renders them uncallable for other code running in the same runtime.
*  Include scan codes in events on *Windows*. Thanks to *bhudax*!
*  Correctly apply transformation to scroll event values on *Windows*. Thanks
   to *DOCCA0*!


v1.6.7 (2020-02-17) - Various fixes
-----------------------------------
*  Corrected infinite scrolling on *macOS* when providing non-integer deltas.
   Thanks to *Iván Munsuri Ibáñez*!
*  Corrected controller and listener handling of media keys on *macOS*. Thanks
   to *Iván Munsuri Ibáñez*!


v1.6.6 (2020-01-23) - Corrected hot key documentation
-----------------------------------------------------
*  The code examples for the simple ``pynput.keyboard.HotKey`` now work. Thanks
   to *jfongattw*!


v1.6.5 (2020-01-08) - Corrected media key mappings
--------------------------------------------------
*  Corrected media key mappings on *macOS*. Thanks to *Luis Nachtigall*!


v1.6.4 (2020-01-03) - Corrected imports yet again
-------------------------------------------------
*  Corrected imports for keyboard Controller. Thanks to *rhystedstone*!


v1.6.3 (2019-12-28) - Corrected imports again
---------------------------------------------
*  Corrected imports for keyboard Controller. Thanks to *Matt Iversen*!


v1.6.2 (2019-12-28) - Corrected imports
---------------------------------------
*  Corrected imports for keyboard Controller. Thanks to *Matt Iversen*!


v1.6.1 (2019-12-27) - Corrections for *Windows*
-----------------------------------------------
*  Corrected global hotkeys on *Windows*.
*  Corrected pressed / released state for keyboard listener on *Windows*.
   Thanks to *segalion*!

v1.6.0 (2019-12-11) - Global Hotkeys
------------------------------------
*  Added support for global hotkeys.
*  Added support for streaming listener events synchronously.


v1.5.2 (2019-12-06) - Corrected media key names for *Xorg*
----------------------------------------------------------
*  Removed media flag from *Xorg* keys.


v1.5.1 (2019-12-06) - Corrected media key names for *macOS*
-----------------------------------------------------------
*  Corrected attribute names for media keys on *macOS*. Thanks to *ah3243*!


v1.5.0 (2019-12-04) - Various improvements
------------------------------------------
*  Corrected keyboard listener on *Windows*. Thanks to *akiratakasaki*,
   *segalion*, *SpecialCharacter*!
*  Corrected handling of some special keys, including arrow keys, when combined
   with modifiers on *Windows*. Thanks to *tuessetr*!
*  Updated documentation to include information about DPI scaling on *Windows*.
   Thanks to *david-szarka*!
*  Added experimental support for media keys. Thanks to *ShivamJoker*,
   *StormTersteeg*!


v1.4.5 (2019-11-05) - Corrected errors on *Python 3.8*
------------------------------------------------------
*  Corrected errors about using `in` operator for enums on *Python 3.8* on
   *macOS*.


v1.4.4 (2019-09-24) - Actually corrected keyboard listener on macOS
-------------------------------------------------------------------
*  Included commit to correctly fall back on
   ``CGEventKeyboardGetUnicodeString``.
*  Corrected deprecation warnings about ``Enum`` usage on *Python 3.8*.


v1.4.3 (2019-09-24) - Corrected keyboard listener on macOS again
----------------------------------------------------------------
*  Correctly fall back on ``CGEventKeyboardGetUnicodeString``.
*  Updated documentation.


v1.4.2 (2019-03-22) - Corrected keyboard listener on macOS
----------------------------------------------------------
*  Use ``CGEventKeyboardGetUnicodeString`` in *macOS* keyboard listener to send
   correct characters.
*  Include keysym instead of key code in *Xorg* keyboard listener.
*  Corrected logging to not include expected ``StopException``.
*  Updated and corrected documentation.


v1.4.1 (2018-09-07) - Logging
-----------------------------
*  Log unhandled exceptions raised by listener callbacks.


v1.4 (2018-07-03) - Event suppression
-------------------------------------
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


v1.3.10 (2018-02-05) - Do not crash under *Xephyr*
--------------------------------------------------
*  Do not crash when ``Xlib.display.Display.get_input_focus`` returns an
   integer, as it may when running under *Xephyr*. Thanks to *Eli Skeggs*!


v1.3.9 (2018-01-12) - Correctly handle the letter *A* on *OSX*
--------------------------------------------------------------
*  Corrected check for virtual key code when generating keyboard events on
   *OSX*. This fixes an issue where pressing *A* with *shift* explicitly pressed
   would still type a minuscule letter.


v1.3.8 (2017-12-08) - Do not crash on some keyboard layouts on *OSX*
--------------------------------------------------------------------
*  Fall back on a different method to retrieve the keyboard layout on *OSX*.
   This helps for some keyboard layouts, such as *Chinese*. Thanks to
   *haoflynet*!


v1.3.7 (2017-08-23) - *Xorg* corrections
----------------------------------------
*  Include mouse buttons up to *30* for *Xorg*.


v1.3.6 (2017-08-13) - *win32* corrections
-----------------------------------------
*  Corrected double delivery of fake keyboard events on *Windows*.
*  Corrected handling of synthetic unicode keys on *Windows*.


v1.3.5 (2017-06-07) - Corrected dependencies again
--------------------------------------------------
*  Reverted changes in *1.3.3*.
*  Corrected platform specifier for *Python 2* on *Linux*.


v1.3.4 (2017-06-05) - *Xorg* corrections
----------------------------------------
*  Corrected bounds check for values on *Xorg*.


v1.3.3 (2017-06-05) - Make dependencies non-optional
----------------------------------------------------
*  Made platform dependencies non-optional.


v1.3.2 (2017-05-15) - Fix for button click on Mac
-------------------------------------------------
*  Corrected regression from previous release where button clicks would
   crash the *Mac* mouse listener.


v1.3.1 (2017-05-12) - Fixes for unknown buttons on Linux
--------------------------------------------------------
*  Fall back on `Button.unknown` for unknown mouse buttons in *Xorg* mouse
   listener.


v1.3 (2017-04-10) - Platform specific features
----------------------------------------------
*  Added ability to stop event propagation on *Windows*. This will prevent
   events from reaching other applications.
*  Added ability to ignore events on *Windows*. This is a workaround for systems
   where the keyboard monitor interferes with normal keyboard events.
*  Added ability to modify events on *OSX*. This allows intercepting and
   altering input events before they reach other applications.
*  Corrected crash on *OSX* when some types of third party input sources are
   installed.


v1.2 (2017-01-06) - Improved error handling
-------------------------------------------
*  Allow catching exceptions thrown from listener callbacks. This changes the
   API, as joining a listener now potentially raises unhandled exceptions,
   and unhandled exceptions will stop listeners.
*  Added support for the numeric keypad on *Linux*.
*  Improved documentation.
*  Thanks to *jollysean* and *gilleswijnker* for their input!


v1.1.7 (2017-01-02) - Handle middle button on Windows
-----------------------------------------------------
*  Listen for and dispatch middle button mouse clicks on *Windows*.


v1.1.6 (2016-11-24) - Corrected context manager for pressing keys
-----------------------------------------------------------------
*  Corrected bug in ``pynput.keyboard.Controller.pressed`` which caused it to
   never release the key. Many thanks to Toby Southwell!


v1.1.5 (2016-11-17) - Corrected modifier key combinations on Linux
------------------------------------------------------------------
*  Corrected handling of modifier keys to allow them to be composable on
   *Linux*.


v1.1.4 (2016-10-30) - Small bugfixes
------------------------------------
*  Corrected error generation when ``GetKeyboardState`` fails.
*  Make sure to apply shift state to borrowed keys on *X*.
*  Use *pylint*.


v1.1.3 (2016-09-27) - Changed Xlib backend library
--------------------------------------------------
*  Changed *Xlib* library.


v1.1.2 (2016-09-26) - Added missing type for Python 2
-----------------------------------------------------
*  Added missing ``LPDWORD`` for *Python 2* on *Windows*.


v1.1.1 (2016-09-26) - Fixes for listeners and controllers on Windows
--------------------------------------------------------------------
*  Corrected keyboard listener on *Windows*. Modifier keys and other keys
   changing the state of the keyboard are now handled correctly.
*  Corrected mouse click and release on *Windows*.
*  Corrected code samples.


v1.1 (2016-06-22) - Simplified usage on Linux
---------------------------------------------
*  Propagate import errors raised on Linux to help troubleshoot missing
   ``Xlib`` module.
*  Declare ``python3-xlib`` as dependency on *Linux* for *Python 3*.


v1.0.6 (2016-04-19) - Universal wheel
-------------------------------------
*  Make sure to build a universal wheel for all python versions.


v1.0.5 (2016-04-11) - Fixes for dragging on OSX
-----------------------------------------------
*  Corrected dragging on *OSX*.
*  Added scroll speed constant for *OSX* to correct slow scroll speed.


v1.0.4 (2016-04-11) - Fixes for clicking and scrolling on Windows
-----------------------------------------------------------------
*  Corrected name of mouse input field when sending click and scroll events.


v1.0.3 (2016-04-05) - Fixes for Python 3 on Windows
---------------------------------------------------
*  Corrected use of ``ctypes`` on Windows.


v1.0.2 (2016-04-03) - Fixes for thread identifiers
--------------------------------------------------
*  Use thread identifiers to identify threads, not Thread instances.


v1.0.1 (2016-04-03) - Fixes for Python 3
----------------------------------------
*  Corrected bugs which prevented the library from being used on *Python 3*.


v1.0 (2016-02-28) - Stable Release
----------------------------------
*  Changed license to *LGPL*.
*  Corrected minor bugs and inconsistencies.
*  Corrected and extended documentation.


v0.6 (2016-02-08) - Keyboard Monitor
------------------------------------
*  Added support for monitoring the keyboard.
*  Corrected wheel packaging.
*  Corrected deadlock when stopping a listener in some cases on *X*.
*  Corrected key code constants on *Mac OSX*.
*  Do not intercept events on *Mac OSX*.


v0.5.1 (2016-01-26) - Do not die on dead keys
---------------------------------------------
*  Corrected handling of dead keys.
*  Corrected documentation.


v0.5 (2016-01-18) - Keyboard Modifiers
--------------------------------------
*  Added support for modifiers.


v0.4 (2015-12-22) - Keyboard Controller
---------------------------------------
*  Added keyboard controller.


v0.3 (2015-12-22) - Cleanup
---------------------------
*  Moved ``pynput.mouse.Controller.Button`` to top-level.


v0.2 (2015-10-28) - Initial Release
-----------------------------------
*  Support for controlling the mouse on *Linux*, *Mac OSX* and *Windows*.
*  Support for monitoring the mouse on *Linux*, *Mac OSX* and *Windows*.
