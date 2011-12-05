import unittest
import sys
import re
import time
import datetime

from robot.utils.asserts import (assert_equal, assert_raises_with_msg,
                                 assert_true, assert_not_none)

from robot.utils.robottime import (timestr_to_secs, secs_to_timestr, get_time,
                                   parse_time, format_time, get_elapsed_time,
                                   get_timestamp, get_start_timestamp,
                                   timestamp_to_secs, _get_timetuple)


EXAMPLE_TIME = time.mktime(datetime.datetime(2007, 9, 20, 16, 15, 14).timetuple())


class TestTime(unittest.TestCase):

    def test_get_timetuple_excluding_millis(self):
        assert_equal(_get_timetuple(12345)[:-1], time.localtime(12345)[:6])

    def test_get_current_timetuple_excluding_millis(self):
        while True:
            expected = time.localtime()
            actual = _get_timetuple()
            if expected == time.localtime():
                break
        assert_equal(actual[:-1], expected[:6])

    def test_get_timetuple_millis(self):
        assert_equal(_get_timetuple(12345)[-2:], (45, 0))
        assert_equal(_get_timetuple(12345.12345)[-2:], (45, 123))
        assert_equal(_get_timetuple(12345.67890)[-2:], (45, 679))
        assert_equal(_get_timetuple(12345.99999)[-2:], (46, 0))

    def test_timestr_to_secs(self):
        for inp, exp in [('1', 1),
                         ('42', 42),
                         (1, 1),
                         (1.1, 1.1),
                         ('3.141', 3.141),
                         ('1s', 1),
                         ('0 day 1 MINUTE 2 S 42 millis', 62.042),
                         ('1minute 0sec 10 millis', 60.01),
                         ('9 9 secs    5  3 4 m i l l i s e co n d s', 99.534),
                         ('10DAY10H10M10SEC', 900610),
                         ('1day 23h 46min 7s 666ms', 171967.666),
                         ('1.5min 1.5s', 91.5),
                         ('1 day', 60*60*24),
                         ('1 d', 60*60*24),
                         ('1 hour', 60*60),
                         ('1 h', 60*60),
                         ('1 minute', 60),
                         ('1 m', 60),
                         ('1 second', 1),
                         ('1 s', 1),
                         ('1 millisecond', 0.001),
                         ('1 ms', 0.001),
                         (-1, -1),
                         (-1.1, -1.1),
                         ('-1', -1),
                         ('-1s', -1),
                         ('-1 min 2 s', -62),
                         ('0.55555', 0.556),
                         (11.111111, 11.111),
                         ('0.1millis', 0),
                         ('0.5ms', 0.001),
                         (0, 0),
                         ('0', 0),
                         ('0day 0hour 0minute 0seconds 0millisecond', 0)]:
             assert_equal(timestr_to_secs(inp), exp, inp)

    def test_timestr_to_secs_invalid(self):
        for inv in ['', 'foo', '1sec 42 millis 3', '1min 2w', None]:
            assert_raises_with_msg(ValueError, "Invalid time string '%s'" % inv,
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

    def test_format_time(self):
        timetuple = (2005, 11, 2, 14, 23, 12, 123)
        for seps, exp in [(('-',' ',':'), '2005-11-02 14:23:12'),
                          (('', '-', ''), '20051102-142312'),
                          (('-',' ',':','.'), '2005-11-02 14:23:12.123')]:
            assert_equal(format_time(timetuple, *seps), exp)

    def test_get_timestamp(self):
        for seps, pattern in [((), '^\d{8} \d\d:\d\d:\d\d.\d\d\d$'),
                              (('',' ',':',None), '^\d{8} \d\d:\d\d:\d\d$'),
                              (('','','',None), '^\d{14}$'),
                              (('-','&nbsp;',':',';'),
                               '^\d{4}-\d\d-\d\d&nbsp;\d\d:\d\d:\d\d;\d\d\d$')]:
            ts = get_timestamp(*seps)
            assert_not_none(re.search(pattern, ts),
                            "'%s' didn't match '%s'" % (ts, pattern), False)

    def test_get_start_timestamp(self):
        start = get_start_timestamp(millissep='.')
        time.sleep(0.002)
        assert_equal(get_start_timestamp(millissep='.'), start)

    def test_timestamp_to_secs_with_default(self):
        assert_equal(timestamp_to_secs('20070920 16:15:14.123'), EXAMPLE_TIME+0.123)

    def test_timestamp_to_secs_with_seps(self):
        result = timestamp_to_secs('2007-09-20#16x15x14M123', ('-','#','x','M'))
        assert_equal(result, EXAMPLE_TIME+0.123)

    def test_timestamp_to_secs_with_millis(self):
        result = timestamp_to_secs('20070920 16:15:14.123')
        assert_equal(result, EXAMPLE_TIME+0.123)

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
            actual = get_elapsed_time(starttime, endtime)
            assert_equal(actual, expected, endtime)

    def test_parse_modified_time_with_valid_times(self):
        for input, expected in [('100', 100),
                                ('2007-09-20 16:15:14', EXAMPLE_TIME),
                                ('20070920 161514', EXAMPLE_TIME)]:
            assert_equal(parse_time(input), expected)

    def test_parse_modified_time_with_now(self):
        for input, adjusted in [('now', 0),
                                ('NOW', 0),
                                ('Now', 0),
                                ('now + 100 seconds', 100),
                                ('now - 100 seconds', -100),
                                ('now + 1 day 100 seconds', 86500),
                                ('now - 1 day 100 seconds', -86500),
                                ('now + 1 day 10 hours 1 minute 10 seconds',
                                 122470),
                                ('now - 1 day 10 hours 1 minute 10 seconds',
                                 -122470),
                                ('now +   100 seconds', 100)]:
            exp = get_time('epoch') + adjusted
            parsed = parse_time(input)
            assert_true(exp <= parsed <= exp +1,
                        "%d <= %d <= %d" % (exp, parsed, exp+1) )

    def test_parse_modified_time_with_invalid_times(self):
        for value, msg in [("-100", "Epoch time must be positive (got -100)"),
                           ("YYYY-MM-DD hh:mm:ss",
                            "Invalid time format 'YYYY-MM-DD hh:mm:ss'"),
                           ("now + foo", "Invalid time string 'foo'"),
                           ("now +    2a ", "Invalid time string '2a'")]:
            assert_raises_with_msg(ValueError, msg, parse_time, value)

    def test_parse_time_and_get_time_must_round_seconds_down(self):
        secs_before = int(time.time()) % 60
        get_time_result = get_time()[-2:]
        parse_time_result = parse_time('NOW') % 60
        secs_after = int(time.time()) % 60
        if secs_after == secs_before: # Check that second has not passed during the measurements
            assert_equal(get_time_result, '%02d' % secs_before)
            assert_equal(parse_time_result % 60, secs_after)

if __name__ == "__main__":
    unittest.main()
