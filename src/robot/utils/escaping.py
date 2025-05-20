#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re

_CONTROL_WORDS = frozenset(("ELSE", "ELSE IF", "AND", "WITH NAME", "AS"))
_SEQUENCES_TO_BE_ESCAPED = ("\\", "${", "@{", "%{", "&{", "*{", "=")


def escape(item):
    if not isinstance(item, str):
        return item
    if item in _CONTROL_WORDS:
        return "\\" + item
    for seq in _SEQUENCES_TO_BE_ESCAPED:
        if seq in item:
            item = item.replace(seq, "\\" + seq)
    return item


def glob_escape(item):
    # Python 3.4+ has `glob.escape()` but it has special handling for drives
    # that we don't want.
    for char in "[*?":
        if char in item:
            item = item.replace(char, f"[{char}]")
    return item


class Unescaper:
    _escape_sequences = re.compile(
        r"""
        (\\+)                # escapes
        (n|r|t               # n, r, or t
         |x[0-9a-fA-F]{2}    # x+HH
         |u[0-9a-fA-F]{4}    # u+HHHH
         |U[0-9a-fA-F]{8}    # U+HHHHHHHH
        )?                   # optionally
        """,
        re.VERBOSE,
    )

    def __init__(self):
        self._escape_handlers = {
            "": lambda value: value,
            "n": lambda value: "\n",
            "r": lambda value: "\r",
            "t": lambda value: "\t",
            "x": self._hex_to_unichr,
            "u": self._hex_to_unichr,
            "U": self._hex_to_unichr,
        }

    def _hex_to_unichr(self, value):
        ordinal = int(value, 16)
        # No Unicode code points above 0x10FFFF
        if ordinal > 0x10FFFF:
            return "U" + value
        # `chr` only supports ordinals up to 0xFFFF on narrow Python builds.
        # This may not be relevant anymore.
        if ordinal > 0xFFFF:
            return eval(rf"'\U{ordinal:08x}'")
        return chr(ordinal)

    def unescape(self, item):
        if not isinstance(item, str) or "\\" not in item:
            return item
        return self._escape_sequences.sub(self._handle_escapes, item)

    def _handle_escapes(self, match):
        escapes, text = match.groups()
        half, is_escaped = divmod(len(escapes), 2)
        escapes = escapes[:half]
        text = text or ""
        if is_escaped:
            marker, value = text[:1], text[1:]
            text = self._escape_handlers[marker](value)
        return escapes + text


unescape = Unescaper().unescape


def split_from_equals(value):
    from robot.variables import VariableMatches

    if not isinstance(value, str) or "=" not in value:
        return value, None
    matches = VariableMatches(value, ignore_errors=True)
    if not matches and "\\" not in value:
        return tuple(value.split("=", 1))
    try:
        index = _find_split_index(value, matches)
    except ValueError:
        return value, None
    return value[:index], value[index + 1 :]


def _find_split_index(string, matches):
    remaining = string
    relative_index = 0
    for match in matches:
        try:
            return _find_split_index_from_part(match.before) + relative_index
        except ValueError:
            remaining = match.after
            relative_index += match.end
    return _find_split_index_from_part(remaining) + relative_index


def _find_split_index_from_part(string):
    index = 0
    while "=" in string[index:]:
        index += string[index:].index("=")
        if _not_escaping(string[:index]):
            return index
        index += 1
    raise ValueError


def _not_escaping(name):
    backslashes = len(name) - len(name.rstrip("\\"))
    return backslashes % 2 == 0
