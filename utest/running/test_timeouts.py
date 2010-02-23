import unittest
import sys
import time
import os

from robot.utils.asserts import *
from robot.errors import *
from robot.running.timeouts import TestTimeout, KeywordTimeout

# thread_resources is here
sys.path.append(os.path.join(os.path.dirname(__file__),'..','utils'))

from thread_resources import passing, failing, sleeping, returning, MyException

if os.name == 'java':
    from java.lang import Error as JavaError
    from thread_resources import java_failing
    

class TestInit(unittest.TestCase):
    
    def test_no_params(self):
        self._verify_tout(TestTimeout())
        
    def test_timeout_string(self):
        for tout_str, exp_str, exp_secs in [ ('1s', '1 second', 1), 
                                             ('10 sec', '10 seconds', 10), 
                                             ('2h 1minute', '2 hours 1 minute', 7260),
                                             ('42', '42 seconds', 42) ]:
            self._verify_tout(TestTimeout(tout_str), exp_str, exp_secs)

    def test_invalid_timeout_string(self):
        for inv in [ 'invalid', '1s 1', '' ]:
            for params in [ [inv], [inv,'whatever'] ]:
                tout = TestTimeout(*params)
                err = "Setting test timeout failed: Invalid time string '%s'"
                self._verify_tout(tout, secs=0.000001, err=err % inv)

    def test_message(self):
        for msgcols in [ ['mymessage'], 
                         ['This is my message!'],
                         ['Message in','two colums'],
                         ['My','message','in','quite','many','columns','.'] ]:
            tout = TestTimeout('10sec', *msgcols)
            self._verify_tout(tout, str='10 seconds', secs=10, msg=' '.join(msgcols))

    def _verify_tout(self, tout, str='', secs=-1, msg=None, err=None):
        assert_equals(tout.string, str)
        assert_equals(tout.secs, secs)
        assert_equals(tout.message, msg)
        assert_equals(tout.error, err)

        
class TestTimer(unittest.TestCase):
      
    def test_time_left(self):
        tout = TestTimeout('1s')
        tout.start()
        assert_true(tout.time_left() > 0.9)
        time.sleep(0.2)
        assert_true(tout.time_left() < 0.9)
        
    def test_timed_out_with_no_timeout(self):
        tout = TestTimeout()
        tout.start()
        time.sleep(0.01)
        assert_false(tout.timed_out())
        
    def test_timed_out_with_non_exceeded_timeout(self):
        tout = TestTimeout('10s')
        tout.start()
        time.sleep(0.01)
        assert_false(tout.timed_out())
        
    def test_timed_out_with_exceeded_timeout(self):
        tout = TestTimeout('1ms')
        tout.start()
        time.sleep(0.02)
        assert_true(tout.timed_out())
        
        
class TestComparisons(unittest.TestCase):
    
    def test_compare_when_none_timeouted(self):
        touts = self._create_timeouts([''] * 10)
        assert_equals(min(touts).string, '')
        assert_equals(max(touts).string, '')

    def test_compare_when_all_timeouted(self):
        touts = self._create_timeouts(['1min','42seconds','43','1h1min','99'])
        assert_equals(min(touts).string, '42 seconds')
        assert_equals(max(touts).string, '1 hour 1 minute')
        
    def test_compare_with_timeouted_and_non_timeouted(self):
        touts = self._create_timeouts(['','1min','42sec','','43','1h1m','99',''])
        assert_equals(min(touts).string, '')
        assert_equals(max(touts).string, '1 hour 1 minute')
    
    def test_that_compare_uses_starttime(self):
        touts = self._create_timeouts(['1min','42seconds','43','1h1min','99'])
        touts[2].starttime -= 2
        assert_equals(min(touts).string, '43 seconds')
        assert_equals(max(touts).string, '1 hour 1 minute')
        
    def _create_timeouts(self, tout_strs):
        touts = []
        for tout_str in tout_strs:
            touts.append(TestTimeout(tout_str))
            touts[-1].start()
        return touts


class MockLogger:
    def __init__(self):
        self.msgs = []
    def debug(self, msg):
        self.msgs.append(('DEBUG',msg))
    def info(self, msg):
        self.msgs.append(('INFO',msg))


class TestRun(unittest.TestCase):
    
    def setUp(self):
        self.tout = TestTimeout('1s')
        self.tout.start()
        self.logger = MockLogger()
    
    def test_passing(self):
        assert_none(self.tout.run(passing, logger=self.logger))
        self._verify_debug_msg(self.logger.msgs[0])
        
    def test_returning(self):
        for arg in [ 10, 'hello', ['l','i','s','t'], unittest]:
            ret = self.tout.run(returning, args=(arg,), logger=self.logger)
            assert_equals(ret, arg)
            self._verify_debug_msg(self.logger.msgs[-1])

    def test_failing(self):
        try:
            self.tout.run(failing, args=('hello world',))
        except MyException, err:
            assert_equals(str(err), 'hello world')
        else:
            fail('run did not raise an exception as expected')

    if os.name == 'java':        
        def test_java_failing(self):
            try:
                self.tout.run(java_failing, args=('hi tellus',))
            except JavaError, err:
                assert_equals(err.getMessage(), 'hi tellus')
            else:
                fail('run did not raise an exception as expected')

    def test_sleeping(self):
        assert_equals(self.tout.run(sleeping, args=(0.01,)), 0.01)

    def test_method_executed_normally_if_no_timeout(self):
        os.environ['ROBOT_THREAD_TESTING'] = 'initial value'
        self.tout.run(sleeping, (0.05,), {}, self.logger)
        self._verify_debug_msg(self.logger.msgs[0])
        assert_equals(os.environ['ROBOT_THREAD_TESTING'], '0.05')

    def test_method_stopped_if_timeout(self):
        os.environ['ROBOT_THREAD_TESTING'] = 'initial value'
        self.tout.secs = 0.01
        assert_raises_with_msg(TimeoutError, 'Test timeout 1 second exceeded.',
                               self.tout.run, sleeping, (0.05,), {}, self.logger)
        self._verify_debug_msg(self.logger.msgs[0])
        time.sleep(0.1)
        assert_equals(os.environ['ROBOT_THREAD_TESTING'], 'initial value')

    def test_zero_and_negative_timeout(self):
        for tout in [ 0, 0.0, -0.01, -1, -1000 ]:
            self.tout.time_left = lambda : tout
            assert_raises(TimeoutError, self.tout.run, sleeping, (10,))
            
    def test_customized_message(self):
        for msgcols in [ ['mymessage'], ['My','message','in','5','cols'] ]:
            self.logger.msgs = []
            tout = KeywordTimeout('1s', *msgcols)
            tout.start()
            tout.run(passing, logger=self.logger)
            self._verify_debug_msg(self.logger.msgs[0], 'Keyword')
            tout.secs = 0.01
            assert_raises_with_msg(TimeoutError, ' '.join(msgcols),
                                   tout.run, sleeping, (1,), {}, self.logger)
            self._verify_debug_msg(self.logger.msgs[1], 'Keyword')

    def _verify_debug_msg(self, msg, type='Test'):
        assert_equals(msg[0], 'DEBUG')
        assert_true(msg[1].startswith('%s timeout 1 second active.' % type), msg[1])
        assert_true(msg[1].endswith('seconds left.'), msg[1])


if __name__ == '__main__':
    unittest.main()
