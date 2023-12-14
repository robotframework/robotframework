import unittest
import re
import time
import warnings
from datetime import datetime, timedelta

from robot.utils.asserts import (assert_equal, assert_raises_with_msg,
                                 assert_true, assert_not_none)

from robot.utils.robottime import (timestr_to_secs, secs_to_timestr, get_time,
                                   parse_time, format_time, get_elapsed_time,
                                   get_timestamp, timestamp_to_secs, parse_timestamp,
                                   elapsed_time_to_string, _get_timetuple)


EXAMPLE_TIME = time.mktime(datetime(2007, 9, 20, 16, 15, 14).timetuple())


class TestTime(unittest.TestCase):

    def test_get_timetuple_excluding_millis(self):
        assert_equal(_get_timetuple(12345)[:-1], time.localtime(12345)[:6])

    def test_get_current_timetuple_excluding_millis(self):
        while True:
            expected = time.localtime(time.time())
            actual = _get_timetuple()
            # make sure got same times and _get_timetuple() did not round millis
            if expected == time.localtime(time.time()) and actual[-1] > 0:
                break
        assert_equal(actual[:-1], expected[:6])

    def test_get_timetuple_millis(self):
        assert_equal(_get_timetuple(12345)[-2:], (45, 0))
        assert_equal(_get_timetuple(12345.12345)[-2:], (45, 123))
        assert_equal(_get_timetuple(12345.67890)[-2:], (45, 679))
        assert_equal(_get_timetuple(12345.99999)[-2:], (46, 0))

    def test_timestr_to_secs_with_numbers(self):
        for inp, exp in [(1, 1),
                         (42, 42),
                         (1.1, 1.1),
                         (3.142, 3.142),
                         (-1, -1),
                         (-1.1, -1.1),
                         (0, 0),
                         (0.55555, 0.556),
                         (11.111111, 11.111),
                         ('1e2', 100),
                         ('-1.5e3', -1500)]:
            assert_equal(timestr_to_secs(inp), exp, inp)
            if not isinstance(inp, str):
                assert_equal(timestr_to_secs(str(inp)), exp, inp)

    def test_timestr_to_secs_uses_bankers_rounding(self):
        assert_equal(timestr_to_secs(0.1, 0), 0)
        assert_equal(timestr_to_secs(0.5, 0), 0)
        assert_equal(timestr_to_secs(0.51, 0), 1)
        assert_equal(timestr_to_secs(0.99, 0), 1)
        assert_equal(timestr_to_secs(1.0, 0), 1)
        assert_equal(timestr_to_secs(1.499, 0), 1)
        assert_equal(timestr_to_secs(1.5, 0), 2)

    def test_timestr_to_secs_with_time_string(self):
        for inp, exp in [('1s', 1),
                         ('0 day 1 MINUTE 2 S 42 millis', 62.042),
                         ('1minute 0sec 10 millis', 60.01),
                         ('9 9 secs    5  3 4 m i l l i s e co n d s', 99.534),
                         ('10DAY10H10M10SEC', 900610),
                         ('1day 23h 46min 7s 666ms', 171967.666),
                         ('1.5min 1.5s', 91.5),
                         ('1.5 days', 60*60*36),
                         ('1 day', 60*60*24),
                         ('2 days', 2*60*60*24),
                         ('1 d', 60*60*24),
                         ('1 hour', 60*60),
                         ('3 hours', 3*60*60),
                         ('1 h', 60*60),
                         ('1 minute', 60),
                         ('2 minutes', 2*60),
                         ('1 min', 60),
                         ('2 mins', 2*60),
                         ('1 m', 60),
                         ('1M', 60),
                         ('1 second', 1),
                         ('2 seconds', 2),
                         ('1 sec', 1),
                         ('2 secs', 2),
                         ('1 s', 1),
                         ('1 millisecond', 0.001),
                         ('2 milliseconds', 0.002),
                         ('1 millisec', 0.001),
                         ('2 millisecs', 0.002),
                         ('1234 millis', 1.234),
                         ('1 msec', 0.001),
                         ('2 msecs', 0.002),
                         ('1 ms', 0.001),
                         ('-1s', -1),
                         ('- 1 min 2 s', -62),
                         ('0.1millis', 0),
                         ('0.5ms', 0.001),
                         ('0day 0hour 0minute 0seconds 0millisecond', 0)]:
            assert_equal(timestr_to_secs(inp), exp, inp)

    def test_timestr_to_secs_with_time_string_ns_accuracy(self):
        for input, expected in [("1 us", 1E-6),
                                ("1 μs", 1E-6),
                                ("1 microsecond", 1E-6),
                                ("1 microseconds", 1E-6),
                                ("2 us", 2E-6),
                                ("1 ns", 1E-9),
                                ("1 nanosecond", 1E-9),
                                ("1 nanoseconds", 1E-9),
                                ("2 ns", 2E-9),
                                ("-100 ns", -100E-9),
                                ("1.2us", 1.2E-6)]:
            assert_equal(timestr_to_secs(input, round_to=9), expected)

    def test_timestr_to_secs_with_timer_string(self):
        for inp, exp in [('00:00:00', 0),
                         ('00:00:01', 1),
                         ('01:02:03', 3600 + 2*60 + 3),
                         ('100:00:00', 100*3600),
                         ('1:00:00', 3600),
                         ('11:00:00', 11*3600),
                         ('00:00', 0),
                         ('00:01', 1),
                         ('42:01', 42*60 + 1),
                         ('100:00', 100*60),
                         ('100:100', 100*60 + 100),
                         ('100:100:100', 100*3600 + 100*60 + 100),
                         ('1:1:1', 3600 + 60 + 1),
                         ('0001:0001:0001', 3600 + 60 + 1),
                         ('-00:00:00', 0),
                         ('-00:01:10', -70),
                         ('-1:2:3', -3600 - 2*60 - 3),
                         ('+00:00:00', 0),
                         ('+00:01:10', 70),
                         ('+1:2:3', 3600 + 2*60 + 3),
                         ('00:00:00.0', 0),
                         ('00:00:00.000', 0),
                         ('00:00:00.000000000', 0),
                         ('00:00:00.1', 0.1),
                         ('00:00:00.42', 0.42),
                         ('00:00:00.001', 0.001),
                         ('00:00:00.123', 0.123),
                         ('00:00:00.1234', 0.123),
                         ('00:00:00.12345', 0.123),
                         ('00:00:00.12356', 0.124),
                         ('00:00:00.999', 0.999),
                         ('00:00:00.9995001', 1),
                         ('00:00:00.000000001', 0)]:
            assert_equal(timestr_to_secs(inp), exp, inp)
            if '.' not in inp:
                inp += '.500'
                exp += 0.5 if inp[0] != '-' else -0.5
                assert_equal(timestr_to_secs(inp), exp, inp)

    def test_timestr_to_secs_with_timedelta(self):
        assert_equal(timestr_to_secs(timedelta(minutes=1)), 60)
        assert_equal(timestr_to_secs(timedelta(microseconds=1000)), 0.001)

    def test_timestr_to_secs_custom_rounding(self):
        secs = 0.123456789
        for round_to in 0, 1, 6:
            expected = round(secs, round_to)
            assert_equal(timestr_to_secs(secs, round_to), expected)
            assert_equal(timestr_to_secs(str(secs), round_to), expected)

    def test_timestr_to_secs_no_rounding(self):
        secs = 0.123456789
        assert_equal(timestr_to_secs(secs, round_to=None), secs)
        assert_equal(timestr_to_secs(str(secs), round_to=None), secs)

    def test_timestr_to_secs_with_invalid(self):
        for inv in ['', 'foo', 'foo days', '1sec 42 millis 3', '1min 2w', '1x',
                    '01:02:03:04', '01:02:03foo', 'foo01:02:03', None]:
            assert_raises_with_msg(ValueError, f"Invalid time string '{inv}'.",
                                   timestr_to_secs, inv)

    def test_secs_to_timestr(self):
        for inp, compact, verbose in [
            (0.001, '1ms', '1 millisecond'),
            (0.002, '2ms', '2 milliseconds'),
            (0.9999, '1s', '1 second'),
            (1, '1s', '1 second'),
            (1.9999, '2s', '2 seconds'),
            (2, '2s', '2 seconds'),
            (60, '1min', '1 minute'),
            (120, '2min', '2 minutes'),
            (3600, '1h', '1 hour'),
            (7200, '2h', '2 hours'),
            (60*60*24, '1d', '1 day'),
            (60*60*48, '2d', '2 days'),
            (171967.667, '1d 23h 46min 7s 667ms',
             '1 day 23 hours 46 minutes 7 seconds 667 milliseconds'),
            (7320, '2h 2min', '2 hours 2 minutes'),
            (7210.05, '2h 10s 50ms', '2 hours 10 seconds 50 milliseconds') ,
            (11.1111111, '11s 111ms', '11 seconds 111 milliseconds'),
            (0.55555555, '556ms', '556 milliseconds'),
            (0, '0s', '0 seconds'),
            (9999.9999, '2h 46min 40s', '2 hours 46 minutes 40 seconds'),
            (10000, '2h 46min 40s', '2 hours 46 minutes 40 seconds'),
            (-1, '- 1s', '- 1 second'),
            (-171967.667, '- 1d 23h 46min 7s 667ms',
             '- 1 day 23 hours 46 minutes 7 seconds 667 milliseconds')]:
            assert_equal(secs_to_timestr(inp, compact=True), compact, inp)
            assert_equal(secs_to_timestr(inp), verbose, inp)
            assert_equal(secs_to_timestr(timedelta(seconds=inp)), verbose, inp)

    def test_format_time(self):
        timetuple = (2005, 11, 2, 14, 23, 12, 123)
        for seps, exp in [(('-',' ',':'), '2005-11-02 14:23:12'),
                          (('', '-', ''), '20051102-142312'),
                          (('-',' ',':','.'), '2005-11-02 14:23:12.123')]:
            with warnings.catch_warnings(record=True):
                assert_equal(format_time(timetuple, *seps), exp)

    def test_get_timestamp(self):
        for seps, pattern in [
            ((), r'^\d{8} \d\d:\d\d:\d\d.\d\d\d$'),
            (('', ' ', ':', None), r'^\d{8} \d\d:\d\d:\d\d$'),
            (('', '', '', None), r'^\d{14}$'),
            (('-', '&nbsp;', ':', ';'), r'^\d{4}-\d\d-\d\d&nbsp;\d\d:\d\d:\d\d;\d\d\d$')
        ]:
            with warnings.catch_warnings(record=True):
                ts = get_timestamp(*seps)
            assert_not_none(re.search(pattern, ts),
                            "'%s' didn't match '%s'" % (ts, pattern), False)

    def test_timestamp_to_secs(self):
        with warnings.catch_warnings(record=True):
            assert_equal(timestamp_to_secs('20070920 16:15:14.123'), EXAMPLE_TIME+0.123)
            assert_equal(timestamp_to_secs('20070920T16:15:14.123'), EXAMPLE_TIME+0.123)
            assert_equal(timestamp_to_secs('2007-09-20#16x15x14M123', ('-','#','x','M')),
                         EXAMPLE_TIME+0.123)
            assert_equal(timestamp_to_secs('20070920 16:15:14.123'), EXAMPLE_TIME+0.123)

    def test_get_elapsed_time(self):
        starttime = '20060526 14:01:10.500'
        for endtime, expected in [('20060526 14:01:10.500', 0),
                                  ('20060526 14:01:10.500',0),
                                  ('20060526 14:01:10.501', 1),
                                  ('20060526 14:01:10.777', 277),
                                  ('20060526 14:01:11.000', 500),
                                  ('20060526 14:01:11.321', 821),
                                  ('20060526 14:01:11.499', 999),
                                  ('20060526 14:01:11.500', 1000),
                                  ('20060526 14:01:11.501', 1001),
                                  ('20060526 14:01:11.000', 500),
                                  ('20060526 14:01:11.500', 1000),
                                  ('20060526 14:01:11.510', 1010),
                                  ('20060526 14:01:11.512',1012),
                                  ('20060601 14:01:10.499', 518399999),
                                  ('20060601 14:01:10.500', 518400000),
                                  ('20060601 14:01:10.501', 518400001)]:
            with warnings.catch_warnings(record=True):
                actual = get_elapsed_time(starttime, endtime)
            assert_equal(actual, expected, endtime)

    def test_get_elapsed_time_negative(self):
        starttime = '20060526 14:01:10.500'
        for endtime, expected in [('20060526 14:01:10.499', -1),
                                  ('20060526 14:01:10.000', -500),
                                  ('20060526 14:01:09.900', -600),
                                  ('20060526 14:01:09.501', -999),
                                  ('20060526 14:01:09.500', -1000),
                                  ('20060526 14:01:09.499', -1001)]:
            with warnings.catch_warnings(record=True):
                actual = get_elapsed_time(starttime, endtime)
            assert_equal(actual, expected, endtime)

    def test_elapsed_time_to_string(self):
        for elapsed, expected in [(0, '00:00:00.000'),
                                  (0.0001, '00:00:00.000'),
                                  (0.00049, '00:00:00.000'),
                                  (0.00050, '00:00:00.001'),
                                  (0.00051, '00:00:00.001'),
                                  (0.001, '00:00:00.001'),
                                  (0.0015, '00:00:00.002'),
                                  (0.042, '00:00:00.042'),
                                  (0.999, '00:00:00.999'),
                                  (0.9999, '00:00:01.000'),
                                  (1.0, '00:00:01.000'),
                                  (1, '00:00:01.000'),
                                  (1.001, '00:00:01.001'),
                                  (60, '00:01:00.000'),
                                  (600, '00:10:00.000'),
                                  (654.321, '00:10:54.321'),
                                  (660, '00:11:00.000'),
                                  (3600, '01:00:00.000'),
                                  (36000, '10:00:00.000'),
                                  (360000, '100:00:00.000'),
                                  (360000 + 36000 + 3600 + 660 + 11.111,
                                   '111:11:11.111')]:
            assert_equal(elapsed_time_to_string(elapsed, seconds=True),
                         expected, elapsed)
            assert_equal(elapsed_time_to_string(timedelta(seconds=elapsed)),
                         expected, elapsed)
            if elapsed != 0:
                assert_equal(elapsed_time_to_string(-elapsed, seconds=True),
                             '-' + expected, elapsed)
                assert_equal(elapsed_time_to_string(timedelta(seconds=-elapsed)),
                             '-' + expected, elapsed)

    def test_elapsed_time_to_string_without_millis(self):
        for elapsed, expected in [(0, '00:00:00'),
                                  (0.001, '00:00:00'),
                                  (0.5, '00:00:00'),
                                  (0.501, '00:00:01'),
                                  (0.999, '00:00:01'),
                                  (1.0, '00:00:01'),
                                  (1, '00:00:01'),
                                  (1.4999, '00:00:01'),
                                  (1.500, '00:00:02'),
                                  (59.4999, '00:00:59'),
                                  (59.5, '00:01:00'),
                                  (59.999, '00:01:00'),
                                  (60, '00:01:00'),
                                  (654.321, '00:10:54'),
                                  (654.500, '00:10:54'),
                                  (654.501, '00:10:55'),
                                  (3599.999, '01:00:00'),
                                  (3600, '01:00:00'),
                                  (359999.999, '100:00:00'),
                                  (360000, '100:00:00'),
                                  (360000.5, '100:00:00'),
                                  (360000.501, '100:00:01')]:
            assert_equal(elapsed_time_to_string(elapsed, include_millis=False,
                                                seconds=True),
                         expected, elapsed)
            if expected != '00:00:00':
                assert_equal(elapsed_time_to_string(-1 * elapsed, False, True),
                             '-' + expected, elapsed)

    def test_elapsed_time_default_input_is_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            assert_equal(elapsed_time_to_string(1000), '00:00:01.000')
        assert_equal(str(w[0].message),
                     "'robot.utils.elapsed_time_to_string' currently accepts input "
                     "as milliseconds, but that will be changed to seconds in "
                     "Robot Framework 8.0. Use 'seconds=True' to change the behavior "
                     "already now and to avoid this warning. Alternatively pass "
                     "the elapsed time as a 'timedelta'.")

    def test_parse_timestamp(self):
        for timestamp in ['2023-09-08 23:34:45.123456',
                          '2023-09-08T23:34:45.123456',
                          '2023-09-08 23:34:45:123456',
                          '2023:09:08:23:34:45:123456',
                          '20230908 23:34:45.123456',
                          '2023_09_08 233445.123456',
                          '20230908233445123456']:
            assert_equal(parse_timestamp(timestamp),
                         datetime(2023, 9, 8, 23, 34, 45, 123456))

    def test_parse_timestamp_fill_missing(self):
        for timestamp, expected in [
            ('2023-09-08 23:34:45.123', '2023-09-08 23:34:45.123'),
            ('2023-09-08 23:34:45', '2023-09-08 23:34:45'),
            ('20230908 23:34:45', '2023-09-08 23:34:45'),
            ('2023-09-08 23:34', '2023-09-08 23:34:00'),
            ('20230101', '2023-01-01 00:00:00')
        ]:
            assert_equal(parse_timestamp(timestamp),
                         datetime.fromisoformat(expected))

    def test_parse_timestamp_with_datetime(self):
        dt = datetime.now()
        assert_equal(parse_timestamp(dt), dt)

    def test_parse_timestamp_invalid(self):
        assert_raises_with_msg(ValueError,
                               "Invalid timestamp 'bad'.",
                               parse_timestamp,
                               'bad')

    def test_parse_time_with_valid_times(self):
        for input, expected in [('100', 100),
                                ('2007-09-20 16:15:14', EXAMPLE_TIME),
                                ('20070920 161514', EXAMPLE_TIME)]:
            assert_equal(parse_time(input), expected)

    def test_parse_time_with_now_and_utc(self):
        for input, adjusted in [('now', 0),
                                ('NOW', 0),
                                ('Now', 0),
                                ('now+100seconds', 100),
                                ('now    -    100    seconds   ', -100),
                                ('now + 1 day 100 seconds', 86500),
                                ('now - 1 day 100 seconds', -86500),
                                ('now + 1day 10hours 1minute 10secs', 122470),
                                ('NOW - 1D 10H 1MIN 10S', -122470)]:
            now = int(time.time())
            parsed = parse_time(input)
            expected = now + adjusted
            if time.localtime(now).tm_isdst is not time.localtime(expected).tm_isdst:
                dst_diff = time.timezone - time.altzone
                expected += dst_diff if time.localtime(now).tm_isdst else -dst_diff
            assert_true(expected - parsed < 0.1)
            parsed = parse_time(input.upper().replace('NOW', 'UtC'))
            zone = time.altzone if time.localtime(now).tm_isdst else time.timezone
            expected += zone
            assert_true(expected - parsed < 0.1)

    def test_get_time_with_zero(self):
        assert_equal(get_time('epoch', 0), 0)

    def test_parse_modified_time_with_invalid_times(self):
        for value, msg in [("-100", "Epoch time must be positive (got -100)."),
                           ("YYYY-MM-DD hh:mm:ss",
                            "Invalid time format 'YYYY-MM-DD hh:mm:ss'."),
                           ("now + foo", "Invalid time string 'foo'."),
                           ("now -    2a ", "Invalid time string '2a'."),
                           ("now+", "Invalid time string ''."),
                           ("nowadays", "Invalid time format 'nowadays'.")]:
            assert_raises_with_msg(ValueError, msg, parse_time, value)

    def test_parse_time_and_get_time_must_round_seconds_down(self):
        # Rounding to closest second, instead of rounding down, could give
        # times that are greater then e.g. timestamps of files created
        # afterwards.
        self._verify_parse_time_and_get_time_rounding()
        time.sleep(0.5)
        self._verify_parse_time_and_get_time_rounding()

    def _verify_parse_time_and_get_time_rounding(self):
        secs = lambda: int(time.time()) % 60
        start_secs = secs()
        gt_result = get_time()[-2:]
        pt_result = parse_time('NOW') % 60
        # Check that seconds have not changed during test
        if secs() == start_secs:
            assert_equal(gt_result, '%02d' % start_secs)
            assert_equal(pt_result, start_secs)


if __name__ == "__main__":
    unittest.main()
