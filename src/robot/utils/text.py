#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from unic import unic
from misc import seq2str2
from charwidth import get_char_width


_MAX_ASSIGN_LENGTH = 200
_MAX_ERROR_LINES = 40
_MAX_ERROR_LINE_LENGTH = 78
_ERROR_CUT_EXPLN = ('    [ Message content over the limit has been removed. ]')


def cut_long_message(msg):
    lines = msg.splitlines()
    lengths = _count_line_lenghts(lines)
    if sum(lengths) <= _MAX_ERROR_LINES:
        return msg
    start = _prune_excess_lines(lines, lengths)
    end = _prune_excess_lines(lines, lengths, True)
    return '\n'.join(start + [_ERROR_CUT_EXPLN] + end)

def _prune_excess_lines(lines, lengths, from_end=False):
    if from_end:
        lines.reverse()
        lengths.reverse()
    ret = []
    total = 0
    limit = _MAX_ERROR_LINES/2
    for line, length in zip(lines[:limit], lengths[:limit]):
        if total + length >= limit:
            ret.append(_cut_long_line(line, total, from_end))
            break
        total += length
        ret.append(line)
    if from_end:
        ret.reverse()
    return ret

def _cut_long_line(line, used, from_end):
    available_lines = _MAX_ERROR_LINES/2 - used
    available_chars = available_lines * _MAX_ERROR_LINE_LENGTH - 3
    if len(line) > available_chars:
        if not from_end:
            line = line[:available_chars] + '...'
        else:
            line = '...' + line[-available_chars:]
    return line

def _count_line_lenghts(lines):
    return [ _count_virtual_line_length(line) for line in lines ]

def _count_virtual_line_length(line):
    length = len(line) / _MAX_ERROR_LINE_LENGTH
    if not len(line) % _MAX_ERROR_LINE_LENGTH == 0 or len(line) == 0:
        length += 1
    return length


def format_assign_message(variable, value, cut_long=True):
    value = unic(value) if variable.startswith('$') else seq2str2(value)
    if cut_long and len(value) > _MAX_ASSIGN_LENGTH:
        value = value[:_MAX_ASSIGN_LENGTH] + '...'
    return '%s = %s' % (variable, value)


def get_console_length(text):
    return sum(get_char_width(char) for char in text)


def pad_console_length(text, width):
    if width < 5:
        width = 5
    diff = get_console_length(text) - width
    if diff <= 0:
        return _pad_width(text, width)
    return _pad_width(_lose_width(text, diff+3)+'...', width)

def _pad_width(text, width):
    more = width - get_console_length(text)
    return text + ' ' * more

def _lose_width(text, diff):
    lost = 0
    while lost < diff:
        lost += get_console_length(text[-1])
        text = text[:-1]
    return text
