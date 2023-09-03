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

import inspect
import os.path
import re
from itertools import takewhile
from pathlib import Path

from .charwidth import get_char_width
from .misc import seq2str2
from .robottypes import is_string
from .unic import safe_str


MAX_ERROR_LINES = 40
MAX_ASSIGN_LENGTH = 200
_MAX_ERROR_LINE_LENGTH = 78
_ERROR_CUT_EXPLN = '    [ Message content over the limit has been removed. ]'
_TAGS_RE = re.compile(r'\s*tags:(.*)', re.IGNORECASE)


def cut_long_message(msg):
    if MAX_ERROR_LINES is None:
        return msg
    lines = msg.splitlines()
    lengths = _count_line_lengths(lines)
    if sum(lengths) <= MAX_ERROR_LINES:
        return msg
    start = _prune_excess_lines(lines, lengths)
    end = _prune_excess_lines(lines, lengths, from_end=True)
    return '\n'.join(start + [_ERROR_CUT_EXPLN] + end)

def _prune_excess_lines(lines, lengths, from_end=False):
    if from_end:
        lines.reverse()
        lengths.reverse()
    ret = []
    total = 0
    limit = MAX_ERROR_LINES // 2
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
    available_lines = MAX_ERROR_LINES // 2 - used
    available_chars = available_lines * _MAX_ERROR_LINE_LENGTH - 3
    if len(line) > available_chars:
        if not from_end:
            line = line[:available_chars] + '...'
        else:
            line = '...' + line[-available_chars:]
    return line

def _count_line_lengths(lines):
    return [ _count_virtual_line_length(line) for line in lines ]

def _count_virtual_line_length(line):
    if not line:
        return 1
    lines, remainder = divmod(len(line), _MAX_ERROR_LINE_LENGTH)
    return lines if not remainder else lines + 1


def format_assign_message(variable, value, items=None, cut_long=True):
    formatter = {'$': safe_str, '@': seq2str2, '&': _dict_to_str}[variable[0]]
    value = formatter(value)
    if cut_long:
        value = cut_assign_value(value)
    decorated_items = ''.join(f'[{item}]' for item in items) if items else ''
    return f'{variable}{decorated_items} = {value}'

def _dict_to_str(d):
    if not d:
        return '{ }'
    return '{ %s }' % ' | '.join('%s=%s' % (safe_str(k), safe_str(d[k])) for k in d)


def cut_assign_value(value):
    if not is_string(value):
        value = safe_str(value)
    if len(value) > MAX_ASSIGN_LENGTH:
        value = value[:MAX_ASSIGN_LENGTH] + '...'
    return value


def get_console_length(text):
    return sum(get_char_width(char) for char in text)


def pad_console_length(text, width):
    if width < 5:
        width = 5
    diff = get_console_length(text) - width
    if diff > 0:
        text = _lose_width(text, diff+3) + '...'
    return _pad_width(text, width)

def _pad_width(text, width):
    more = width - get_console_length(text)
    return text + ' ' * more

def _lose_width(text, diff):
    lost = 0
    while lost < diff:
        lost += get_console_length(text[-1])
        text = text[:-1]
    return text


def split_args_from_name_or_path(name):
    """Split arguments embedded to name or path like ``Example:arg1:arg2``.

    The separator can be either colon ``:`` or semicolon ``;``. If both are used,
    the first one is considered to be the separator.
    """
    if os.path.exists(name):
        return os.path.abspath(name), []
    if isinstance(name, Path):
        name = str(name)
    index = _get_arg_separator_index_from_name_or_path(name)
    if index == -1:
        return name, []
    args = name[index+1:].split(name[index])
    name = name[:index]
    if os.path.exists(name):
        name = os.path.abspath(name)
    return name, args


def _get_arg_separator_index_from_name_or_path(name):
    colon_index = name.find(':')
    # Handle absolute Windows paths
    if colon_index == 1 and name[2:3] in ('/', '\\'):
        colon_index = name.find(':', colon_index+1)
    semicolon_index = name.find(';')
    if colon_index == -1:
        return semicolon_index
    if semicolon_index == -1:
        return colon_index
    return min(colon_index, semicolon_index)


def split_tags_from_doc(doc):
    doc = doc.rstrip()
    tags = []
    if not doc:
        return doc, tags
    lines = doc.splitlines()
    match = _TAGS_RE.match(lines[-1])
    if match:
        doc = '\n'.join(lines[:-1]).rstrip()
        tags = [tag.strip() for tag in match.group(1).split(',')]
    return doc, tags


def getdoc(item):
    return inspect.getdoc(item) or ''


def getshortdoc(doc_or_item, linesep='\n'):
    if not doc_or_item:
        return ''
    doc = doc_or_item if is_string(doc_or_item) else getdoc(doc_or_item)
    lines = takewhile(lambda line: line.strip(), doc.splitlines())
    return linesep.join(lines)
