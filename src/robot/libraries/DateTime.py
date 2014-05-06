from datetime import timedelta, datetime
import time
from string import digits
import re

from robot.utils import elapsed_time_to_string, secs_to_timestr, timestr_to_secs


class DateTime(object):

    def convert_time(self, time, result_format='number', exclude_millis=False):
        return Time(time).convert(result_format, millis=not exclude_millis)

    def convert_date(self, date, result_format='timestamp', input_format=None):
        return Date(date, input_format).convert(result_format)


class Time(object):
    _clock_re = re.compile('(\d{2,}):(\d{2}):(\d{2})(\.(\d{3}))?')

    def __init__(self, time):
        self.seconds = self._convert_time_to_seconds(time)

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
        hours, minutes, seconds, millis_included, millis = match.groups()
        result = 60 * 60 * int(hours) + 60 * int(minutes) + int(seconds)
        print match.groups()
        if millis_included:
            result += int(millis) / 1000.0
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
    def __init__(self, dt, input_format):
        self.dt = self._convert_to_dt(dt, input_format)

    def _convert_to_dt(self, dt, input_format):
        if isinstance(dt, datetime):
            return dt
        if isinstance(dt, basestring):
            return self._string_to_datetime(dt, input_format)
        if isinstance(dt, (int, long, float)):
            return datetime.fromtimestamp(dt)

    def _string_to_datetime(self, dt, input_format):
        if not input_format:
            dt = self._normalize_timestamp(dt)
            input_format = '%Y-%m-%d %H:%M:%S.%f'
        return datetime.strptime(dt, input_format)

    def _normalize_timestamp(self, date):
        stamp = ''.join(digit for digit in date if digit in digits)
        stamp = stamp.ljust(17, '0')
        return '%s-%s-%s %s:%s:%s.%s' % (stamp[:4], stamp[4:6], stamp[6:8], stamp[8:10],
                                         stamp[10:12], stamp[12:14], stamp[14:17])

    def convert(self, output_format):
        try:
            result_converter = getattr(self, '_convert_to_%s' % output_format.lower())
        except AttributeError:
            raise ValueError("Unknown format '%s'." % output_format)
        return result_converter()

    def _convert_to_timestamp(self):
        if self.dt.microsecond:
            return str(self.dt)[:-3]
        return str(self.dt)

    def _convert_to_epoch(self):
        return time.mktime(self.dt.timetuple())

    def _convert_to_datetime(self):
        return self.dt
