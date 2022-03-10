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

from operator import add, sub
import re

from .robottypes import is_integer
from .unic import safe_str


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
    if code_style and len(parts) == 1 \
            and not (string.isalpha() and string.islower()):
        parts = _split_camel_case(parts[0])
    return ' '.join(part[0].upper() + part[1:] for part in parts)


def _split_camel_case(string):
    tokens = []
    token = []
    for prev, char, next in zip(' ' + string, string, string[1:] + ' '):
        if _is_camel_case_boundary(prev, char, next):
            if token:
                tokens.append(''.join(token))
            token = [char]
        else:
            token.append(char)
    if token:
        tokens.append(''.join(token))
    return tokens


def _is_camel_case_boundary(prev, char, next):
    if prev.isdigit():
        return not char.isdigit()
    if char.isupper():
        return next.islower() or prev.isalpha() and not prev.isupper()
    return char.isdigit()


def plural_or_not(item):
    count = item if is_integer(item) else len(item)
    return '' if count in (1, -1) else 's'


def seq2str(sequence, quote="'", sep=', ', lastsep=' and '):
    """Returns sequence in format `'item 1', 'item 2' and 'item 3'`."""
    sequence = [f'{quote}{safe_str(item)}{quote}' for item in sequence]
    if not sequence:
        return ''
    if len(sequence) == 1:
        return sequence[0]
    last_two = lastsep.join(sequence[-2:])
    return sep.join(sequence[:-2] + [last_two])


def seq2str2(sequence):
    """Returns sequence in format `[ item 1 | item 2 | ... ]`."""
    if not sequence:
        return '[ ]'
    return '[ %s ]' % ' | '.join(safe_str(item) for item in sequence)


def test_or_task(text, rpa=False):
    """Replaces `{test}` in `text` with `test` or `task` depending on `rpa`."""
    def replace(match):
        test = match.group(1)
        if not rpa:
            return test
        upper = [c.isupper() for c in test]
        return ''.join(c.upper() if up else c for c, up in zip('task', upper))
    return re.sub('{(test)}', replace, text, flags=re.IGNORECASE)


def isatty(stream):
    # first check if buffer was detached
    if hasattr(stream, 'buffer') and stream.buffer is None:
        return False
    if not hasattr(stream, 'isatty'):
        return False
    try:
        return stream.isatty()
    except ValueError:    # Occurs if file is closed.
        return False
