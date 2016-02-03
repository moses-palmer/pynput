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


def lookup(name):
    """Looks up a named unicode character.

    If it does not exist, ``None`` is returned, otherwise the code point is
    returned.

    :return: a hex number as a string or ``None``
    """
    try:
        return '%04X' % ord(unicodedata.lookup(name))
    except KeyError:
        return None

# A mapping from dead keys to their unicode codepoints
DEAD_CODEPOINTS = {
    name: (
        lookup('COMBINING ' + codepoint),
        lookup(codepoint))
    for name, codepoint in {
        'abovecomma': 'COMMA ABOVE RIGHT',
        'abovedot': 'DOT ABOVE',
        'abovereversedcomma': 'TURNED COMMA ABOVE',
        'abovering': 'RING ABOVE',
        'aboveverticalline': 'VERTICAL LINE ABOVE',
        'acute': 'ACUTE ACCENT',
        'belowbreve': 'BREVE BELOW',
        'belowcircumflex': 'CIRCUMFLEX ACCENT BELOW',
        'belowcomma': 'COMMA BELOW',
        'belowdiaeresis': 'DIAERESIS BELOW',
        'belowdot': 'DOT BELOW',
        'belowmacron': 'MACRON BELOW',
        'belowring': 'RING BELOW',
        'belowtilde': 'TILDE BELOW',
        'belowverticalline': 'VERTICAL LINE BELOW',
        'breve': 'BREVE',
        'caron': 'CARON',
        'cedilla': 'CEDILLA',
        'circumflex': 'CIRCUMFLEX ACCENT',
        'diaeresis': 'DIAERESIS',
        'doubleacute': 'DOUBLE ACUTE ACCENT',
        'doublegrave': 'DOUBLE GRAVE ACCENT',
        'grave': 'GRAVE ACCENT',
        'hook': 'HOOK ABOVE',
        'horn': 'HORN',
        'invertedbreve': 'INVERTED BREVE BELOW',
        'iota': 'GREEK YPOGEGRAMMENI',
        'longsolidusoverlay': 'LONG SOLIDUS OVERLAY',
        'lowline': 'LOW LINE',
        'macron': 'MACRON',
        'ogonek': 'OGONEK',
        'stroke': 'SHORT STROKE OVERLAY',
        'tilde': 'TILDE'}.items()}


def definitions(data):
    """Yields all keysym as the tuple ``(name, keysym, (first, second))``.

    ``(first, second))`` is a tuple of codepoints. The first value is the one
    to use in the lookup table, and the second one is used only by dead keys to
    indicate the non-combining version.

    If a codepoint is ``None``, the definition is for a dead key with no
    unicode codepoint.
    """
    for line in data:
        for regex in (KEYSYM_RE, DEAD_KEYSYM_RE):
            m = regex.search(line)
            if m:
                name, keysym, codepoint, description = m.groups()
                if codepoint:
                    # If the code point is specified, this keysym corresponds
                    # to a normal character
                    yield (
                        name,
                        (keysym, (codepoint, codepoint)))

                elif not description or 'alias for' not in description:
                    # If we have no code point, this is a dead key unless it
                    # is an alias, in which case we ignore it
                    yield (
                        'dead_' + name,
                        (keysym, DEAD_CODEPOINTS.get(name, (None, None))))

                break


def main():
    data = sys.stdin.read().splitlines()
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

DEAD_KEYS = {
%s}

CHARS = {
    codepoint: name
    for name, (keysym, codepoint) in SYMBOLS.items()
    if codepoint}

KEYSYMS = {
    keysym: name
    for name, (keysym, codepoint) in SYMBOLS.items()
    if codepoint}
''' % (
        datetime.date.today().year,
        ',\n'.join(
            '    \'%s\': (0x%s, %s)' % (
                    name,
                    keysym,
                    'u\'\\u%s\'' % first if first else None)
            for name, (keysym, (first, second)) in definitions(data)),
        ',\n'.join(
            '    %s: %s' % (
                    'u\'\\u%s\'' % first,
                    'u\'\\u%s\'' % second)
            for name, (keysym, (first, second)) in definitions(data)
            if first and second and first != second)))

main()
