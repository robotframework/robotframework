from datetime import timedelta
import re

from robot.utils import elapsed_time_to_string, secs_to_timestr, timestr_to_secs


class DateTime(object):

    def convert_time(self, time, result_format='number', exclude_millis=False):
        return Time(time).convert(result_format, millis=not exclude_millis)


class Time(object):
    _clock_re = re.compile('(\d{2,}):(\d{2}):(\d{2})(\.(\d{3}))?')

    def __init__(self, time):
        self.seconds = self._convert_time_to_seconds(time)

    def _convert_time_to_seconds(self, time):
        if isinstance(time, timedelta):
            return time.total_seconds()
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
