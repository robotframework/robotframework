#  Copyright 2008-2015 Nokia Solutions and Networks
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

import datetime
import time
import re

from .normalizing import normalize
from .misc import plural_or_not, roundup
from .robottypes import is_number, is_string


_timer_re = re.compile('([+-])?(\d+:)?(\d+):(\d+)(.\d+)?')


def _get_timetuple(epoch_secs=None):
    if epoch_secs is None:  # can also be 0 (at least in unit tests)
        epoch_secs = time.time()
    secs, millis = _float_secs_to_secs_and_millis(epoch_secs)
    timetuple = time.localtime(secs)[:6]  # from year to secs
    return timetuple + (millis,)

def _float_secs_to_secs_and_millis(secs):
    isecs = int(secs)
    millis = roundup((secs - isecs) * 1000)
    return (isecs, millis) if millis < 1000 else (isecs+1, 0)


def timestr_to_secs(timestr, round_to=3):
    """Parses time like '1h 10s', '01:00:10' or '42' and returns seconds."""
    if is_string(timestr) or is_number(timestr):
        for converter in _number_to_secs, _timer_to_secs, _time_string_to_secs:
            secs = converter(timestr)
            if secs is not None:
                return secs if round_to is None else roundup(secs, round_to)
    raise ValueError("Invalid time string '%s'." % timestr)

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
    millis = secs = mins = hours = days = 0
    if timestr[0] == '-':
        sign = -1
        timestr = timestr[1:]
    else:
        sign = 1
    temp = []
    for c in timestr:
        try:
            if   c == 'x': millis = float(''.join(temp)); temp = []
            elif c == 's': secs   = float(''.join(temp)); temp = []
            elif c == 'm': mins   = float(''.join(temp)); temp = []
            elif c == 'h': hours  = float(''.join(temp)); temp = []
            elif c == 'd': days   = float(''.join(temp)); temp = []
            else: temp.append(c)
        except ValueError:
            return None
    if temp:
        return None
    return sign * (millis/1000 + secs + mins*60 + hours*60*60 + days*60*60*24)

def _normalize_timestr(timestr):
    timestr = normalize(timestr)
    for specifier, aliases in [('x', ['millisecond', 'millisec', 'millis',
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


def secs_to_timestr(secs, compact=False):
    """Converts time in seconds to a string representation.

    Returned string is in format like
    '1 day 2 hours 3 minutes 4 seconds 5 milliseconds' with following rules:

    - Time parts having zero value are not included (e.g. '3 minutes 4 seconds'
      instead of '0 days 0 hours 3 minutes 4 seconds')
    - Hour part has a maximun of 23 and minutes and seconds both have 59
      (e.g. '1 minute 40 seconds' instead of '100 seconds')

    If compact has value 'True', short suffixes are used.
    (e.g. 1d 2h 3min 4s 5ms)
    """
    return _SecsToTimestrHelper(secs, compact).get_value()


class _SecsToTimestrHelper:

    def __init__(self, float_secs, compact):
        self._compact = compact
        self._ret = []
        self._sign, millis, secs, mins, hours, days \
                = self._secs_to_components(float_secs)
        self._add_item(days, 'd', 'day')
        self._add_item(hours, 'h', 'hour')
        self._add_item(mins, 'min', 'minute')
        self._add_item(secs, 's', 'second')
        self._add_item(millis, 'ms', 'millisecond')

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
                millissep=None, gmtsep=None):
    """Returns a timestamp formatted from given time using separators.

    Time can be given either as a timetuple or seconds after epoch.

    Timetuple is (year, month, day, hour, min, sec[, millis]), where parts must
    be integers and millis is required only when millissep is not None.
    Notice that this is not 100% compatible with standard Python timetuples
    which do not have millis.

    Seconds after epoch can be either an integer or a float.
    """
    if is_number(timetuple_or_epochsecs):
        timetuple = _get_timetuple(timetuple_or_epochsecs)
    else:
        timetuple = timetuple_or_epochsecs
    daytimeparts = ['%02d' % t for t in timetuple[:6]]
    day = daysep.join(daytimeparts[:3])
    time_ = timesep.join(daytimeparts[3:6])
    millis = millissep and '%s%03d' % (millissep, timetuple[6]) or ''
    return day + daytimesep + time_ + millis + _diff_to_gmt(gmtsep)

def _diff_to_gmt(sep):
    if not sep:
        return ''
    if time.altzone == 0:
        sign = ''
    elif time.altzone > 0:
        sign = '-'
    else:
        sign = '+'
    minutes = abs(time.altzone) / 60.0
    hours, minutes = divmod(minutes, 60)
    return '%sGMT%s%s%02d:%02d' % (sep, sep, sign, hours, minutes)


def get_time(format='timestamp', time_=None):
    """Return the given or current time in requested format.

    If time is not given, current time is used. How time is returned is
    is deternined based on the given 'format' string as follows. Note that all
    checks are case insensitive.

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
    time_ = int(time_ or time.time())
    format = format.lower()
    # 1) Return time in seconds since epoc
    if 'epoch' in format:
        return time_
    timetuple = time.localtime(time_)
    parts = []
    for i, match in enumerate('year month day hour min sec'.split()):
        if match in format:
            parts.append('%.2d' % timetuple[i])
    # 2) Return time as timestamp
    if not parts:
        return format_time(timetuple, daysep='-')
    # Return requested parts of the time
    elif len(parts) == 1:
        return parts[0]
    else:
        return parts


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
        return timestamp_to_secs(timestr, (' ', ':', '-', '.'))
    except ValueError:
        return None

def _parse_time_now_and_utc(timestr):
    timestr = timestr.replace(' ', '').lower()
    base = _parse_time_now_and_utc_base(timestr[:3])
    if base is not None:
        extra = _parse_time_now_and_utc_extra(timestr[3:])
        if extra is not None:
            return base + extra
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


def get_timestamp(daysep='', daytimesep=' ', timesep=':', millissep='.'):
    return TIMESTAMP_CACHE.get_timestamp(daysep, daytimesep, timesep, millissep)


def timestamp_to_secs(timestamp, seps=None):
    try:
        secs = _timestamp_to_millis(timestamp, seps) / 1000.0
    except (ValueError, OverflowError):
        raise ValueError("Invalid timestamp '%s'." % timestamp)
    else:
        return roundup(secs, 3)


def secs_to_timestamp(secs, seps=None, millis=False):
    if not seps:
        seps = ('', ' ', ':', '.' if millis else None)
    ttuple = time.localtime(secs)[:6]
    if millis:
        millis = (secs - int(secs)) * 1000
        ttuple = ttuple + (roundup(millis),)
    return format_time(ttuple, *seps)


def get_elapsed_time(start_time, end_time):
    """Returns the time between given timestamps in milliseconds."""
    if start_time == end_time or not (start_time and end_time):
        return 0
    if start_time[:-4] == end_time[:-4]:
        return int(end_time[-3:]) - int(start_time[-3:])
    start_millis = _timestamp_to_millis(start_time)
    end_millis = _timestamp_to_millis(end_time)
    # start/end_millis can be long but we want to return int when possible
    return int(end_millis - start_millis)


def elapsed_time_to_string(elapsed, include_millis=True):
    """Converts elapsed time in milliseconds to format 'hh:mm:ss.mil'.

    If `include_millis` is True, '.mil' part is omitted.
    """
    prefix = ''
    if elapsed < 0:
        prefix = '-'
        elapsed = abs(elapsed)
    if include_millis:
        return prefix + _elapsed_time_to_string(elapsed)
    return prefix + _elapsed_time_to_string_without_millis(elapsed)

def _elapsed_time_to_string(elapsed):
    secs, millis = divmod(roundup(elapsed), 1000)
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d.%03d' % (hours, mins, secs, millis)

def _elapsed_time_to_string_without_millis(elapsed):
    secs = roundup(elapsed, ndigits=-3) // 1000
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def _timestamp_to_millis(timestamp, seps=None):
    if seps:
        timestamp = _normalize_timestamp(timestamp, seps)
    Y, M, D, h, m, s, millis = _split_timestamp(timestamp)
    secs = time.mktime(datetime.datetime(Y, M, D, h, m, s).timetuple())
    return roundup(1000*secs + millis)

def _normalize_timestamp(ts, seps):
    for sep in seps:
        if sep in ts:
            ts = ts.replace(sep, '')
    ts = ts.ljust(17, '0')
    return '%s%s%s %s:%s:%s.%s' % (ts[:4], ts[4:6], ts[6:8], ts[8:10],
                                   ts[10:12], ts[12:14], ts[14:17])

def _split_timestamp(timestamp):
    years = int(timestamp[:4])
    mons = int(timestamp[4:6])
    days = int(timestamp[6:8])
    hours = int(timestamp[9:11])
    mins = int(timestamp[12:14])
    secs = int(timestamp[15:17])
    millis = int(timestamp[18:21])
    return years, mons, days, hours, mins, secs, millis


class TimestampCache(object):

    def __init__(self):
        self._previous_secs = None
        self._previous_separators = None
        self._previous_timestamp = None

    def get_timestamp(self, daysep='', daytimesep=' ', timesep=':', millissep='.'):
        epoch = self._get_epoch()
        secs, millis = _float_secs_to_secs_and_millis(epoch)
        if self._use_cache(secs, daysep, daytimesep, timesep):
            return self._cached_timestamp(millis, millissep)
        timestamp = format_time(epoch, daysep, daytimesep, timesep, millissep)
        self._cache_timestamp(secs, timestamp, daysep, daytimesep, timesep, millissep)
        return timestamp

    # Seam for mocking
    def _get_epoch(self):
        return time.time()

    def _use_cache(self, secs, *separators):
        return self._previous_timestamp \
            and self._previous_secs == secs \
            and self._previous_separators == separators

    def _cached_timestamp(self, millis, millissep):
        if millissep:
            return self._previous_timestamp + millissep + format(millis, '03d')
        return self._previous_timestamp

    def _cache_timestamp(self, secs, timestamp, daysep, daytimesep, timesep, millissep):
        self._previous_secs = secs
        self._previous_separators = (daysep, daytimesep, timesep)
        self._previous_timestamp = timestamp[:-4] if millissep else timestamp


TIMESTAMP_CACHE = TimestampCache()
