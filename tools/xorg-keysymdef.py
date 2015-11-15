#!/usr/bin/env python
# coding: utf-8
# Copyright 2015 Moses Palmér
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
Converts <keysymdef.h> to Python mappings.
"""

import collections
import datetime
import re
import sys
import unicodedata


#: The regular expresion used to extract normal values; they are on the form:
#:
#:     #define XK_<name> <hex keysym> /* <unicode point> <character name> */
KEYSYM_RE = re.compile(r'''(?mx)
    # name
    \#define \s+ XK_([a-zA-Z0-9_]+)\s+

    # keysym
    0x([0-9a-fA-F]+)\s+

    # codepoint
    /\*\s* U\+([0-9a-fA-F]+)\s+.*?\*/

    # description, not present
    ()''')

#: The regular expresion used to extract dead key values; they are on the form:
#:
#:     #define XK_dead_<name> <hex keysym> [/* description */]
DEAD_KEYSYM_RE = re.compile(r'''(?mx)
    # name
    \#define \s+ XK_dead_([a-zA-Z0-9_]+)\s+

    # keysym
    0x([0-9a-fA-F]+)\s*

    # codepoint, not present
    ()

    # description
    (?:/\*(.*?)\*/)?''')

# A mapping from dead keys to their unicode codepoints
DEAD_CODEPOINTS = {
    name: '%04X' % ord(unicodedata.lookup(codepoint))
    for name, codepoint in {
        'abovecomma': 'COMBINING COMMA ABOVE RIGHT',
        'abovedot': 'COMBINING DOT ABOVE',
        'abovereversedcomma': 'COMBINING TURNED COMMA ABOVE',
        'abovering': 'COMBINING RING ABOVE',
        'aboveverticalline': 'COMBINING VERTICAL LINE ABOVE',
        'acute': 'COMBINING ACUTE ACCENT',
        'belowbreve': 'COMBINING BREVE BELOW',
        'belowcircumflex': 'COMBINING CIRCUMFLEX ACCENT BELOW',
        'belowcomma': 'COMBINING COMMA BELOW',
        'belowdiaeresis': 'COMBINING DIAERESIS BELOW',
        'belowdot': 'COMBINING DOT BELOW',
        'belowmacron': 'COMBINING MACRON BELOW',
        'belowring': 'COMBINING RING BELOW',
        'belowtilde': 'COMBINING TILDE BELOW',
        'belowverticalline': 'COMBINING VERTICAL LINE BELOW',
        'breve': 'COMBINING BREVE',
        'caron': 'COMBINING CARON',
        'cedilla': 'COMBINING CEDILLA',
        'circumflex': 'COMBINING CIRCUMFLEX ACCENT',
        'diaeresis': 'COMBINING DIAERESIS',
        'doubleacute': 'COMBINING DOUBLE ACUTE ACCENT',
        'doublegrave': 'COMBINING DOUBLE GRAVE ACCENT',
        'grave': 'COMBINING GRAVE ACCENT',
        'hook': 'COMBINING HOOK ABOVE',
        'horn': 'COMBINING HORN',
        'invertedbreve': 'COMBINING INVERTED BREVE BELOW',
        'iota': 'COMBINING GREEK YPOGEGRAMMENI',
        'longsolidusoverlay': 'COMBINING LONG SOLIDUS OVERLAY',
        'lowline': 'COMBINING LOW LINE',
        'macron': 'COMBINING MACRON',
        'ogonek': 'COMBINING OGONEK',
        'stroke': 'COMBINING SHORT STROKE OVERLAY',
        'tilde': 'COMBINING TILDE'}.items()}


def definitions():
    """Yields all keysym as the tuple ``(name, keysym, codepoint)``.

    If ``codepoint`` is ``None``, the definition is for a dead key with no
    unicode codepoint.
    """
    for line in sys.stdin:
        for regex in (KEYSYM_RE, DEAD_KEYSYM_RE):
            m = regex.search(line)
            if m:
                name, keysym, codepoint, description = m.groups()
                if codepoint:
                    # If the code point is specified, this keysym corresponds
                    # to a normal character
                    yield (
                        name,
                        (keysym, codepoint))

                elif not description or 'alias for' not in description:
                    # If we have no code point, this is a dead key unless it
                    # is an alias, in which case we ignore it
                    yield (
                        'dead_' + name,
                        (keysym, DEAD_CODEPOINTS.get(name, None)))

                break


def main():
    sys.stdout.write('''# coding: utf-8
# Copyright %d Moses Palmér
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

SYMBOLS = {
%s}

CHARS = {
    codepoint: name
    for name, (keysym, codepoint) in SYMBOLS.items()
    if codepoint}
''' % (
        datetime.date.today().year,
        ',\n'.join(
            '    \'%s\': (0x%s, %s)' % (
                    name,
                    keysym,
                    'u\'\\u%s\'' % codepoint if codepoint else None)
            for name, (keysym, codepoint) in definitions())))

main()
