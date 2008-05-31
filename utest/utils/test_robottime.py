import unittest
import sys
import re
import time
from types import *

from robot.utils.asserts import *
from robot.errors import *

from robot.utils.robottime import *

    
class TestTime(unittest.TestCase):
    
    def test_timestr_to_secs(self):
        for inp, exp in [ ('1', 1),
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
                          ('0day 0hour 0minute 0seconds 0millisecond', 0)
                         ]:
             
             assert_equals(timestr_to_secs(inp), exp, inp)
    
    def test_timestr_to_secs_invalid(self):
        for inv in ['', 'foo', '1sec 42 millis 3', '1min 2w']:  
            assert_raises_with_msg(DataError, "Invalid time string '%s'" % inv,
                                   timestr_to_secs, inv)
     
    def test_secs_to_timestr(self):
        for inp, compact, verbose in [ (0.001, '1ms', '1 millisecond'),
                                       (0.002, '2ms', '2 milliseconds'),
                                       (1, '1s', '1 second'),
                                       (2, '2s', '2 seconds'),
                                       (60, '1min', '1 minute'),
                                       (120, '2min', '2 minutes'),
                                       (3600, '1h', '1 hour'),
                                       (7200, '2h', '2 hours'),
                                       (60*60*24, '1d', '1 day'),
                                       (60*60*48, '2d', '2 days'),
                                       (171967.667, '1d 23h 46min 7s 667ms', 
                                        '1 day 23 hours 46 minutes 7 seconds 667 milliseconds' ),
                                       (7320, '2h 2min', '2 hours 2 minutes'),
                                       (7210.05, '2h 10s 50ms', 
                                        '2 hours 10 seconds 50 milliseconds') ,
                                       (11.1111111, '11s 111ms', 
                                        '11 seconds 111 milliseconds'),
                                       (0.55555555, '556ms', '556 milliseconds'),
                                       (0, '0s', '0 seconds') ,
                                       (-1, '- 1s', '- 1 second'),
                                       (-171967.667, '- 1d 23h 46min 7s 667ms', 
                                        '- 1 day 23 hours 46 minutes 7 seconds 667 milliseconds' ),
                                   ]:
            assert_equals(secs_to_timestr(inp), verbose)
            assert_equals(secs_to_timestr(inp, compact=True), compact)


            
    def test_format_time(self):
        tt = (2005, 11, 2, 14, 23, 12, 123)   # timetuple
        for seps, exp in [ ( ('-',' ',':'), '2005-11-02 14:23:12'),
                           ( ('', '-', ''), '20051102-142312'),
                           ( ('-',' ',':','.'),  '2005-11-02 14:23:12.123') ]:
            assert_equals(format_time(tt, *seps), exp)
        
    def test_get_timestamp(self):
        for seps, pattern in [
                ( (), '^\d{8} \d\d:\d\d:\d\d.\d\d\d$' ),
                ( ('',' ',':',None), '^\d{8} \d\d:\d\d:\d\d$' ),
                ( ('','','',None), '^\d{14}$' ), 
                ( ('-','&nbsp;',':',';'), 
                  '^\d{4}-\d\d-\d\d&nbsp;\d\d:\d\d:\d\d;\d\d\d$' ) ]:
            ts = get_timestamp(*seps)
            assert_not_none(re.search(pattern, ts),
                            "'%s' didn't match '%s'" % (ts, pattern), False)
    
    def test_get_start_timestamp(self):
        start = get_start_timestamp(millissep='.')
        time.sleep(0.002)
        assert_equals(get_start_timestamp(millissep='.'), start)
        
    def test_timestamp_to_secs_with_default(self):
        assert_equals(timestamp_to_secs('20070920 16:15:14.123'), 1190294114)

    def test_timestamp_to_secs_with_seps(self):
        result = timestamp_to_secs('2007-09-20#16x15x14M123', ('-','#','x','M'))
        assert_equals(result, 1190294114)
        
    def test_timestamp_to_secs_with_millis(self):
        result = timestamp_to_secs('20070920 16:15:14.123', millis=True)
        assert_equals(result, 1190294114.123)
        
    def test_get_elapsed_time_without_millis(self):
        starttime = '20060526 14:01:10'
        seps = ('', ' ', ':', None)
        for endtime, expected in [ ('20060526 14:01:10', '00:00:00'),
                                   ('20060526 14:01:11', '00:00:01'),
                                   ('20060526 14:01:21', '00:00:11'),
                                   ('20060526 14:02:09', '00:00:59'),
                                   ('20060526 14:02:10', '00:01:00'),
                                   ('20060526 14:02:11', '00:01:01'), 
                                   ('20060526 14:27:42', '00:26:32'), 
                                   ('20060526 15:01:09', '00:59:59'), 
                                   ('20060526 15:01:10', '01:00:00'), 
                                   ('20060526 15:01:11', '01:00:01'), 
                                   ('20060526 23:59:59', '09:58:49'), 
                                   ('20060527 00:00:00', '09:58:50'), 
                                   ('20060527 00:00:01', '09:58:51'), 
                                   ('20060527 00:01:10', '10:00:00'), 
                                   ('20060527 14:01:10', '24:00:00'), 
                                   ('20060530 18:01:09', '99:59:59'), 
                                   ('20060530 18:01:10', '100:00:00'), 
                                   ('20060530 18:01:11', '100:00:01'),
                                   ('20060601 14:01:09', '143:59:59'),                           
                                   ('20060601 14:01:10', '144:00:00'), 
                                   ('20060601 14:01:11', '144:00:01'),
                                   ('20070526 14:01:09', '8759:59:59'),
                                   ('20070526 14:01:10', '8760:00:00') ]:
            actual = get_elapsed_time(starttime, endtime, seps)
            assert_equals(actual, expected+'.000', endtime)

    def test_get_elapsed_time_with_millis(self):
        starttime = '20060526 14:01:10.500'
        seps = ('', ' ', ':', '.')
        for endtime, expected in [ ('20060526 14:01:10.500', '00:00:00.000'),
                                   ('20060526 14:01:10.5',   '00:00:00.000'),
                                   ('20060526 14:01:10.5000','00:00:00.000'),                                  
                                   ('20060526 14:01:10.501', '00:00:00.001'),
                                   ('20060526 14:01:10.777', '00:00:00.277'),
                                   ('20060526 14:01:11.000', '00:00:00.500'),
                                   ('20060526 14:01:11.321', '00:00:00.821'),                                  
                                   ('20060526 14:01:11.499', '00:00:00.999'),
                                   ('20060526 14:01:11.500', '00:00:01.000'),                                  
                                   ('20060526 14:01:11.501', '00:00:01.001'),
                                   ('20060526 14:01:11',     '00:00:00.500'),
                                   ('20060526 14:01:11.5',   '00:00:01.000'),
                                   ('20060526 14:01:11.51',  '00:00:01.010'),
                                   ('20060526 14:01:11.5123','00:00:01.012'),      
                                   ('20060601 14:01:10.499', '143:59:59.999'),                           
                                   ('20060601 14:01:10.500', '144:00:00.000'), 
                                   ('20060601 14:01:10.501', '144:00:00.001'),
                                   ('20070526 14:01:10.499', '8759:59:59.999'),
                                   ('20070526 14:01:10.500', '8760:00:00.000') ]:
            actual = get_elapsed_time(starttime, endtime, seps)
            assert_equals(actual, expected, endtime)

    def test_get_elapsed_time_negatime_without_millis(self):
        starttime = '20060526 14:01:10'
        seps = ('', ' ', ':', None)
        for endtime, expected in [ ('20060526 14:01:09', '-00:00:01'),
                                   ('20060526 14:00:11', '-00:00:59'),
                                   ('20060526 14:00:10', '-00:01:00'),
                                   ('20060526 14:00:09', '-00:01:01'),
                                   ('20060521 14:01:11', '-119:59:59'),         
                                   ('20060521 14:01:10', '-120:00:00'),                                  
                                   ('20060521 14:01:09', '-120:00:01') ]:
            actual = get_elapsed_time(starttime, endtime, seps)
            assert_equals(actual, expected+'.000', endtime)

    def test_get_elapsed_time_negatime_with_millis(self):
        starttime = '20060526 14:01:10.500'
        seps = ('', ' ', ':', '.')
        for endtime, expected in [ ('20060526 14:01:10.499', '-00:00:00.001'),
                                   ('20060526 14:01:10',     '-00:00:00.500'),
                                   ('20060526 14:01:09.9',   '-00:00:00.600'),
                                   ('20060526 14:01:09.501', '-00:00:00.999'),
                                   ('20060526 14:01:09.500', '-00:00:01.000'),
                                   ('20060526 14:01:09.499', '-00:00:01.001') ]:
            actual = get_elapsed_time(starttime, endtime, seps)
            assert_equals(actual, expected, endtime)

    def test_get_elapsed_millis(self):
        starttime = '20060526 14:01:10.500'
        seps = ('', ' ', ':', '.')
        for endtime, expected in [ ('20060526 13:59:30.500', -100000),
                                   ('20060526 14:00:10.500', -60000),
                                   ('20060526 14:01:09.250', -1250),
                                   ('20060526 14:01:09.499', -1001),                                  
                                   ('20060526 14:01:09.500', -1000),
                                   ('20060526 14:01:09.501', -999),
                                   ('20060526 14:01:09.750', -750),
                                   ('20060526 14:01:10',     -500),
                                   ('20060526 14:01:10.250', -250),
                                   ('20060526 14:01:10.499', -1), 
                                   ('20060526 14:01:10.500', 0),                            
                                   ('20060526 14:01:10.501', 1),
                                   ('20060526 14:01:10.750', 250),
                                   ('20060526 14:01:11',     500),
                                   ('20060526 14:01:11.250', 750),
                                   ('20060526 14:01:11.499', 999),
                                   ('20060526 14:01:11.500', 1000),                                  
                                   ('20060526 14:01:11.501', 1001),
                                   ('20060526 14:01:11.750', 1250),
                                   ('20060526 14:01:40.500', 30000),
                                   ('20060526 14:02:10.500', 60000),
                                   ('20060526 14:02:10.501', 60001),
                                   ('20060526 14:02:50.500', 100000),
                                   ('20060526 15:01:10.500', 3600000), 
                                   ('20060530 18:01:10.500', 360000000) ]:
            actual = get_elapsed_millis(starttime, endtime, seps)
            assert_equals(actual, expected, endtime)
            assert_true(type(actual) in [IntType,LongType])

    def test_get_elapsed_time_separators(self):
        startday = endday = ('2006','05','26')
        starttime = ('14','01','10')
        endtime = ('15','01','09')
        startmillis = endmillis = '500'
        for d_sep, dt_sep, t_sep, m_sep in [ ('', ' ', ':', None),
                                             ('', ' ', '', None),
                                             ('-', 'T', ':', None),
                                             ('-', '-', '-', None),
                                             ('', '', '', None),   
                                             ('', ' ', ':', '.'),
                                             ('', ' ', '', '.'),  
                                             ('-', 'T', ':', '.'),
                                             ('-', '-', '-', '-'),
                                             ('', '', '', '') ]:
            start_stamp = d_sep.join(startday) + dt_sep + t_sep.join(starttime)
            end_stamp = d_sep.join(endday) + dt_sep + t_sep.join(endtime)
            expected = '00:59:59.000'
            if m_sep is not None:
                start_stamp += m_sep + startmillis
                end_stamp += m_sep + endmillis
            seps = (d_sep, dt_sep, t_sep, m_sep)
            actual = get_elapsed_time(start_stamp, end_stamp, seps)
            assert_equals(actual, expected)

    def test_get_elapsed_time_without_end_timestamp(self):
        seps = ('-', ' ', ':', '.')
        elapsed_string = get_elapsed_time(get_timestamp(*seps), seps=seps)
        elapsed_millis = get_elapsed_millis(get_timestamp(*seps), seps=seps)
        assert_true(elapsed_string.startswith('00:00:00.0'), elapsed_string)
        assert_true(elapsed_millis < 100, elapsed_millis)

    def test_elapsed_string_to_millis_to_string(self):
        for string, millis in [ ('00:00:00.000', 0),
                                ('00:00:00.001', 1),
                                ('00:00:00.003', 3),
                                ('00:00:00.999', 999),                               
                                ('00:00:01.000', 1000),
                                ('00:00:01.234', 1234),
                                ('00:00:10.101', 10101),
                                ('00:00:59.999', 59999),
                                ('00:01:00.000', 60000),
                                ('00:01:01.001', 61001),
                                ('00:10:20.300', 620300),
                                ('00:59:59.999', 3599999),
                                ('01:00:00.000', 3600000),
                                ('01:00:00.001', 3600001),
                                ('01:02:03.004', 3723004),
                                ('10:00:00.000', 36000000),
                                ('12:34:56.789', 45296789),
                                ('99:59:59.999', 359999999),
                                ('100:00:00.000', 360000000),
                                ('999:59:59.999', 3599999999),
                                ('1000:00:00.000', 3600000000),
                                ('1000:10:10.100', 3600610100),
                                ('-00:00:00.000', 0),
                                ('-00:00:00.001', -1),
                                ('-999:59:59.999', -3599999999),
                    ]:
            actual = elapsed_string_to_millis(string)
            assert_equals(actual, millis)
            assert_true(type(actual) in [IntType,LongType])
            if millis == 0: string = '00:00:00.000'
            assert_equals(elapsed_millis_to_string(millis), string)
            assert_equals(elapsed_millis_to_string(millis+0.123), string)
        

class TestDiffToGMT(unittest.TestCase):
    
    def test_positive_gmt(self):
        assert_equals(get_diff_to_gmt(9000), "GMT -02:30")

    def test_negative_gmt(self):
        assert_equals(get_diff_to_gmt(-7200), "GMT +02:00")

    def test_zero_gmt(self):
        assert_equals(get_diff_to_gmt(0), "GMT +00:00")

    def test_big_positive_gmt(self):
        assert_equals(get_diff_to_gmt(40500), "GMT -11:15")

    def test_big_negative_gmt(self):
        assert_equals(get_diff_to_gmt(-38700), "GMT +10:45")


if __name__ == "__main__":
    unittest.main()
