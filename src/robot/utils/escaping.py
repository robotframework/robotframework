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

import re


_ESCAPE_RE = re.compile(r'(\\+)([^\\]{0,2})')   # escapes and nextchars
_SEQS_TO_BE_ESCAPED = ('\\', '${', '@{', '%{', '&{', '*{' , '=')


def escape(item):
    if not isinstance(item, basestring):
        return item
    for seq in _SEQS_TO_BE_ESCAPED:
        if seq in item:
            item = item.replace(seq, '\\' + seq)
    return item


def unescape(item):
    if not isinstance(item, basestring):
        return item
    result = []
    unprocessed = item
    while True:
        res = _ESCAPE_RE.search(unprocessed)
        # If no escapes found append string to result and exit loop
        if res is None:
            result.append(unprocessed)
            break
        # Split string to pre match, escapes, nextchars and unprocessed parts
        # (e.g. '<pre><esc><nc><unproc>') where nextchars contains 0-2 chars
        # and unprocessed may contain more escapes. Pre match part contains
        # no escapes can is appended directly to result.
        result.append(unprocessed[:res.start()])
        escapes = res.group(1)
        nextchars = res.group(2)
        unprocessed = unprocessed[res.end():]
        # Append every second escape char to result
        result.append('\\' * (len(escapes) / 2))
        # Handle '\n', '\r' and '\t'. Note that both '\n' and '\n ' are
        # converted to '\n'
        if len(escapes) % 2 == 0 or len(nextchars) == 0 \
                    or nextchars[0] not in ['n','r','t']:
            result.append(nextchars)
        elif nextchars[0] == 'n':
            if len(nextchars) == 1 or nextchars[1] == ' ':
                result.append('\n')
            else:
                result.append('\n' + nextchars[1])
        elif nextchars[0] == 'r':
            result.append('\r' + nextchars[1:])
        else:
            result.append('\t' + nextchars[1:])
    return ''.join(result)
