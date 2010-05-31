#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


import os
import urllib

from unic import unic
from normalizing import normpath


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
    if code_style:
        string = string.replace('_', ' ')
    parts = string.split()
    if len(parts) == 0:
        return ''
    elif len(parts) == 1 and code_style:
        parts = _splitCamelCaseString(parts[0])
    parts = [ part[0].upper() + part[1:] for part in parts if part != '' ]
    return ' '.join(parts)


def _splitCamelCaseString(string):
    parts = []
    current_part = []
    string = ' ' + string + ' '  # extra spaces make going through string easier
    for i in range(1, len(string)-1):
        # on 1st/last round prev/next is ' ' and char is 1st/last real char
        prev, char, next = string[i-1:i+2]
        if _isWordBoundary(prev, char, next):
            parts.append(''.join(current_part))
            current_part = [ char ]
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
    if len(sequence) == 0:
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


def get_link_path(target, base):
    """Returns a relative path to a target from a base. If base is an existing
    file, then its parent directory is considered. Otherwise, base is assumed
    to be a directory.

    Rationale: os.path.relpath is not available before Python 2.6
    """
    pathname =  _get_pathname(target, base)
    url = urllib.pathname2url(pathname.encode('UTF-8'))
    if os.path.isabs(pathname):
        pre = url.startswith('/') and 'file:' or 'file:///'
        url = pre + url
    # Want consistent url on all platforms/interpreters
    return url.replace('%5C', '/').replace('%3A', ':').replace('|', ':')

def _get_pathname(target, base):
    target = normpath(target)
    base = normpath(base)
    if os.path.isfile(base):
        base = os.path.dirname(base)
    if base == target:
        return os.path.basename(target)
    base_drive, base_path = os.path.splitdrive(base)
    # if in Windows and base and link on different drives
    if os.path.splitdrive(target)[0] != base_drive:
        return target
    common_len = len(_common_path(base, target))
    if base_path == os.sep:
        return target[common_len:]
    if common_len == len(base_drive) + len(os.sep):
        common_len -= len(os.sep)
    dirs_up = os.sep.join([os.pardir] * base[common_len:].count(os.sep))
    return os.path.join(dirs_up, target[common_len + len(os.sep):])


def _common_path(p1, p2):
    """Returns the longest path common to p1 and p2.

    Rationale: as os.path.commonprefix is character based, it doesn't consider
    path separators as such, so it may return invalid paths:
    commonprefix(('/foo/bar/', '/foo/baz.txt')) -> '/foo/ba' (instead of /foo)
    """
    while p1 and p2:
        if p1 == p2:
            return p1
        if len(p1) > len(p2):
            p1 = os.path.dirname(p1)
        else:
            p2 = os.path.dirname(p2)
    return ""
