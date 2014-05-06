from datetime import timedelta, datetime
import time
import string
import sys
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
        if isinstance(dt, basestring):
            dt = self._string_to_datetime(dt, input_format)
        elif isinstance(dt, (int, long, float)):
            dt = self._dt_from_timestamp(dt)
        elif not isinstance(dt, datetime):
            raise ValueError("Unsupported input '%s'." % dt)
        return self._round_dt_to_millis(dt)

    def _round_dt_to_millis(self, dt):
        return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                        dt.second, int(round(dt.microsecond, -3)))

    def _string_to_datetime(self, dt, input_format):
        if not input_format:
            dt = self._normalize_timestamp(dt)
            input_format = '%Y-%m-%d %H:%M:%S.%f'
        if '%f' in input_format and (sys.version_info < (2, 6) or
                                     sys.platform == 'cli'):
            return self._handle_un_supported_f_directive(dt, input_format)
        return datetime.strptime(dt, input_format)

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
        return self._dt_from_timestamp(epoch)

    def _dt_from_timestamp(self, ts):
        # Jython and IronPython handle floats incorrectly. For example,
        # datetime.fromtimestamp(1399410716.123).microsecond == 122999
        dt = datetime.fromtimestamp(ts)
        return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                        dt.second, int(round(ts % 1 * 10**6, -3)))

    def convert(self, format):
        try:
            result_converter = getattr(self, '_convert_to_%s' % format.lower())
        except AttributeError:
            raise ValueError("Unknown format '%s'." % format)
        return result_converter(self.dt)

    def _convert_to_timestamp(self, dt):
        if dt.microsecond:
            return str(dt)[:-3]
        return str(dt)

    def _convert_to_epoch(self, dt):
        return time.mktime(dt.timetuple())

    def _convert_to_datetime(self, dt):
        return dt
