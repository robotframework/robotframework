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

from datetime import timedelta, datetime
import time
import string
import sys
import re

from robot.utils import elapsed_time_to_string, secs_to_timestr, timestr_to_secs


class DateTime(object):

    def convert_time(self, time, result_format='number', exclude_millis=False):
        return Time(time).convert(result_format, millis=not exclude_millis)

    def convert_date(self, date, result_format='timestamp', exclude_millis=False, date_format=None):
        return Date(date, date_format).convert(result_format, millis=not exclude_millis)

    def subtract_dates(self, date1, date2, result_format='number', exclude_millis=False, date1_format=None, date2_format=None):
        time = Date(date1, date1_format) - Date(date2, date2_format)
        return time.convert(result_format, millis=not exclude_millis)

    def add_to_date(self, date, time, result_format='timestamp', exclude_millis=False, date_format=None):
        date = Date(date, date_format) + Time(time)
        return date.convert(result_format, millis=not exclude_millis)

    def subtract_from_date(self, date, time, result_format='timestamp', exclude_millis=False, date_format=None):
        date = Date(date, date_format) - Time(time)
        return date.convert(result_format, millis=not exclude_millis)

    def add_to_time(self, time1, time2, result_format='number', exclude_millis=False):
        time = Time(time1) + Time(time2)
        return time.convert(result_format, millis=not exclude_millis)

    def subtract_from_time(self, time1, time2, result_format='number', exclude_millis=False):
        time = Time(time1) - Time(time2)
        return time.convert(result_format, millis=not exclude_millis)

    def get_current_date(self, time_zone='local', increment='0', result_format='timestamp', exclude_millis=False):
        dt = self._get_current_date(time_zone.upper())
        date = Date(dt) + Time(increment)
        return date.convert(result_format, millis=not exclude_millis)

    def _get_current_date(self, time_zone):
        if time_zone == 'LOCAL':
            return datetime.now()
        if time_zone == 'UTC':
            return datetime.utcnow()
        raise ValueError('Unsupported timezone %s' % time_zone)

class Time(object):
    _clock_re = re.compile('([-+])?(\d+):(\d{2}):(\d{2})(\.\d{3})?')

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
        if isinstance(time, basestring):
            match = self._clock_re.match(time)
            if match:
                return self._convert_clock_to_secs(match)
        return timestr_to_secs(time)

    def _convert_clock_to_secs(self, match):
        prefix, hours, minutes, seconds, millis = match.groups()
        result = 60 * 60 * int(hours) + 60 * int(minutes) + int(seconds)
        if millis:
            result += int(millis[1:]) / 1000.0
        if prefix == '-':
            result *= -1
        return result

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

    def _convert_to_clock(self, seconds, millis=True):
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
        if '%f' in input_format and (sys.version_info < (2, 6) or
                                     sys.platform == 'cli'):
            return self._handle_un_supported_f_directive(dt, input_format)
        return self._mktime_with_millis(datetime.strptime(dt, input_format))

    def _normalize_timestamp(self, date):
        ts = ''.join(d for d in date if d in string.digits).ljust(20, '0')
        return '%s-%s-%s %s:%s:%s.%s' % (ts[:4], ts[4:6], ts[6:8], ts[8:10],
                                         ts[10:12], ts[12:14], ts[14:])

    def _handle_un_supported_f_directive(self, dt, input_format):
        if not input_format.endswith('%f'):
            raise ValueError('%f directive is supported only at the end of '
                             'the format string on this Python interpreter.')
        input_format = input_format[:-2]
        micro = re.search('\d+$', dt).group(0)
        dt = dt[:-len(micro)]
        epoch = time.mktime(time.strptime(dt, input_format))
        epoch += float(micro) / 10**len(micro)
        return epoch

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
