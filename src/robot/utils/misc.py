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

import inspect
import sys

from .unic import unic


def printable_name(string, code_style=False):
    """Generates and returns printable name from the given string.

    Examples:
    'simple'           -> 'Simple'
    'name with spaces' -> 'Name With Spaces'
    'more   spaces'    -> 'More Spaces'
    'Cases AND spaces' -> 'Cases AND Spaces'
    ''                 -> ''

    If 'code_style' is True:

    'mixedCAPSCamel'   -> 'Mixed CAPS Camel'
    'camelCaseName'    -> 'Camel Case Name'
    'under_score_name' -> 'Under Score Name'
    'under_and space'  -> 'Under And Space'
    'miXed_CAPS_nAMe'  -> 'MiXed CAPS NAMe'
    ''                 -> ''
    """
    if code_style and '_' in string:
        string = string.replace('_', ' ')
    parts = string.split()
    if not parts:
        return ''
    if code_style and len(parts) == 1:
        parts = _splitCamelCaseString(parts[0])
    return ' '.join(part[0].upper() + part[1:] for part in parts if part != '')


def _splitCamelCaseString(string):
    parts = []
    current_part = []
    string = ' ' + string + ' '  # extra spaces make going through string easier
    for i in range(1, len(string)-1):
        # on 1st/last round prev/next is ' ' and char is 1st/last real char
        prev, char, next = string[i-1:i+2]
        if _isWordBoundary(prev, char, next):
            parts.append(''.join(current_part))
            current_part = [char]
        else:
            current_part.append(char)
    parts.append(''.join(current_part))   # append last part
    return parts


def _isWordBoundary(prev, char, next):
    if char.isupper():
        return (prev.islower() or next.islower()) and prev.isalnum()
    if char.isdigit():
        return prev.isalpha()
    return prev.isdigit()


def plural_or_not(item):
    count = item if isinstance(item, (int, long)) else len(item)
    return '' if count == 1 else 's'


def seq2str(sequence, quote="'", sep=', ', lastsep=' and '):
    """Returns sequence in format 'item 1', 'item 2' and 'item 3'"""
    quote_elem = lambda string: quote + unic(string) + quote
    if not sequence:
        return ''
    if len(sequence) == 1:
        return quote_elem(sequence[0])
    elems = [quote_elem(s) for s in sequence[:-2]]
    elems.append(quote_elem(sequence[-2]) + lastsep + quote_elem(sequence[-1]))
    return sep.join(elems)


def seq2str2(sequence):
    """Returns sequence in format [ item 1 | item 2 | ... ] """
    if not sequence:
        return '[ ]'
    return '[ %s ]' % ' | '.join(unic(item) for item in sequence)


def getdoc(item):
    doc = inspect.getdoc(item) or u''
    if isinstance(doc, unicode):
        return doc
    try:
        return doc.decode('UTF-8')
    except UnicodeDecodeError:
        return unic(doc)


# On IronPython sys.stdxxx.isatty() always returns True
if sys.platform != 'cli':

    def isatty(stream):
        return hasattr(stream, 'isatty') and stream.isatty()

else:

    from ctypes import windll

    _HANDLE_IDS = {sys.__stdout__ : -11, sys.__stderr__ : -12}
    _CONSOLE_TYPE = 2

    def isatty(stream):
        if stream not in _HANDLE_IDS:
            return False
        handle = windll.kernel32.GetStdHandle(_HANDLE_IDS[stream])
        return windll.kernel32.GetFileType(handle) == _CONSOLE_TYPE
