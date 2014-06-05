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


"""A test library for manipulating and verifying date and time values.

`DateTime` is a standard library of Robot Framework that allows converting date and time values, adding and
subtracting them and verifying variables as date or time values.

This library is new in Robot Framework 2.8.5.

= Table of Contents =

- `Defining date and time`
- `Time formats`
- `Date formats`
- `Formatted timestamps`
- `Millisecond handling`
- `Keywords`

= Defining date and time =

The terms used by this library differ somewhat from those used in Python. In this library the term `time` is used
to represent a period of time measured in hours, minutes, seconds etc. (like Python's timedelta).

On the other hand, `date` represents both date and time of day (like Python's datetime).

= Time formats =

Time can be input in and converted to following formats:

| = Format name = | = Example =             |
| number          | 3903.0                  |
| verbose         | 1hour 5minutes 3seconds |
| compact         | 1h 5m 3s                |
| timer           | 01:05:03.000            |
| timedelta       | Python timedelta object |

= Date formats =

Date can be input in and converted to following formats:

| = Format name =             | = Example =             |
| timestamp                   | 28.05.2014 12:05:03.000 |
| epoch                       | 123123123123.0          |
| datetime                    | Python datetime object  |

= Formatted timestamps =

`timestamp` strings can have both input and output formatting specified in formatting directives which are
documented in Python's [https://docs.python.org/2/library/time.html#time.strftime|time.strftime() documentation].

*Note:* The %f directive for microseconds is not supported anywhere but in the end of a format string for Python
versions < 2.6 and for Jython.

Input formatting is always given as separate parameter (or parameters, if there are many date inputs) to keywords
handling dates. In output formatting however, a colon character is needed to specify that we want a timestamp with
custom formatting (e.g. 'timestamp:format').

If a format is not given to string input or output in keyword, it is assumed to be '%Y-%m-%d %H:%M:%S' by default.
However, the input is flexible and will accept any non-digit separators as long as the numbers are in the right
order.

Examples:
| ${ts} =         | Convert Date | 12:05:03 28.05.2014 | date_format=%H:%M:%S %m.%d.%Y |
| Should Be Equal | ${ts}        | 2014-05-28 12:05:03 |
| Add To Date     | ${ts}        | 1hour               | timestamp:%H.%M.%S %d-%m |
| Should Be Equal | ${ts}        | 13.05.03 28-05      |

= Millisecond handling =

Every keyword in this library has the option to leave milliseconds out of the result. By default, milliseconds are
kept with every conversion and calculation. If milliseconds are chosen to be left out the result will be rounded to
nearest second.
"""

from datetime import timedelta, datetime
import time
import string
import sys
import re

from robot.utils import elapsed_time_to_string, secs_to_timestr, timestr_to_secs


def should_be_date(date, input_format=None):
    """Validate input to be a date.

    `date` is valid when it is in one of the `Date Formats`.

    `input_format` is formatting directive (See `Formatted Timestamps` in introduction) that can be given to validate
    a timestamp string in custom format.

    Returns `True` if `date` is valid and `False` otherwise.

    Examples:
    | ${result} =        | Should Be Date | 2014-06-02 11:59:01.001 |
    | Should Be True     | ${result}      |
    | ${result} =        | Should Be Date | 11:59:01.001 02-06-2014 | %H:%M:%S %d-%m-%Y |
    | Should Be True     | ${result}      |
    | ${result} =        | Should Be Date | no date here |
    | Should Not Be True | ${result}      |
    | ${result} =        | Should Be Date | ${111} |
    | Should Be True     | ${result}      |
    | ${result} =        | Should Be Date | 111 |
    | Should Not Be True | ${result}      |

    New in Robot Framework 2.8.5.
    """
    try:
        Date(date, input_format)
    except ValueError:
        return False
    return True

def should_be_time(time):
    """Validate input to be a time value.

    `time` is valid when it is in one of the `Time Formats`.

    Returns `True` if `time` is valid and `False` otherwise.

    Examples:
    | ${result} =        | Should Be Time | 10 s     |
    | Should Be True     | ${result}      |
    | ${result} =        | Should Be Time | 1 parsec |
    | Should Not Be True | ${result}      |

    New in Robot Framework 2.8.5.
    """
    try:
        Time(time)
    except ValueError:
        return False
    return True

def convert_time(time, result_format='number', exclude_millis=False):
    """Convert time to different format.

    `time` is a time representation given in one of the supported formats.

    `result_format` is the name of the format that `time` is converted to.

    Set `exclude_millis` to True to leave milliseconds out of the result by default they are kept.

    Returns time in specified format.

    Examples:
    | ${time} =       | Convert Time  | 10 s              | number  |
    | Should Be Equal | ${time}       | ${10}             |
    | ${time} =       | Convert Time  | 1:00:01           | verbose |
    | Should Be Equal | ${time}       | 1 hour 1 seconds  |
    | ${time} =       | Convert Time  | ${3660}           | compact |
    | Should Be Equal | ${time}       | 1h 1min           |

    New in Robot Framework 2.8.5.
    """
    return Time(time).convert(result_format, millis=not exclude_millis)

def convert_date(date, result_format='timestamp', exclude_millis=False, date_format=None):
    """Convert date to different format.

    `date` is a date representation given in one of the supported formats.

    `result_format` is the name of the format that `date` is converted to.

    Set `exclude_millis` to True to leave milliseconds out of the result by default they are kept.

    `date_format` can be used to specify how the input date is formatted if it is a string. See `Date formats` in
    the introduction for syntax.

    Returns date in specified format.

    Examples:
    | ${ts} =         | Convert Date | 2014.05.28 12:05:03.111 | epoch                         |
    | Should Be Equal | ${ts}        | ${1401267903.111}       |
    | ${ts} =         | Convert Date | 12.05.03 28-05-2014     | date_format=%H.%M.%S %m-%d-%Y |
    | Should Be Equal | ${ts}        | 2014-05-28 12:05:03     |
    | ${ts} =         | Convert Date | ${datetime.now()}       | timestamp:%Y/%m/%d %H:%M      |
    | Should Be Equal | ${ts}        | 2014/05/28 12:05        |

    New in Robot Framework 2.8.5.
    """
    return Date(date, date_format).convert(result_format, millis=not exclude_millis)

def subtract_dates(date1, date2, result_format='number', exclude_millis=False, date1_format=None, date2_format=None):
    """Subtract date2 from date1.

    `date1` and `date2` are date representations given in one supported formats. They can be of different formats.

    `result_format` is the name of the time format that the result is outputted in.

    Set `exclude_millis` to True to leave milliseconds out of the result by default they are kept.

    `date1_format` and `date2_format` can be used to specify how the two input dates are formatted if they are
    strings. See `Date formats` in the introduction for syntax.

    Returns difference between date1 and date2 in time.

     Examples:
    | ${time} =       | Subtract Dates | 2014.05.28 12:05:03.111 | 2014.05.27 12:05:03.111 |
    | Should Be Equal | ${time}        | ${86400}                |
    | ${time} =       | Subtract Dates | 2014.05.28 12:05:03.111 | 2014.05.27 11:04:03.111 | verbose |
    | Should Be Equal | ${time}        | 1 day 1 hour 1 second   |
    | ${time} =       | Subtract Dates | 2014.05.28 12:05:03.000 | 2014.05.27 12:05:03.499 | compact | exclude_millis=true |
    | Should Be Equal | ${time}        | 1d                      |

    New in Robot Framework 2.8.5.
    """
    time = Date(date1, date1_format) - Date(date2, date2_format)
    return time.convert(result_format, millis=not exclude_millis)

def add_to_date(date, time, result_format='timestamp', exclude_millis=False, date_format=None):
    """Add time to a date.

    `date` is a date representation given in one of the supported formats.

    `time` is a time representation given in one of the supported formats.

    `result_format` is the name of the date format that the result is outputted in.

    Set `exclude_millis` to True to leave milliseconds out of the result by default they are kept.

    `date_format` can be used to specify how the input date is formatted if it is a string. See `Date formats` in
    the introduction for syntax.

    Returns date which is given amount of time in the future.

    Examples:
    | ${date} =       | Add To Date    | 2014.05.28 12:05:03.111 | 1h |
    | Should Be Equal | ${date}        | 2014.05.28 13:05:03.111 |
    | ${date} =       | Add To Date    | 2014.05.28 12:05:03.111 | 1 year 3 hours |
    | Should Be Equal | ${date}        | 2015.05.28 15:05:03.111 |

    New in Robot Framework 2.8.5.
    """
    date = Date(date, date_format) + Time(time)
    return date.convert(result_format, millis=not exclude_millis)

def subtract_from_date(date, time, result_format='timestamp', exclude_millis=False, date_format=None):
    """Subtract time from date.

    `date` is a date representation given in one of the supported formats.

    `time` is a time representation given in one of the supported formats.

    `result_format` is the name of the date format that the result is outputted in.

    Set `exclude_millis` to True to leave milliseconds out of the result by default they are kept.

    `date_format` can be used to specify how the input date is formatted if it is a string. See `Date formats` in
    the introduction for syntax.

    Returns date which is given time before the specified date.

    Examples:
    | ${date} =       | Subtract From Date | 2014.05.28 12:05:03.111 | 1h                |
    | Should Be Equal | ${date}            | 2014.05.28 11:05:03.111 |
    | ${date} =       | Subtract From Date | 2014.05.28 12:05:03.111 | 12h 5min 3s 111ms | timestamp:%d:%m |
    | Should Be Equal | ${date}            | 28.05                   |

    New in Robot Framework 2.8.5.
    """
    date = Date(date, date_format) - Time(time)
    return date.convert(result_format, millis=not exclude_millis)

def add_to_time(time1, time2, result_format='number', exclude_millis=False):
    """Add time2 to time1.

    `time1` and `time2` are time representations given in one of the supported formats.

    `result_format` is the name of the time format that the result is outputted in.

    Set `exclude_millis` to True to leave milliseconds out of the result by default they are kept.

    Returns the sum of two times.

    Examples:
    | ${time} =       | Add To Time | 01:00:00.000      | 3h |
    | Should Be Equal | ${time}     | ${14400}          |
    | ${time} =       | Add To Time | 3 hours 5 minutes | 00:01:00.000 | timer |
    | Should Be Equal | ${time}     | 03:06:00.000      |

    New in Robot Framework 2.8.5.
    """
    time = Time(time1) + Time(time2)
    return time.convert(result_format, millis=not exclude_millis)

def subtract_from_time(time1, time2, result_format='number', exclude_millis=False):
    """Subtract time2 from time1.

    `time1` and `time2` are time representations given in one of the supported formats.

    `result_format` is the name of the time format that the result is outputted in.

    Set `exclude_millis` to True to leave milliseconds out of the result by default they are kept.

    Returns the difference of two times.

    Examples:
    | ${time} =       | Subtract From Time | 01:00:00.000 | 5min |
    | Should Be Equal | ${time}            | ${3300}      |
    | ${time} =       | Subtract From Time | ${36}        | 1m   |
    | Should Be Equal | ${time}            | ${-14}       |

    New in Robot Framework 2.8.5.
    """
    time = Time(time1) - Time(time2)
    return time.convert(result_format, millis=not exclude_millis)

def get_current_date(time_zone='local', increment='0', result_format='timestamp', exclude_millis=False):
    """Get current date value.

    Current date can be returned in either local time or in UTC by specifying the `time_zone` as either
    'local' or 'UTC'.

    The value van also be incremented or subtracted by `increment`, which can be any of the supported time formats.

    `result_format` is the name of the time format that the result is outputted in.

    Set `exclude_millis` to True to leave milliseconds out of the result by default they are kept.

    Returns a date in specified format.

    Examples:
    | ${date} =       | Get Current Date |
    | Should Be Equal | ${date}          | 2014-05-30 14:45:01.135 |
    | ${date} =       | Get Current Date | UTC                     |
    | Should Be Equal | ${date}          | 2014-05-30 11:45:01.135 |
    | ${date} =       | Get Current Date | UTC                     | -5h |
    | Should Be Equal | ${date}          | 2014-05-30 06:45:01.135 |
    | ${date} =       | Get Current Date | result_format=epoch     |
    | Should Be Equal | ${date}          | ${1401450301.0}         |

    New in Robot Framework 2.8.5.
    """
    if time_zone.upper() == 'LOCAL':
        dt = datetime.now()
    elif time_zone.upper() == 'UTC':
        dt = datetime.utcnow()
    else:
        raise ValueError('Unsupported timezone %s' % time_zone)
    date = Date(dt) + Time(increment)
    return date.convert(result_format, millis=not exclude_millis)


class Time(object):

    def __init__(self, time):
        self.seconds = self._convert_time_to_seconds(time)

    def __add__(self, other):
        if isinstance(other, Time):
            return Time(self.seconds + other.seconds)
        raise TypeError('Can only add Time to Time, not %s' % type(other).__name__)

    def __sub__(self, other):
        if isinstance(other, Time):
            return Time(self.seconds - other.seconds)
        raise TypeError('Can only subtract Time from Time, not %s' % type(other).__name__)

    def _convert_time_to_seconds(self, time):
        if isinstance(time, timedelta):
            # timedelta.total_seconds() is new in Python 2.7
            return (time.days * 24 * 60 * 60 + time.seconds +
                    time.microseconds / 1000000.0)
        return timestr_to_secs(time)

    def convert(self, format, millis=True):
        try:
            result_converter = getattr(self, '_convert_to_%s' % format.lower())
        except AttributeError:
            raise ValueError("Unknown format '%s'." % format)
        seconds = self.seconds if millis else int(round(self.seconds))
        return result_converter(seconds, millis)

    def _convert_to_number(self, seconds, millis=True):
        return seconds

    def _convert_to_verbose(self, seconds, millis=True):
        return secs_to_timestr(seconds)

    def _convert_to_compact(self, seconds, millis=True):
        return secs_to_timestr(seconds, compact=True)

    def _convert_to_timer(self, seconds, millis=True):
        return elapsed_time_to_string(seconds * 1000, include_millis=millis)

    def _convert_to_timedelta(self, seconds, millis=True):
        return timedelta(seconds=seconds)


class Date(object):

    def __init__(self, dt, input_format=None):
        self.seconds = self._convert_to_secs(dt, input_format)

    def __add__(self, other):
        if isinstance(other, Time):
            return Date(self.seconds + other.seconds)
        raise TypeError('Can only add Time to Date, not %s' % type(other).__name__)

    def __sub__(self, other):
        if isinstance(other, Date):
            return Time(self.seconds - other.seconds)
        if isinstance(other, Time):
            return Date(self.seconds - other.seconds)
        raise TypeError('Can only subtract Date or Time from Date, not %s' % type(other).__name__)

    def _convert_to_secs(self, timestamp, input_format):
        if isinstance(timestamp, basestring):
            timestamp = self._string_to_epoch(timestamp, input_format)
        elif isinstance(timestamp, datetime):
            timestamp = self._mktime_with_millis(timestamp)
        elif not isinstance(timestamp, (int, long, float)):
            raise ValueError("Unsupported input '%s'." % timestamp)
        return round(timestamp, 3)

    def _string_to_epoch(self, dt, input_format):
        if not input_format:
            dt = self._normalize_timestamp(dt)
            input_format = '%Y-%m-%d %H:%M:%S.%f'
        if self._need_to_handle_f_directive(input_format):
            return self._handle_un_supported_f_directive(dt, input_format)
        return self._mktime_with_millis(datetime.strptime(dt, input_format))

    def _need_to_handle_f_directive(self, format):
        if '%f' in format and (sys.version_info < (2, 6) or sys.platform == 'cli'):
            return True
        return False

    def _normalize_timestamp(self, date):
        ts = ''.join(d for d in date if d in string.digits).ljust(20, '0')
        return '%s-%s-%s %s:%s:%s.%s' % (ts[:4], ts[4:6], ts[6:8], ts[8:10],
                                         ts[10:12], ts[12:14], ts[14:])

    def _handle_un_supported_f_directive(self, dt, input_format):
        input_format = self._remove_f_from_format(input_format)
        micro = re.search('\d+$', dt).group(0)
        dt = dt[:-len(micro)]
        epoch = time.mktime(time.strptime(dt, input_format))
        epoch += float(micro) / 10**len(micro)
        return epoch

    def _remove_f_from_format(self, format):
        if not format.endswith('%f'):
            raise ValueError('%f directive is supported only at the end of '
                             'the format string on this Python interpreter.')
        return format[:-2]

    def _dt_from_timestamp(self, ts):
        # Jython and IronPython handle floats incorrectly. For example,
        # datetime.fromtimestamp(1399410716.123).microsecond == 122999
        dt = datetime.fromtimestamp(ts)
        return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                        dt.second, int(round(ts % 1 * 10**6, -3)))

    def _mktime_with_millis(self, dt):
        return time.mktime(dt.timetuple()) + dt.microsecond / 10.0**6

    def convert(self, format, millis=True):
        if ':' in format:
            format, output_format = format.split(':', 1)
            return self._convert_to_timestamp(self.seconds, millis, output_format)
        try:
            result_converter = getattr(self, '_convert_to_%s' % format.lower())
        except AttributeError:
            raise ValueError("Unknown format '%s'." % format)
        dt = self.seconds if millis else round(self.seconds)
        return result_converter(dt, millis)

    def _convert_to_timestamp(self, seconds, millis=True, output_format=None):
        dt = self._dt_from_timestamp(seconds)
        if output_format:
            if self._need_to_handle_f_directive(output_format):
                output_format = self._remove_f_from_format(output_format)
            else:
                output_format = str(output_format) #Python 2.5 does not accept unicode
                millis = False
        else:
            output_format = '%Y-%m-%d %H:%M:%S'
        ts = dt.strftime(output_format)
        if millis:
            ts += '.%03d' % (round(seconds % 1 * 1000))
        return ts

    def _convert_to_epoch(self, dt, millis=True):
        return dt

    def _convert_to_datetime(self, dt, millis=True):
        return self._dt_from_timestamp(dt)
