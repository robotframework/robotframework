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

from datetime import date, datetime, timedelta
from decimal import Decimal


STANDARD_TYPE_DOCS = {
    bool: '''\
Strings ``TRUE``, ``YES``, ``ON`` and ``1`` are converted to ``True``,
the empty string as well as ``FALSE``, ``NO``, ``OFF`` and ``0``
are converted to ``False``, and the string ``NONE`` is converted
to ``None``. Other strings and all non-string arguments are
passed as-is, allowing keywords to handle them specially if
needed. All string comparisons are case-insensitive.

Examples: ``TRUE`` (converted to ``True``), ``off`` (converted to ``False``,
``example`` (used as-is)
''',
    int: '''\
Conversion is done using Python's ``int`` built-in function. Floating point
numbers are converted only if they can be represented as integers exactly. 
For example, ``1.0`` is accepted and ``1.1`` is not.

Starting from RF 4.1, it is possible to use hexadecimal, octal and binary
numbers by prefixing values with ``0x``, ``0o`` and ``0b``, respectively.

Starting from RF 4.1, spaces and underscores can be used as visual separators
for digit grouping purposes.

Examples: ``42``, ``-1``, ``0b1010``, ``10 000 000``, ``0xBAD_C0FFEE`` 
''',
    float: 'TODO',
    Decimal: 'TODO',
    str: 'TODO',
    bytes: 'TODO',
    bytearray: 'Set below to same value as `bytes`.',
    datetime: 'TODO',
    date: 'TODO',
    timedelta: 'TODO',
    type(None): 'TODO',
    list: 'TODO',
    tuple: 'TODO',
    dict: 'TODO',
    set: 'TODO',
    frozenset: 'TODO'
}

STANDARD_TYPE_DOCS[bytearray] = STANDARD_TYPE_DOCS[bytes]
