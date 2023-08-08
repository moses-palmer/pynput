# coding=utf-8
# pynput
# Copyright (C) 2015-2022 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
The main *pynput* module.

This module imports ``keyboard`` and ``mouse``.
"""

def _logger(cls):
    """Creates a logger with a name suitable for a specific class.

    This function takes into account that implementations for classes reside in
    platform dependent modules, and thus removes the final part of the module
    name.

    :param type cls: The class for which to create a logger.

    :return: a logger
    """
    import logging
    return logging.getLogger('{}.{}'.format(
        '.'.join(cls.__module__.split('.', 2)[:2]),
        cls.__name__))


from . import keyboard
from . import mouse
