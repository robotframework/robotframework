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

from collections.abc import Mapping, Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

try:
    from types import NoneType
except ImportError:  # Python < 3.10
    NoneType = type(None)

from robot.utils import Secret

STANDARD_TYPE_DOCS = {
    Any: """\
Any value is accepted. No conversion is done.
""",
    object: """\
Any value is accepted. No conversion is done.
""",
    bool: """\
Strings ``TRUE``, ``YES``, ``ON``, ``1`` and possible localization specific "true
strings" are converted to Boolean ``True``, the empty string, strings ``FALSE``,
``NO``, ``OFF`` and ``0`` and possibly localization specific "false strings"
are converted to Boolean ``False``, and the string ``NONE`` is converted to
the Python ``None`` object. Other strings and all other values are passed as-is,
allowing keywords to handle them specially if needed. All string comparisons are
case-insensitive.

Examples: ``TRUE`` (converted to ``True``), ``off`` (converted to ``False``),
``example`` (used as-is)
""",
    int: """\
Conversion is done using Python's [https://docs.python.org/library/functions.html#int|int]
built-in function. Floating point
numbers are accepted only if they can be represented as integers exactly.
For example, ``1.0`` is accepted and ``1.1`` is not.

It is possible to use hexadecimal, octal and binary numbers by prefixing values
with ``0x``, ``0o`` and ``0b``, respectively. Spaces and underscores can be used
as visual separators for digit grouping purposes.

Examples: ``42``, ``-1``, ``0b1010``, ``10 000 000``, ``0xBAD_C0FFEE``
""",
    float: """\
Conversion is done using Python's
[https://docs.python.org/library/functions.html#float|float] built-in function.

Spaces and underscores can be used as visual separators for digit grouping purposes.

Examples: ``3.14``, ``2.9979e8``, ``10 000.000 01``
""",
    Decimal: """\
Conversion is done using Python's
[https://docs.python.org/library/decimal.html#decimal.Decimal|Decimal] class.

Spaces and underscores can be used as visual separators for digit grouping purposes.

Examples: ``3.14``, ``10 000.000 01``
""",
    str: """\
All arguments are converted to Unicode strings.

Most values are converted simply by using ``str(value)``. An exception is that
bytes are mapped directly to Unicode code points with same ordinals. This means
that, for example, ``b"hyv\\xe4"`` becomes ``"hyvä"``.

Converting bytes specially is new Robot Framework 7.4.
""",
    bytes: """\
Strings are converted to bytes so that each Unicode code point
below 256 is directly mapped to a matching byte. Higher code
points are not allowed. Robot Framework's ``\\xHH`` escape syntax is
convenient with bytes having non-printable values.

Examples: ``good``, ``hyvä`` (same as ``hyv\\xE4``), ``\\x00`` (the null byte)

Integers and sequences of integers are converted to matching bytes directly.
They must be in range 0-255.

Examples: ``0`` (converted to the null byte), ``[82, 70]`` (converted to ``RF``)

Support for integers and sequences of integers is new in Robot Framework 7.4.
""",
    bytearray: "Set below to same value as `bytes`.",
    datetime: """\
String timestamps are expected to be in
[https://en.wikipedia.org/wiki/ISO_8601|ISO 8601] like
format ``YYYY-MM-DD hh:mm:ss.mmmmmm``, where any non-digit
character can be used as a separator or separators can be
omitted altogether. Additionally, only the date part is
mandatory, all possibly missing time components are considered
to be zeros.

A special values ``NOW`` and ``TODAY`` (case-insensitive) can be used to get
the current local ``datetime``. This is new in Robot Framework 7.3.

Integers and floats are considered to represent seconds since
the [https://en.wikipedia.org/wiki/Unix_time|Unix epoch].

Examples: ``2022-02-09T16:39:43.632269``, ``20220209 16:39``,
``now``, ``${1644417583.632269}`` (Epoch time)
""",
    date: """\
String timestamps are expected to be in
[https://en.wikipedia.org/wiki/ISO_8601|ISO 8601] like date format
``YYYY-MM-DD``, where any non-digit character can be used as a separator
or separators can be omitted altogether. Possible time components are
only allowed if they are zeros.

A special value ``NOW`` and ``TODAY`` (case-insensitive) can be used to get
the current local ``date``. This is new in Robot Framework 7.3.

Examples: ``2022-02-09``, ``2022-02-09 00:00``, ``today``
""",
    timedelta: """\
Strings are expected to represent a time interval in one of
the time formats Robot Framework supports:
- a number representing seconds like ``42`` or ``10.5``
- a time string like ``1 hour 2 seconds`` or ``1h 2s``
- a "timer" string like ``01:02`` (1 minute 2 seconds) or ``01:00:03`` (1 hour 3 seconds)

Integers and floats are considered to be seconds.

See the [https://robotframework.org/robotframework/|Robot Framework User Guide]
for more details about the supported time formats.
""",
    Path: """\
Strings are converted [https://docs.python.org/library/pathlib.html|Path] objects.
On Windows ``/`` is converted to ``\\`` automatically.

Examples: ``/tmp/absolute/path``, ``relative/path/to/file.ext``, ``name.txt``
""",
    NoneType: """\
String ``NONE`` (case-insensitive) and the empty string are converted to
the Python ``None`` object. Other values cause an error.

Converting the empty string is new in Robot Framework 7.4.
""",
    Sequence: """\
Strings must be Python [https://docs.python.org/library/stdtypes.html#list|list]
or [https://docs.python.org/library/stdtypes.html#tuple|tuple] literals.
They are converted to actual lists or tuples using the
[https://docs.python.org/library/ast.html#ast.literal_eval|ast.literal_eval]
function. They can contain any values ``ast.literal_eval`` supports, including
lists and other collections.

Any sequence is accepted without conversion. An exception is that if the used
type is ``MutableSequence``, immutable values are converted to lists.

If the type has nested types like ``Sequence[int]``, items are converted
to those types automatically.

Examples: ``['one', 'two']``, ``(1, 2, 3)``

Support to convert nested types is new in Robot Framework 6.0.
Support for tuple literals is new in Robot Framework 7.4.
""",
    list: """\
Strings must be Python [https://docs.python.org/library/stdtypes.html#list|list]
or [https://docs.python.org/library/stdtypes.html#tuple|tuple] literals.
They are converted using the
[https://docs.python.org/library/ast.html#ast.literal_eval|ast.literal_eval]
function and possible tuples converted further to lists. They can contain any
values ``ast.literal_eval`` supports, including lists and other collections.

If the argument is a list, it is used without conversion.
Tuples and other sequences are converted to lists.

If the type has nested types like ``list[int]``, items are converted
to those types automatically.

Examples: ``['one', 'two']``, ``[('one', 1), ('two', 2)]``

Support to convert nested types is new in Robot Framework 6.0.
Support for tuple literals is new in Robot Framework 7.4.
""",
    tuple: """\
Strings must be Python [https://docs.python.org/library/stdtypes.html#tuple|tuple]
or [https://docs.python.org/library/stdtypes.html#list|list] literals.
They are converted using the
[https://docs.python.org/library/ast.html#ast.literal_eval|ast.literal_eval]
function and possible lists converted further to tuples. They can contain any
values ``ast.literal_eval`` supports, including tuples and other collections.

If the argument is a tuple, it is used without conversion.
Lists and other sequences are converted to tuples.

If the type has nested types like ``tuple[str, int, int]``, items are converted
to those types automatically.

Examples: ``('one', 'two')``, ``(('one', 1), ('two', 2))``

Support to convert nested types is new in Robot Framework 6.0.
Support for list literals is new in Robot Framework 7.4.
""",
    Mapping: """\
Strings must be Python [https://docs.python.org/library/stdtypes.html#dict|dictionary]
literals. They are converted to actual dictionaries using the
[https://docs.python.org/library/ast.html#ast.literal_eval|ast.literal_eval]
function. They can contain any values ``ast.literal_eval`` supports, including
dictionaries and other collections.

Any mapping is accepted without conversion. An exception is that if the type
is ``MutableMapping``, immutable values are converted to ``dict``.

If the type has nested types like ``Mapping[str, int]``, items are converted
to those types automatically. This in new in Robot Framework 6.0.

Examples: ``{'a': 1, 'b': 2}``, ``{'key': 1, 'nested': {'key': 2}}``
""",
    dict: """\
Strings must be Python [https://docs.python.org/library/stdtypes.html#dict|dictionary]
literals. They are converted to actual dictionaries using the
[https://docs.python.org/library/ast.html#ast.literal_eval|ast.literal_eval]
function. They can contain any values ``ast.literal_eval`` supports, including
dictionaries and other collections.

Any mapping is accepted and converted to a ``dict``.

If the type has nested types like ``dict[str, int]``, items are converted
to those types automatically. This in new in Robot Framework 6.0.

Examples: ``{'a': 1, 'b': 2}``, ``{'key': 1, 'nested': {'key': 2}}``
""",
    set: """\
Strings must be Python [https://docs.python.org/library/stdtypes.html#set|set],
[https://docs.python.org/library/stdtypes.html#list|list]
or [https://docs.python.org/library/stdtypes.html#tuple|tuple]
literals. They are converted using the
[https://docs.python.org/library/ast.html#ast.literal_eval|ast.literal_eval]
function and possible lists and tuples converted further to sets. They can
contain any values ``ast.literal_eval`` supports.

If the argument is a set, it is used without conversion.
Lists and other collection objects are converted to sets.

If the type has nested types like ``set[int]``, items are converted
to those types automatically.

Examples: ``{1, 2, 3, 42}``, ``set()`` (an empty set)

Support to convert nested types is new in Robot Framework 6.0.
Support for list and tuple literals is new in Robot Framework 7.4.
""",
    frozenset: """\
Strings must be Python [https://docs.python.org/library/stdtypes.html#set|set],
[https://docs.python.org/library/stdtypes.html#list|list]
or [https://docs.python.org/library/stdtypes.html#tuple|tuple]
literals. They are converted using the
[https://docs.python.org/library/ast.html#ast.literal_eval|ast.literal_eval]
function and then converted further to ``frozenset``. They can
contain any values ``ast.literal_eval`` supports.

If the argument is a frozenset, it is used without conversion.
Lists and other collection objects are converted to frozensets.

If the type has nested types like ``frozenset[int]``, items are converted
to those types automatically.

Examples: ``{1, 2, 3, 42}``, ``frozenset()`` (an empty set)

Support to convert nested types is new in Robot Framework 6.0.
Support for list and tuple literals is new in Robot Framework 7.4.
""",
    Literal: """\
Only specified values are accepted. Values can be strings,
integers, bytes, Booleans, enums and None, and used arguments
are converted using the value type specific conversion logic.

Strings are case, space, underscore and hyphen insensitive,
but exact matches have precedence over normalized matches.
""",
    Secret: """\
Encapsulates secret values to avoid them being shown in Robot Framework logs.

The value is required to be
[https://robot-framework.readthedocs.io/en/master/autodoc/robot.utils.html#robot.utils.secret.Secret|robot.api.types.Secret]
object. These objects encapsulate confidential values so that they are not
exposed in log files. How to create them is explained in the
[https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#secret-variables|User Guide].

New in Robot Framework 7.4.
""",
}

STANDARD_TYPE_DOCS[bytearray] = STANDARD_TYPE_DOCS[bytes]
