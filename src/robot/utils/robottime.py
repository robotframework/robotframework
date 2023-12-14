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

import re
import time
import warnings
from datetime import datetime, timedelta

from .normalizing import normalize
from .misc import plural_or_not
from .robottypes import is_number, is_string


_timer_re = re.compile(r'^([+-])?(\d+:)?(\d+):(\d+)(\.\d+)?$')


def _get_timetuple(epoch_secs=None):
    if epoch_secs is None:  # can also be 0 (at least in unit tests)
        epoch_secs = time.time()
    secs, millis = _float_secs_to_secs_and_millis(epoch_secs)
    timetuple = time.localtime(secs)[:6]  # from year to secs
    return timetuple + (millis,)


def _float_secs_to_secs_and_millis(secs):
    isecs = int(secs)
    millis = round((secs - isecs) * 1000)
    return (isecs, millis) if millis < 1000 else (isecs+1, 0)


def timestr_to_secs(timestr, round_to=3):
    """Parses time strings like '1h 10s', '01:00:10' and '42' and returns seconds.

    Time can also be given as an integer or float or, starting from RF 6.0.1,
    as a `timedelta` instance.

    The result is rounded according to the `round_to` argument.
    Use `round_to=None` to disable rounding altogether.
    """
    if is_string(timestr) or is_number(timestr):
        converters = [_number_to_secs, _timer_to_secs, _time_string_to_secs]
        for converter in converters:
            secs = converter(timestr)
            if secs is not None:
                return secs if round_to is None else round(secs, round_to)
    if isinstance(timestr, timedelta):
        return timestr.total_seconds()
    raise ValueError(f"Invalid time string '{timestr}'.")


def _number_to_secs(number):
    try:
        return float(number)
    except ValueError:
        return None


def _timer_to_secs(number):
    match = _timer_re.match(number)
    if not match:
        return None
    prefix, hours, minutes, seconds, millis = match.groups()
    seconds = float(minutes) * 60 + float(seconds)
    if hours:
        seconds += float(hours[:-1]) * 60 * 60
    if millis:
        seconds += float(millis[1:]) / 10**len(millis[1:])
    if prefix == '-':
        seconds *= -1
    return seconds


def _time_string_to_secs(timestr):
    timestr = _normalize_timestr(timestr)
    if not timestr:
        return None
    nanos = micros = millis = secs = mins = hours = days = 0
    if timestr[0] == '-':
        sign = -1
        timestr = timestr[1:]
    else:
        sign = 1
    temp = []
    for c in timestr:
        try:
            if   c == 'n': nanos  = float(''.join(temp)); temp = []
            elif c == 'u': micros = float(''.join(temp)); temp = []
            elif c == 'M': millis = float(''.join(temp)); temp = []
            elif c == 's': secs   = float(''.join(temp)); temp = []
            elif c == 'm': mins   = float(''.join(temp)); temp = []
            elif c == 'h': hours  = float(''.join(temp)); temp = []
            elif c == 'd': days   = float(''.join(temp)); temp = []
            else: temp.append(c)
        except ValueError:
            return None
    if temp:
        return None
    return sign * (nanos/1E9 + micros/1E6 + millis/1000 + secs +
                   mins*60 + hours*60*60 + days*60*60*24)


def _normalize_timestr(timestr):
    timestr = normalize(timestr)
    for specifier, aliases in [('n', ['nanosecond', 'ns']),
                               ('u', ['microsecond', 'us', 'μs']),
                               ('M', ['millisecond', 'millisec', 'millis',
                                      'msec', 'ms']),
                               ('s', ['second', 'sec']),
                               ('m', ['minute', 'min']),
                               ('h', ['hour']),
                               ('d', ['day'])]:
        plural_aliases = [a+'s' for a in aliases if not a.endswith('s')]
        for alias in plural_aliases + aliases:
            if alias in timestr:
                timestr = timestr.replace(alias, specifier)
    return timestr


def secs_to_timestr(secs: 'int|float|timedelta', compact=False) -> str:
    """Converts time in seconds to a string representation.

    Returned string is in format like
    '1 day 2 hours 3 minutes 4 seconds 5 milliseconds' with following rules:

    - Time parts having zero value are not included (e.g. '3 minutes 4 seconds'
      instead of '0 days 0 hours 3 minutes 4 seconds')
    - Hour part has a maximum of 23 and minutes and seconds both have 59
      (e.g. '1 minute 40 seconds' instead of '100 seconds')

    If compact has value 'True', short suffixes are used.
    (e.g. 1d 2h 3min 4s 5ms)
    """
    if isinstance(secs, timedelta):
        secs = secs.total_seconds()
    return _SecsToTimestrHelper(secs, compact).get_value()


class _SecsToTimestrHelper:

    def __init__(self, float_secs, compact):
        self._compact = compact
        self._ret = []
        self._sign, ms, sec, min, hour, day = self._secs_to_components(float_secs)
        self._add_item(day, 'd', 'day')
        self._add_item(hour, 'h', 'hour')
        self._add_item(min, 'min', 'minute')
        self._add_item(sec, 's', 'second')
        self._add_item(ms, 'ms', 'millisecond')

    def get_value(self):
        if len(self._ret) > 0:
            return self._sign + ' '.join(self._ret)
        return '0s' if self._compact else '0 seconds'

    def _add_item(self, value, compact_suffix, long_suffix):
        if value == 0:
            return
        if self._compact:
            suffix = compact_suffix
        else:
            suffix = ' %s%s' % (long_suffix, plural_or_not(value))
        self._ret.append('%d%s' % (value, suffix))

    def _secs_to_components(self, float_secs):
        if float_secs < 0:
            sign = '- '
            float_secs = abs(float_secs)
        else:
            sign = ''
        int_secs, millis = _float_secs_to_secs_and_millis(float_secs)
        secs = int_secs % 60
        mins = int_secs // 60 % 60
        hours = int_secs // (60 * 60) % 24
        days = int_secs // (60 * 60 * 24)
        return sign, millis, secs, mins, hours, days


def format_time(timetuple_or_epochsecs, daysep='', daytimesep=' ', timesep=':',
                millissep=None):
    """Deprecated in Robot Framework 7.0. Will be removed in Robot Framework 8.0."""
    warnings.warn("'robot.utils.format_time' is deprecated and will be "
                  "removed in Robot Framework 8.0.")
    if is_number(timetuple_or_epochsecs):
        timetuple = _get_timetuple(timetuple_or_epochsecs)
    else:
        timetuple = timetuple_or_epochsecs
    daytimeparts = ['%02d' % t for t in timetuple[:6]]
    day = daysep.join(daytimeparts[:3])
    time_ = timesep.join(daytimeparts[3:6])
    millis = millissep and '%s%03d' % (millissep, timetuple[6]) or ''
    return day + daytimesep + time_ + millis


def get_time(format='timestamp', time_=None):
    """Return the given or current time in requested format.

    If time is not given, current time is used. How time is returned is
    determined based on the given 'format' string as follows. Note that all
    checks are case-insensitive.

    - If 'format' contains word 'epoch' the time is returned in seconds after
      the unix epoch.
    - If 'format' contains any of the words 'year', 'month', 'day', 'hour',
      'min' or 'sec' only selected parts are returned. The order of the returned
      parts is always the one in previous sentence and order of words in
      'format' is not significant. Parts are returned as zero padded strings
      (e.g. May -> '05').
    - Otherwise (and by default) the time is returned as a timestamp string in
      format '2006-02-24 15:08:31'
    """
    time_ = int(time.time() if time_ is None else time_)
    format = format.lower()
    # 1) Return time in seconds since epoc
    if 'epoch' in format:
        return time_
    dt = datetime.fromtimestamp(time_)
    parts = []
    for part, name in [(dt.year, 'year'), (dt.month, 'month'), (dt.day, 'day'),
                       (dt.hour, 'hour'), (dt.minute, 'min'), (dt.second, 'sec')]:
        if name in format:
            parts.append(f'{part:02}')
    # 2) Return time as timestamp
    if not parts:
        return dt.isoformat(' ', timespec='seconds')
    # Return requested parts of the time
    elif len(parts) == 1:
        return parts[0]
    else:
        return parts


def parse_timestamp(timestamp: 'str|datetime') -> datetime:
    """Parse timestamp in ISO 8601-like formats into a ``datetime``.

    Months, days, hours, minutes and seconds must use two digits and
    year must use four. Microseconds can use up to six digits. All time
    parts can be omitted.

    Separators '-', '_', ' ', 'T', ':' and '.' between date and time components.
    Separators can also be omitted altogether.

    Examples::

        2023-09-08T14:34:42.123456
        2023-09-08 14:34:42.123
        20230908 143442
        2023_09_08

    This is similar to ``datetime.fromisoformat``, but a little less strict.
    The standard function is recommended if the input format is known to be
    accepted.

    If the input is a ``datetime``, it is returned as-is.

    New in Robot Framework 7.0.
    """
    if isinstance(timestamp, datetime):
        return timestamp
    try:
        return datetime.fromisoformat(timestamp)
    except ValueError:
        pass
    orig = timestamp
    for sep in ('-', '_', ' ', 'T', ':', '.'):
        if sep in timestamp:
            timestamp = timestamp.replace(sep, '')
    timestamp = timestamp.ljust(20, '0')
    try:
        return datetime(int(timestamp[0:4]), int(timestamp[4:6]), int(timestamp[6:8]),
                        int(timestamp[8:10]), int(timestamp[10:12]), int(timestamp[12:14]),
                        int(timestamp[14:20]))
    except ValueError:
        raise ValueError(f"Invalid timestamp '{orig}'.")


def parse_time(timestr):
    """Parses the time string and returns its value as seconds since epoch.

    Time can be given in five different formats:

    1) Numbers are interpreted as time since epoch directly. It is possible to
       use also ints and floats, not only strings containing numbers.
    2) Valid timestamp ('YYYY-MM-DD hh:mm:ss' and 'YYYYMMDD hhmmss').
    3) 'NOW' (case-insensitive) is the current local time.
    4) 'UTC' (case-insensitive) is the current time in UTC.
    5) Format 'NOW - 1 day' or 'UTC + 1 hour 30 min' is the current local/UTC
       time plus/minus the time specified with the time string.

    Seconds are rounded down to avoid getting times in the future.
    """
    for method in [_parse_time_epoch,
                   _parse_time_timestamp,
                   _parse_time_now_and_utc]:
        seconds = method(timestr)
        if seconds is not None:
            return int(seconds)
    raise ValueError("Invalid time format '%s'." % timestr)


def _parse_time_epoch(timestr):
    try:
        ret = float(timestr)
    except ValueError:
        return None
    if ret < 0:
        raise ValueError("Epoch time must be positive (got %s)." % timestr)
    return ret


def _parse_time_timestamp(timestr):
    try:
        return parse_timestamp(timestr).timestamp()
    except ValueError:
        return None


def _parse_time_now_and_utc(timestr):
    timestr = timestr.replace(' ', '').lower()
    base = _parse_time_now_and_utc_base(timestr[:3])
    if base is not None:
        extra = _parse_time_now_and_utc_extra(timestr[3:])
        if extra is not None:
            return base + extra + _get_dst_difference(base, base + extra)
    return None


def _parse_time_now_and_utc_base(base):
    now = time.time()
    if base == 'now':
        return now
    if base == 'utc':
        zone = time.altzone if time.localtime().tm_isdst else time.timezone
        return now + zone
    return None


def _parse_time_now_and_utc_extra(extra):
    if not extra:
        return 0
    if extra[0] not in ['+', '-']:
        return None
    return (1 if extra[0] == '+' else -1) * timestr_to_secs(extra[1:])


def _get_dst_difference(time1, time2):
    time1_is_dst = time.localtime(time1).tm_isdst
    time2_is_dst = time.localtime(time2).tm_isdst
    if time1_is_dst is time2_is_dst:
        return 0
    difference = time.timezone - time.altzone
    return difference if time1_is_dst else -difference


def get_timestamp(daysep='', daytimesep=' ', timesep=':', millissep='.'):
    """Deprecated in Robot Framework 7.0. Will be removed in Robot Framework 8.0."""
    warnings.warn("'robot.utils.get_timestamp' is deprecated and will be "
                  "removed in Robot Framework 8.0.")
    dt = datetime.now()
    parts = [str(dt.year), daysep, f'{dt.month:02}', daysep, f'{dt.day:02}', daytimesep,
             f'{dt.hour:02}', timesep, f'{dt.minute:02}', timesep, f'{dt.second:02}']
    if millissep:
        # Make sure milliseconds is < 1000. Good enough for a deprecated function.
        millis = min(round(dt.microsecond, -3) // 1000, 999)
        parts.extend([millissep, f'{millis:03}'])
    return ''.join(parts)


def timestamp_to_secs(timestamp, seps=None):
    """Deprecated in Robot Framework 7.0. Will be removed in Robot Framework 8.0."""
    warnings.warn("'robot.utils.timestamp_to_secs' is deprecated and will be "
                  "removed in Robot Framework 8.0. User 'parse_timestamp' instead.")
    try:
        secs = _timestamp_to_millis(timestamp, seps) / 1000.0
    except (ValueError, OverflowError):
        raise ValueError("Invalid timestamp '%s'." % timestamp)
    else:
        return round(secs, 3)


def secs_to_timestamp(secs, seps=None, millis=False):
    """Deprecated in Robot Framework 7.0. Will be removed in Robot Framework 8.0."""
    warnings.warn("'robot.utils.secs_to_timestamp' is deprecated and will be "
                  "removed in Robot Framework 8.0.")
    if not seps:
        seps = ('', ' ', ':', '.' if millis else None)
    ttuple = time.localtime(secs)[:6]
    if millis:
        millis = (secs - int(secs)) * 1000
        ttuple = ttuple + (round(millis),)
    return format_time(ttuple, *seps)


def get_elapsed_time(start_time, end_time):
    """Deprecated in Robot Framework 7.0. Will be removed in Robot Framework 8.0."""
    warnings.warn("'robot.utils.get_elapsed_time' is deprecated and will be "
                  "removed in Robot Framework 8.0.")
    if start_time == end_time or not (start_time and end_time):
        return 0
    if start_time[:-4] == end_time[:-4]:
        return int(end_time[-3:]) - int(start_time[-3:])
    start_millis = _timestamp_to_millis(start_time)
    end_millis = _timestamp_to_millis(end_time)
    return end_millis - start_millis


def elapsed_time_to_string(elapsed: 'int|float|timedelta',
                           include_millis: bool = True,
                           seconds: bool = False):
    """Converts elapsed time to format 'hh:mm:ss.mil'.

    Elapsed time as an integer or as a float is currently considered to be
    milliseconds, but that will be changed to seconds in Robot Framework 8.0.
    Use ``seconds=True`` to change the behavior already now and to avoid the
    deprecation warning. An alternative is giving the elapsed time as
    a ``timedelta``.

    If `include_millis` is True, '.mil' part is omitted.

    Support for giving the elapsed time as a ``timedelta`` and the ``seconds``
    argument are new in Robot Framework 7.0.
    """
    # TODO: Change the default input to seconds in RF 8.0.
    if isinstance(elapsed, timedelta):
        elapsed = elapsed.total_seconds()
    elif not seconds:
        elapsed /= 1000
        warnings.warn("'robot.utils.elapsed_time_to_string' currently accepts "
                      "input as milliseconds, but that will be changed to seconds "
                      "in Robot Framework 8.0. Use 'seconds=True' to change the "
                      "behavior already now and to avoid this warning. Alternatively "
                      "pass the elapsed time as a 'timedelta'.")
    prefix = ''
    if elapsed < 0:
        prefix = '-'
        elapsed = abs(elapsed)
    if include_millis:
        return prefix + _elapsed_time_to_string_with_millis(elapsed)
    return prefix + _elapsed_time_to_string_without_millis(elapsed)


def _elapsed_time_to_string_with_millis(elapsed):
    elapsed = round(elapsed, 3)
    secs = int(elapsed)
    millis = round((elapsed - secs) * 1000)
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return f'{hours:02}:{mins:02}:{secs:02}.{millis:03}'


def _elapsed_time_to_string_without_millis(elapsed):
    secs = round(elapsed)
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return f'{hours:02}:{mins:02}:{secs:02}'


def _timestamp_to_millis(timestamp, seps=None):
    if seps:
        timestamp = _normalize_timestamp(timestamp, seps)
    Y, M, D, h, m, s, millis = _split_timestamp(timestamp)
    secs = time.mktime((Y, M, D, h, m, s, 0, 0, -1))
    return round(1000*secs + millis)


def _normalize_timestamp(ts, seps):
    for sep in seps:
        if sep in ts:
            ts = ts.replace(sep, '')
    ts = ts.ljust(17, '0')
    return f'{ts[:8]} {ts[8:10]}:{ts[10:12]}:{ts[12:14]}.{ts[14:17]}'


def _split_timestamp(timestamp):
    years = int(timestamp[:4])
    mons = int(timestamp[4:6])
    days = int(timestamp[6:8])
    hours = int(timestamp[9:11])
    mins = int(timestamp[12:14])
    secs = int(timestamp[15:17])
    millis = int(timestamp[18:21])
    return years, mons, days, hours, mins, secs, millis
