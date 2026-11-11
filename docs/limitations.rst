Platform limitations
--------------------

*pynput* aims at providing a unified *API* for all supported platforms. In some
cases, however, that is not entirely possible.


Linux
~~~~~

On *Linux*, *pynput* uses *libei*, *X* or *uinput*.

When running under *X*, the following must be true:

*  An *X server* must be running.

*  The environment variable ``$DISPLAY`` must be set.

When running under *uinput*, the following must be true:

*  You must run your script as root, to that is has the required permissions
   for *uinput*.

Also please note that the ``injected`` flag is not supported for *uinput*.

The latter requirement for *X* means that running *pynput* over *SSH* generally
will not work. To work around that, make sure to set ``$DISPLAY``:

.. code-block:: bash

    $ DISPLAY=:0 python -c 'import pynput'

Please note that the value ``DISPLAY=:0`` is just an example. To find the
actual value, please launch a terminal application from your desktop
environment and issue the command ``echo $DISPLAY``.

When running under *Wayland*, the ``libei`` backend is used. It requires the
following:

*  The compositor must provide the ``org.freedesktop.portal.RemoteDesktop``
   portal. *KDE* and *GNOME* do; *wlroots* based compositors such as *sway*
   and *river*, and others such as *niri*, currently do not, and there the
   ``xorg`` backend is used instead.

*  The packages ``jeepney`` and ``python-libei`` must be installed, along with
   the system library *libei*. Installing *pynput* as ``pynput[libei]`` pulls
   these in.

*  The user must grant permission, in a dialog the compositor itself presents.
   The grant is remembered, so this happens once rather than on every run; see
   ``$PYNPUT_LIBEI_RESTORE_TOKEN`` below.

This backend has the following limitations:

*  **Input cannot be monitored.** The portal used here grants the right to
   inject input, not to observe it; monitoring requires the separate
   ``org.freedesktop.portal.InputCapture`` portal, which is not implemented.
   Creating a listener succeeds, but starting it raises
   ``NotImplementedError``.

*  **The pointer position cannot be read** unless this process set it. There is
   no way to ask the compositor where the pointer is, and reporting a
   plausible but wrong coordinate would be worse than refusing, so
   :attr:`pynput.mouse.Controller.position` raises ``NotImplementedError``
   until it has been assigned. :meth:`pynput.mouse.Controller.move` does not
   need it, since it sends a relative motion.

*  **Coordinates are logical pixels**, which is the space the compositor works
   in. On a display scaled by 125%, a screen 2560 pixels wide is 2048 logical
   pixels wide, and a coordinate outside that range raises ``ValueError``
   rather than being clamped.

*  **Typing characters requires the ``xkbcommon`` package.** *libei*, like the
   kernel, identifies keys by position rather than by the character they
   produce. The compositor supplies its keyboard layout, but interpreting it
   needs *libxkbcommon*; without it, keys such as :attr:`pynput.keyboard.Key`
   members still work and characters raise ``InvalidKeyException``.

Also please note that the ``injected`` flag is not supported for ``libei``,
since there is no listener to report it.

The environment variable ``$PYNPUT_LIBEI_RESTORE_TOKEN`` sets the file in which
the permission grant is stored, which defaults to
``$XDG_DATA_HOME/pynput/libei-restore-token``. Setting it to an empty value
stops the grant being stored, at the cost of a permission dialog on every run.

To use ``Xwayland`` instead, which provides limited functionality, force the
``xorg`` backend. Note that you will then only exchange input events with
applications running under that emulator.


macOS
~~~~~

Recent versions of *macOS* restrict monitoring of the keyboard for security
reasons. For that reason, one of the following must be true:

*  The process must run as root.

*  Your application must be white listed under *Enable access for assistive
   devices*. Note that this might require that you package your application,
   since otherwise the entire *Python* installation must be white listed.

*  On versions after *Mojave*, you may also need to whitelist your terminal
   application if running your script from a terminal.

Please note that this does not apply to monitoring of the mouse or trackpad.

All listener classes have the additional attribute ``IS_TRUSTED``, which is
``True`` if no permissions are lacking.


Windows
~~~~~~~

On *Windows*, virtual events sent by *other* processes may not be received.
This library takes precautions, however, to dispatch any virtual events
generated to all currently running listeners of the current process.

Furthermore, sending key press events will properly propagate to the rest of
the system, but the operating system does not consider the buttons to be truly
*pressed*. This means that key press events will not be continuously emitted as
when holding down a physical key, and certain key sequences, such as *shift*
pressed while pressing arrow keys, do not work as expected.
