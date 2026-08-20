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

"""A library for handling date and time values.

`DateTime` is a Robot Framework standard library that supports creating and
converting date and time values (e.g. [Get Current Date], [Convert Time]),
as well as doing simple calculations with them (e.g. [Subtract Time From Date],
[Add Time To Time]). It supports dates and times in various formats, and can
also be used by other libraries programmatically.

### Table of contents

%TOC%

# Terminology

In the context of this library, `date` and `time` generally have the following
meanings:

- `date`: An entity with both date and time components but without any
  time zone information. For example, `2014-06-11 10:07:42`.
- `time`: A time interval. For example, `1 hour 20 minutes` or `01:20:00`.

This terminology differs from what Python's standard [datetime module] uses.
Basically its [datetime] and [timedelta] objects match `date` and `time` as
defined by this library.

# Date formats

Dates can be given to and received from keywords in different formats:

- [Timestamp]
- [Custom timestamp]
- [TODAY and NOW]
- [datetime object]
- [date object]
- [Epoch time]

Input format is in most cases determined automatically. An exception is that
when using a [custom timestamp], the format must be specified using the
`date_format` argument. The default result format is [timestamp], but it can
be overridden using the `result_format` argument like `result_format=datetime`.

## Timestamp

If a date is given as a string, it is always considered to be a timestamp.
If a custom format is not given using the `date_format` argument, the timestamp
is expected to be in [ISO 8601] like format `YYYY-MM-DD hh:mm:ss.mmmmmm`,
where any non-digit character can be used as a separator or separators can be
omitted altogether. Additionally, only the date part is mandatory, all missing
time components are considered to be zeros.

Dates can also be returned in the `YYYY-MM-DD hh:mm:ss.mmm` format by using
the `timestamp` value with the `result_format` argument. This is also the default
format that keywords returning dates use. Milliseconds can be excluded
using `exclude_millis` as explained in the [Millisecond handling] section.

Examples:

```robotframework
*** Test Cases ***
Timestamps
    ${date1} =    Convert Date    2014-06-11 10:07:42.000
    ${date2} =    Convert Date    20140611 100742    result_format=timestamp
    Should Be Equal    ${date1}    ${date2}
    ${date} =     Convert Date    20140612 12:57    exclude_millis=True
    Should Be Equal    ${date}    2014-06-12 12:57:00
```

## Custom timestamp

It is possible to use custom timestamps in both input and output. This format
uses the same [format codes] as the [datetime module]. For example, the default
timestamp discussed in the previous section would match `%Y-%m-%d %H:%M:%S.%f`.

When using a custom timestamp in input, it must be specified using the
`date_format` argument. The actual input value must be a string that matches
the specified format exactly. When using a custom timestamp in output, it must
be given using `result_format` argument.

Examples:

```robotframework
*** Test Cases ***
Custom timestamps
    ${date} =    Convert Date    28.05.2014 12:05    date_format=%d.%m.%Y %H:%M
    Should Be Equal    ${date}    2014-05-28 12:05:00.000
    ${date} =    Convert Date    ${date}    result_format=%d.%m.%Y
    Should Be Equal    ${date}    28.05.2014
```

## `TODAY` and `NOW`

Strings `TODAY` and `NOW` (case-insensitive) can be used to get the current
date automatically without using the [Get Current Date] keyword.

```robotframework
*** Variables ***
${ROBOCON 2027}    2027-03-08

*** Test Cases ***
Days to RoboCon 2027
    ${delta} =    Subtract Date From Date    ${ROBOCON 2027}    TODAY    result_format=timedelta
    Log    It is ${delta.days} days to RoboCon 2027!
```

Support for `TODAY` and `NOW` is new in Robot Framework 7.5.

## `datetime` object

Python's standard [datetime] objects can be used both in input and output.
In input, they are recognized automatically, and in output it is possible
to get them by using the `datetime` value with the `result_format` argument.

One nice benefit with datetime objects is that they have different time
components available as attributes that can be easily accessed using the
extended variable syntax.

Examples:

```robotframework
*** Test Cases ***
Datetine
    ${datetime} =    Convert Date    2014-06-11 10:07:42.123    datetime
    Should Be Equal    ${datetime.year}           2014      type=int
    Should Be Equal    ${datetime.month}          6         type=int
    Should Be Equal    ${datetime.day}            11        type=int
    Should Be Equal    ${datetime.hour}           10        type=int
    Should Be Equal    ${datetime.minute}         7         type=int
    Should Be Equal    ${datetime.second}         42        type=int
    Should Be Equal    ${datetime.microsecond}    123000    type=int
```

## `date` object

Python's standard [date] objects are automatically recognized in input
the same way as [datetime] objects are. In output, it is possible to get
[date] objects by using `result_format=date`. Possible non-zero time
components are simply discarded.

Support for [date] objects in input and output is new Robot Framework 7.0
and Robot Framework 7.5, respectively.

## Epoch time

Epoch time is the time in seconds since the [UNIX epoch] i.e. 00:00:00.000 (UTC)
January 1, 1970. To give a date as an epoch time, it must be given as a number
(integer or float), not as a string. To return a date as an epoch time,
it is possible to use the `epoch` value with the `result_format` argument.
Epoch times are returned as floating point numbers.

Notice that epoch times are independent on time zones and thus same
around the world at a certain time. For example, epoch times returned
by [Get Current Date] are not affected by the `time_zone` argument.
What local time a certain epoch time matches then depends on the time zone.

Following examples demonstrate using epoch times. They are tested in Finland,
and due to the reasons explained above they would fail on other time zones.

```robotframework
*** Test Cases ***
Epoch
    ${date} =    Convert Date    ${1000000000}
    Should Be Equal    ${date}    2001-09-09 04:46:40.000
    ${date} =    Convert Date    2014-06-12 13:27:59.279    epoch
    Should Be Equal    ${date}    ${1402568879.279}
```

## Earliest supported date

The earliest date that is supported depends on the date format and to some
extent on the platform:

- Timestamps support year 1900 and above.
- Python datetime objects support year 1 and above.
- Epoch time supports 1970 and above on Windows.
- On other platforms epoch time supports 1900 and above or even earlier.

# Time formats

Similarly as dates, times can be given to and received from keywords in
various different formats. Supported formats are [Number], [Time string]
(verbose and compact), [Timer string] and [Python timedelta].

Input format for time is always determined automatically based on the input.
Result format is number by default, but it can be customized using
the `result_format` argument.

## Number

Time given as a number is interpreted to be seconds. It can be given
either as an integer or a float, or it can be a string that can be converted
to a number.

To return a time as a number, `result_format` argument must have value
`number`, which is also the default. Returned number is always a float.

Examples:

```robotframework
*** Test Cases ***
Number
    ${time} =    Convert Time    3.14
    Should Be Equal    ${time}    3.14    type=float
    ${time} =    Convert Time    ${time}    result_format=number
    Should Be Equal    ${time}    3.14    type=float
```

## Time string

Time strings are strings in format like `1 minute 42 seconds` or `1min 42s`.
The basic idea of this format is having first a number and then a text
specifying what time that number represents. Numbers can be either
integers or floating point numbers, the whole format is case and space
insensitive, and it is possible to add a minus prefix to specify negative
times. The available time specifiers are:

- `weeks`, `week`, `w` (new in RF 7.1)
- `days`, `day`, `d`
- `hours`, `hour`, `h`
- `minutes`, `minute`, `mins`, `min`, `m`
- `seconds`, `second`, `secs`, `sec`, `s`
- `milliseconds`, `millisecond`, `millis`, `ms`
- `microseconds`, `microsecond`, `us`, `μs` (new in RF 6.0)
- `nanoseconds`, `nanosecond`, `ns` (new in RF 6.0)

Starting from Robot Framework 7.6, [Add Time To Date] and
[Subtract Time From Date] also accept integer calendar units `years`, `year`,
`yrs`, `yr`, `months` and `month`. These units can be combined with the fixed
units above, such as `1 year 2 months 3 days`. Because their exact duration
depends on the starting date, they are not supported by other keywords. If the
original day does not exist in the target month, it is limited to the last day
of that month.

When returning a time string, it is possible to select between `verbose`
and `compact` representations using `result_format` argument. The verbose
format uses long specifiers like `week` and `day`, and adds `s` at the end
when needed. The compact format uses shorter specifiers like `w` and `d`, and
even drops the space between the number and the specifier.

Examples:

```robotframework
*** Test Cases ***
Time string
    ${time} =    Convert Time    1 minute 42 seconds
    Should Be Equal    ${time}    ${102}
    ${time} =    Convert Time    4200    verbose
    Should Be Equal    ${time}    1 hour 10 minutes
    ${time} =    Convert Time    - 1.5 hours    compact
    Should Be Equal    ${time}    - 1h 30min
```

## Timer string

Timer string is a string given in timer like format `hh:mm:ss.mil`. In this
format both hour and millisecond parts are optional, leading and trailing
zeros can be left out when they are not meaningful, and negative times can
be represented by adding a minus prefix.

To return a time as timer string, the `result_format` argument must be given
the value `timer`. Timer strings are by default returned in full `hh:mm:ss.mil`
format, but milliseconds can be excluded using `exclude_millis` as explained
in the [Millisecond handling] section.

Examples:

```robotframework
*** Test Cases ***
Timer string
    ${time} =    Convert Time    01:42
    Should Be Equal    ${time}    102    type=float
    ${time} =    Convert Time    01:10:00.123
    Should Be Equal    ${time}    4200.123    type=float
    ${time} =    Convert Time    102    timer
    Should Be Equal    ${time}    00:01:42.000
    ${time} =    Convert Time    -101.567    timer    exclude_millis=True
    Should Be Equal    ${time}    -00:01:42
```

## Python timedelta

Python's standard [timedelta] objects are also supported both in input and
in output. In input, they are recognized automatically, and in output it is
possible to receive them by giving the `timedelta` value to the `result_format`
argument.

Examples:

```robotframework
*** Test Cases ***
Timedelta
    ${timedelta} =    Convert Time    01:10:02.123    timedelta
    Should Be Equal    ${timedelta.total_seconds()}    ${4202.123}
```

# Millisecond handling

This library handles dates and times internally using the precision of the
given input. With [Timestamp], [Time string], and [Timer string] result
formats seconds are, however, rounded to millisecond accuracy. Milliseconds
may also be included even if there would be none.

All keywords returning dates or times have an option to leave milliseconds out
by giving a true value to `exclude_millis` argument. When milliseconds are
excluded, seconds in returned dates and times are rounded to the nearest full
second. With [Timestamp] and [Timer string] result formats, milliseconds will
also be removed from the returned string altogether.

Examples:

```robotframework
*** Test Cases ***
Milliseconds
    ${date} =    Convert Date    2014-06-11 10:07:42
    Should Be Equal    ${date}    2014-06-11 10:07:42.000
    ${date} =    Convert Date    2014-06-11 10:07:42.500    exclude_millis=True
    Should Be Equal    ${date}    2014-06-11 10:07:43
    ${dt} =      Convert Date    2014-06-11 10:07:42.500    datetime    exclude_millis=True
    Should Be Equal    ${dt.second}    ${43}
    Should Be Equal    ${dt.microsecond}    ${0}
    ${time} =    Convert Time    102    timer    exclude_millis=False
    Should Be Equal    ${time}    00:01:42.000
    ${time} =    Convert Time    102.567    timer    exclude_millis=True
    Should Be Equal    ${time}    00:01:43
```

# Programmatic usage

In addition to be used as normal library, this library is intended to
provide a stable API for other libraries to use if they want to support
same date and time formats as this library. All the provided keywords
are available as functions that can be easily imported:

```python
from robot.libraries.DateTime import convert_time


def example_keyword(timeout):
    seconds = convert_time(timeout)
    ...
```

Additionally, helper classes `Date` and `Time` can be used directly:

```python
from robot.libraries.DateTime import Date, Time


def example_keyword(day, interval):
    date = Date(day).convert('datetime')
    interval = Time(interval).convert('number')
    ...
```

In common cases it is more convenient to just use [datetime], [date] and
[timedelta] as type hints and let Robot Framework handle argument conversion
automatically:

```python
from datetime import datetime, timedelta


def example_keyword(day: datetime, interval: timedelta):
    ...
```

[ISO 8601]: http://en.wikipedia.org/wiki/ISO_8601
[UNIX epoch]: http://en.wikipedia.org/wiki/Unix_time
[datetime module]: http://docs.python.org/library/datetime.html
[datetime]: http://docs.python.org/library/datetime.html#datetime-objects
[date]: https://docs.python.org/3/library/datetime.html#date-objects
[timedelta]: http://docs.python.org/library/datetime.html#timedelta-objects
[format codes]: https://docs.python.org/3/library/datetime.html#format-codes
"""

import datetime
import sys
import time
from typing import Literal, overload, Union

from robot.utils import (
    elapsed_time_to_string, secs_to_timestr, timestr_to_secs, type_name
)
from robot.version import get_version

__version__ = get_version()
__all__ = [
    "add_time_to_date",
    "add_time_to_time",
    "convert_date",
    "convert_time",
    "get_current_date",
    "subtract_date_from_date",
    "subtract_time_from_date",
    "subtract_time_from_time",
]
ROBOT_LIBRARY_DOC_FORMAT = "Markdown"

DateInput = Union[datetime.datetime, datetime.date, float, int, str]
DateOutput = Union[datetime.datetime, datetime.date, float, str]
DateFormat = Union[Literal["timestamp", "datetime", "epoch"], str]
TimeInput = Union[datetime.timedelta, float, int, str]
TimeOutput = Union[datetime.timedelta, float, str]
TimeFormat = Literal["number", "verbose", "compact", "timer", "timedelta"]


def get_current_date(
    time_zone: Literal["local", "UTC"] = "local",
    increment: TimeInput = 0,
    result_format: DateFormat = "timestamp",
    exclude_millis: bool = False,
) -> DateOutput:
    """Returns current local or UTC time with an optional increment.

    Args:
        time_zone: Get the current time on this time zone. Currently only
            `local` (default) and `UTC` are supported. This argument has
            no effect if date is returned as an [Epoch time].
        increment: Optional time increment to add to the returned date in
            one of the supported [time formats]. Can be negative.
        result_format: Format of the returned date (see [Date formats]).
        exclude_millis: When set to any true value, rounds and drops
            milliseconds as explained in the [Millisecond handling] section.

    Returns:
        The current date in the requested format.

    Examples:

    ```robotframework
    *** Test Cases ***
    Get current date
        ${date} =    Get Current Date
        Should Be Equal    ${date}    2014-06-12 20:00:58.946
        ${date} =    Get Current Date    UTC
        Should Be Equal    ${date}    2014-06-12 17:00:58.946
        ${date} =    Get Current Date    increment=02:30:00
        Should Be Equal    ${date}    2014-06-12 22:30:58.946
        ${date} =    Get Current Date    UTC    - 5 hours
        Should Be Equal    ${date}    2014-06-12 12:00:58.946
        ${date} =    Get Current Date    result_format=datetime
        Should Be Equal    ${date.year}    ${2014}
        Should Be Equal    ${date.month}    ${6}
    ```
    """
    if time_zone.upper() == "LOCAL" or result_format.upper() == "EPOCH":
        dt = datetime.datetime.now()
    elif time_zone.upper() == "UTC":
        if sys.version_info >= (3, 12):
            # `utcnow()` was deprecated in Python 3.12. We only support "naive"
            # datetime objects and thus need to remove timezone information here.
            dt = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        else:
            dt = datetime.datetime.utcnow()
    else:
        raise ValueError(f"Unsupported timezone '{time_zone}'.")
    date = Date(dt) + Time(increment)
    return date.convert(result_format, millis=not exclude_millis)


def convert_date(
    date: DateInput,
    result_format: DateFormat = "timestamp",
    exclude_millis: bool = False,
    date_format: "str | None" = None,
) -> DateOutput:
    """Converts between supported [date formats].

    Args:
        date: Date in one of the supported [date formats].
        result_format: Format of the returned date.
        exclude_millis: When set to any true value, rounds and drops
            milliseconds as explained in the [Millisecond handling] section.
        date_format: Specifies possible [custom timestamp] format.

    Returns:
        The converted date in the requested format.

    Examples:

    ```robotframework
    *** Test Cases ***
    Convert date
        ${date} =   Convert Date    20140528 12:05:03.111
        Should Be Equal    ${date}    2014-05-28 12:05:03.111
        ${date} =   Convert Date    ${date}    epoch
        Should Be Equal    ${date}    ${1401267903.111}
        ${date} =   Convert Date    5.28.2014 12:05    exclude_millis=yes    date_format=%m.%d.%Y %H:%M
        Should Be Equal    ${date}    2014-05-28 12:05:00
    ```
    """
    return Date(date, date_format).convert(result_format, millis=not exclude_millis)


def convert_time(
    time: TimeInput,
    result_format: TimeFormat = "number",
    exclude_millis: bool = False,
) -> TimeOutput:
    """Converts between supported [time formats].

    Args:
        time: Time in one of the supported [time formats].
        result_format: Format of the returned time.
        exclude_millis: When set to any true value, rounds and drops
            milliseconds as explained in the [Millisecond handling] section.

    Returns:
        The converted time in the requested format.

    Examples:

    ```robotframework
    *** Test Cases ***
    Convert time
        ${time} =    Convert Time    10 seconds
        Should Be Equal    ${time}    ${10}
        ${time} =    Convert Time    1:00:01    verbose
        Should Be Equal    ${time}    1 hour 1 second
        ${time} =    Convert Time    ${3661.5}    timer    exclude_milles=yes
        Should Be Equal    ${time}    01:01:02
    ```
    """
    return Time(time).convert(result_format, millis=not exclude_millis)


def subtract_date_from_date(
    date1: DateInput,
    date2: DateInput,
    result_format: TimeFormat = "number",
    exclude_millis: bool = False,
    date1_format: "str | None" = None,
    date2_format: "str | None" = None,
) -> TimeOutput:
    """Subtracts date from another date and returns time between.

    Args:
        date1: Date to subtract another date from in one of the
            supported [date formats].
        date2: Date that is subtracted in one of the supported
            [date formats].
        result_format: Format of the returned time (see [Time formats]).
        exclude_millis: When set to a true value, rounds and drops
            milliseconds as explained in the [Millisecond handling] section.
        date1_format: Possible [custom timestamp] format of `date1`.
        date2_format: Possible [custom timestamp] format of `date2`.

    Returns:
        The time between the given dates in the requested format.

    Examples:

    ```robotframework
    *** Test Cases ***
    Subtract date from date
        ${time} =    Subtract Date From Date    2014-05-28 12:05:52    2014-05-28 12:05:10
        Should Be Equal    ${time}    ${42}
        ${time} =    Subtract Date From Date    2014-05-28 12:05:52    2014-05-27 12:05:10    verbose
        Should Be Equal    ${time}    1 day 42 seconds
    ```
    """
    time = Date(date1, date1_format) - Date(date2, date2_format)
    return time.convert(result_format, millis=not exclude_millis)


def add_time_to_date(
    date: DateInput,
    time: TimeInput,
    result_format: DateFormat = "timestamp",
    exclude_millis: bool = False,
    date_format: "str | None" = None,
) -> DateOutput:
    """Adds time to date and returns the resulting date.

    Args:
        date: Date to add time to in one of the supported [date formats].
        time: Time that is added in one of the supported [time formats].
            Starting from Robot Framework 7.6, this can also contain integer
            calendar years and months.
        result_format: Format of the returned date.
        exclude_millis: When set to a true value, rounds and drops
            milliseconds as explained in the [Millisecond handling] section.
        date_format: Possible [custom timestamp] format of `date`.

    Returns:
        The resulting date in the requested format.

    Examples:

    ```robotframework
    *** Test Cases ***
    Add time to date
        ${date} =    Add Time To Date    2014-05-28 12:05:03.111    7 days
        Should Be Equal    ${date}    2014-06-04 12:05:03.111
        ${date} =    Add Time To Date    2024-01-31    1 month 1 day
        Should Be Equal    ${date}    2024-03-01 00:00:00.000
        ${date} =    Add Time To Date    2014-05-28 12:05:03.111    01:02:03:004
        Should Be Equal    ${date}    2014-05-28 13:07:06.115
    ```
    """
    date = Date(date, date_format)
    seconds = timestr_to_secs(time, round_to=None, start_date=date.datetime)
    date += Time(seconds)
    return date.convert(result_format, millis=not exclude_millis)


def subtract_time_from_date(
    date: DateInput,
    time: TimeInput,
    result_format: DateFormat = "timestamp",
    exclude_millis: bool = False,
    date_format: "str | None" = None,
) -> DateOutput:
    """Subtracts time from date and returns the resulting date.

    Args:
        date: Date to subtract time from in one of the supported [date formats].
        time: Time that is subtracted in one of the supported [time formats].
            Starting from Robot Framework 7.6, this can also contain integer
            calendar years and months.
        result_format: Format of the returned date.
        exclude_millis: When set to any true value, rounds and drops
            milliseconds as explained in the [Millisecond handling] section.
        date_format: Possible [custom timestamp] format of `date`.

    Returns:
        The resulting date in the requested format.

    Examples:

    ```robotframework
    *** Test Cases ***
    Subtract time from date
        ${date} =    Subtract Time From Date    2014-06-04 12:05:03.111    7 days
        Should Be Equal    ${date}    2014-05-28 12:05:03.111
        ${date} =    Subtract Time From Date    2025-03-31    1 month
        Should Be Equal    ${date}    2025-02-28 00:00:00.000
        ${date} =    Subtract Time From Date    2014-05-28 13:07:06.115    01:02:03:004
        Should Be Equal    ${date}    2014-05-28 12:05:03.111
    ```
    """
    date = Date(date, date_format)
    if isinstance(time, str):
        original = time
        time = _negate_time_string(time)
        try:
            seconds = timestr_to_secs(time, round_to=None, start_date=date.datetime)
        except ValueError:
            raise ValueError(f"Invalid time string '{original}'.")
        date += Time(seconds)
    else:
        date -= Time(time)
    return date.convert(result_format, millis=not exclude_millis)


def _negate_time_string(time: str) -> str:
    time = time.strip()
    if time.startswith("-"):
        return time[1:].lstrip()
    if time.startswith("+"):
        return "-" + time[1:].lstrip()
    return "-" + time


def add_time_to_time(
    time1: TimeInput,
    time2: TimeInput,
    result_format: TimeFormat = "number",
    exclude_millis: bool = False,
) -> TimeOutput:
    """Adds time to another time and returns the resulting time.

    Args:
        time1: First time in one of the supported [time formats].
        time2: Second time in one of the supported [time formats].
        result_format: Format of the returned time.
        exclude_millis: When set to any true value, rounds and drops
            milliseconds as explained in the [Millisecond handling] section.

    Returns:
        The sum of the given times in the requested format.

    Examples:

    ```robotframework
    *** Test Cases ***
    Add time to time
        ${time} =    Add Time To Time    1 minute    42
        Should Be Equal    ${time}    ${102}
        ${time} =    Add Time To Time    3h 5min    01:02:03    timer    exclude_millis=True
        Should Be Equal    ${time}    04:07:03
    ```
    """
    time = Time(time1) + Time(time2)
    return time.convert(result_format, millis=not exclude_millis)


def subtract_time_from_time(
    time1: TimeInput,
    time2: TimeInput,
    result_format: TimeFormat = "number",
    exclude_millis: bool = False,
) -> TimeOutput:
    """Subtracts time from another time and returns the resulting time.

    Args:
        time1: Time to subtract another time from in one of
            the supported [time formats].
        time2: Time to subtract in one of the supported [time formats].
        result_format: Format of the returned time.
        exclude_millis: When set to any true value, rounds and drops
            milliseconds as explained in the [Millisecond handling] section.

    Returns:
        The difference between the given times in the requested format.

    Examples:

    ```robotframework
    *** Test Cases ***
    Subtract time from time
        ${time} =    Subtract Time From Time    00:02:30    100
        Should Be Equal    ${time}    ${50}
        ${time} =    Subtract Time From Time    ${time}    1 minute    compact
        Should Be Equal    ${time}    - 10s
    ```
    """
    time = Time(time1) - Time(time2)
    return time.convert(result_format, millis=not exclude_millis)


class Date:

    def __init__(self, date: DateInput, input_format: "str | None" = None):
        self.datetime = self._convert_to_datetime(date, input_format)

    @property
    def seconds(self) -> float:
        # Mainly for backwards compatibility with RF 2.9.1 and earlier.
        return self._convert_to_epoch(self.datetime)

    def _convert_to_datetime(
        self,
        date: DateInput,
        input_format: "str | None",
    ) -> datetime.datetime:
        if isinstance(date, datetime.datetime):
            return date
        if isinstance(date, datetime.date):
            return datetime.datetime(date.year, date.month, date.day)
        if isinstance(date, (int, float)):
            return self._epoch_seconds_to_datetime(date)
        if isinstance(date, str):
            return self._string_to_datetime(date, input_format)
        raise ValueError(f"Unsupported input '{date}'.")

    def _epoch_seconds_to_datetime(self, secs: float) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(secs)

    def _string_to_datetime(
        self,
        timestamp: str,
        input_format: "str | None",
    ) -> datetime.datetime:
        if timestamp.upper() in ("TODAY", "NOW"):
            return datetime.datetime.now()
        if not input_format:
            timestamp = self._normalize_timestamp(timestamp)
            input_format = "%Y-%m-%d %H:%M:%S.%f"
        return datetime.datetime.strptime(timestamp, input_format)

    def _normalize_timestamp(self, timestamp: str) -> str:
        numbers = "".join(d for d in timestamp if d.isdigit())
        if not (8 <= len(numbers) <= 20):
            raise ValueError(f"Invalid timestamp '{timestamp}'.")
        d = numbers[:8]
        t = numbers[8:].ljust(12, "0")
        return f"{d[:4]}-{d[4:6]}-{d[6:8]} {t[:2]}:{t[2:4]}:{t[4:6]}.{t[6:]}"

    def convert(self, format: str, millis: bool = True) -> DateOutput:
        dt = self.datetime
        if not millis:
            secs = 1 if dt.microsecond >= 5e5 else 0
            dt = dt.replace(microsecond=0) + datetime.timedelta(seconds=secs)
        if "%" in format:
            return self._convert_to_custom_timestamp(dt, format)
        format = format.lower()
        if format == "timestamp":
            return self._convert_to_timestamp(dt, millis)
        if format == "datetime":
            return dt
        if format == "date":
            return dt.date()
        if format == "epoch":
            return self._convert_to_epoch(dt)
        raise ValueError(f"Unknown format '{format}'.")

    def _convert_to_custom_timestamp(self, dt: datetime.datetime, format: str) -> str:
        return dt.strftime(format)

    def _convert_to_timestamp(self, dt: datetime.datetime, millis: bool = True) -> str:
        if not millis:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        ms = round(dt.microsecond / 1000)
        if ms == 1000:
            dt += datetime.timedelta(seconds=1)
            ms = 0
        return dt.strftime("%Y-%m-%d %H:%M:%S") + f".{ms:03d}"

    def _convert_to_epoch(self, dt: datetime.datetime) -> float:
        try:
            return dt.timestamp()
        except OSError:
            # https://github.com/python/cpython/issues/81708
            return time.mktime(dt.timetuple()) + dt.microsecond / 1e6

    def __add__(self, other: "Time") -> "Date":
        if isinstance(other, Time):
            return Date(self.datetime + other.timedelta)
        raise TypeError(f"Can only add Time to Date, got {type_name(other)}.")

    @overload
    def __sub__(self, other: "Date") -> "Time": ...

    @overload
    def __sub__(self, other: "Time") -> "Date": ...

    def __sub__(self, other: "Date | Time") -> "Date | Time":
        if isinstance(other, Date):
            return Time(self.datetime - other.datetime)
        if isinstance(other, Time):
            return Date(self.datetime - other.timedelta)
        raise TypeError(
            f"Can only subtract Date or Time from Date, got {type_name(other)}."
        )


class Time:

    def __init__(self, time: TimeInput):
        self.seconds = timestr_to_secs(time, round_to=None)

    @property
    def timedelta(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=self.seconds)

    def convert(self, format: str, millis: bool = True) -> TimeOutput:
        try:
            result_converter = getattr(self, f"_convert_to_{format.lower()}")
        except AttributeError:
            raise ValueError(f"Unknown format '{format}'.")
        seconds = self.seconds if millis else float(round(self.seconds))
        return result_converter(seconds, millis)

    def _convert_to_number(self, seconds: float, _) -> float:
        return seconds

    def _convert_to_verbose(self, seconds: float, _) -> str:
        return secs_to_timestr(seconds)

    def _convert_to_compact(self, seconds: float, _) -> str:
        return secs_to_timestr(seconds, compact=True)

    def _convert_to_timer(self, seconds: float, millis: bool = True) -> str:
        return elapsed_time_to_string(seconds, include_millis=millis, seconds=True)

    def _convert_to_timedelta(self, seconds: float, _) -> datetime.timedelta:
        return datetime.timedelta(seconds=seconds)

    def __add__(self, other: "Time") -> "Time":
        if isinstance(other, Time):
            return Time(self.seconds + other.seconds)
        raise TypeError(f"Can only add Time to Time, got {type_name(other)}.")

    def __sub__(self, other: "Time") -> "Time":
        if isinstance(other, Time):
            return Time(self.seconds - other.seconds)
        raise TypeError(f"Can only subtract Time from Time, got {type_name(other)}.")
