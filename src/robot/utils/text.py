#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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


from robottypes import is_str
from unic import unic


_MAX_ASSIGN_LENGTH = 200
_MAX_ERROR_LINES = 20
_MAX_ERROR_LINE_LENGTH = 78
_ERROR_CUT_EXPLN = ('    [ Message content over the limit has been removed. ]')


def cut_long_message(msg):
    if not is_str(msg):
        msg = unic(msg)
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


# TODO: rename _msg -> _message
def cut_long_assign_msg(msg):
    if not is_str(msg):
        msg = unic(msg)
    if len(msg) <= _MAX_ASSIGN_LENGTH:
        return msg
    return msg[:_MAX_ASSIGN_LENGTH] + '...'


def wrap(text, width, indent=0):
    """Wraps given text so that it fits into given width with optional indent.

    Preserves existing line breaks and most spaces in the text. Expects that
    existing line breaks are posix newlines (\n).

    Based on a recipe from ActiveState Python Cookbook at
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
    """
    text = reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )
    if not indent > 0:
        return text
    pre = ' ' * indent
    joiner = '\n' + pre
    return pre + joiner.join(text.splitlines())
