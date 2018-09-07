#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
"""
Converts virtual key codes from <winuser.h> to Python definitions.
"""

import datetime
import re
import sys
import unicodedata


#: The regular expresion used to extract virtual key codes; they are on the
#: form:
#:
#:     #define VK_<name> <hex vk>
VK_RE = re.compile(r'''(?mx)
    # name
    \#define \s+ VK_([a-zA-Z0-9_]+)\s+

    # vk
    0x([0-9a-fA-F]+)\s*

    # Discard rest of line
    .*''')


def definitions(data):
    """Yields all virtual key codes as the tuple ``(name, vk)``.
    """
    for line in data:
        m = VK_RE.search(line)
        if not m:
            continue

        name, vk = m.groups()
        yield (name, int(vk, 16))


def main():
    data = sys.stdin.read().splitlines()
    sys.stdout.write('''# coding: utf-8
# pynput
# Copyright (C) 2015-2018-%d Moses Palmér
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

# pylint: disable=C0111,C0302

%s
''' % (
        datetime.date.today().year,
        '\n'.join(
            '%s = %d' % (name, vk)
            for name, vk in definitions(data))))

main()
