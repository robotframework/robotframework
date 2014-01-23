#  Copyright 2008-2014 Nokia Solutions and Networks
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


_SEQS_TO_BE_ESCAPED = ('\\', '${', '@{', '%{', '&{', '*{', '=')


def escape(item):
    if not isinstance(item, basestring):
        return item
    for seq in _SEQS_TO_BE_ESCAPED:
        if seq in item:
            item = item.replace(seq, '\\' + seq)
    return item


def unescape(item):
    if not (isinstance(item, basestring) and '\\' in item):
        return item
    return Unescaper().unescape(item)


class Unescaper(object):
    _escaped = re.compile(r'(\\+)([^\\]*)')

    def unescape(self, string):
        return ''.join(self._yield_unescaped(string))

    def _yield_unescaped(self, string):
        while '\\' in string:
            finder = EscapeFinder(string)
            yield finder.before + finder.backslashes
            if finder.escaped and finder.text:
                yield self._unescape(finder.text)
            else:
                yield finder.text
            string = finder.after
        yield string

    def _unescape(self, text):
        try:
            escape = str(text[0])
        except UnicodeError:
            return text
        try:
            unescaper = getattr(self, '_unescaper_for_' + escape)
        except AttributeError:
            return text
        else:
            return unescaper(text[1:])

    def _unescaper_for_n(self, text):
        if text.startswith(' '):
            text = text[1:]
        return '\n' + text

    def _unescaper_for_r(self, text):
        return '\r' + text

    def _unescaper_for_t(self, text):
        return '\t' + text

    def _unescaper_for_x(self, text):
        return self._unescape_character(text, 2, 'x')

    def _unescaper_for_u(self, text):
        return self._unescape_character(text, 4, 'u')

    def _unescaper_for_U(self, text):
        return self._unescape_character(text, 8, 'U')

    def _unescape_character(self, text, length, escape):
        try:
            char = self._get_character(text[:length], length)
        except ValueError:
            return escape + text
        else:
            return char + text[length:]

    def _get_character(self, text, length):
        if len(text) < length or not text.isalnum():
            raise ValueError
        ordinal = int(text, 16)
        # No Unicode code points above 0x10FFFF
        if ordinal > 0x10FFFF:
            raise ValueError
        # unichr only supports ordinals up to 0xFFFF with narrow Python builds
        if ordinal > 0xFFFF:
            return eval("u'\\U%08x'" % ordinal)
        return unichr(ordinal)


class EscapeFinder(object):
    _escaped = re.compile(r'(\\+)([^\\]*)')

    def __init__(self, string):
        res = self._escaped.search(string)
        self.before = string[:res.start()]
        escape_chars = len(res.group(1))
        self.backslashes = '\\' * (escape_chars // 2)
        self.escaped = bool(escape_chars % 2)
        self.text = res.group(2)
        self.after = string[res.end():]
