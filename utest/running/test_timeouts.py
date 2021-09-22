import unittest
import sys
import time
import os

from robot.errors import TimeoutError
from robot.running.timeouts import TestTimeout, KeywordTimeout
from robot.utils.asserts import (assert_equal, assert_false, assert_true,
                                 assert_raises, assert_raises_with_msg)

# thread_resources is here
sys.path.append(os.path.join(os.path.dirname(__file__),'..','utils'))
from thread_resources import passing, failing, sleeping, returning, MyException


class VariableMock(object):

    def replace_string(self, string):
        return string


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
        for inv in ['invalid', '1s 1']:
            err = "Setting test timeout failed: Invalid time string '%s'."
            self._verify_tout(TestTimeout(inv), str=inv, secs=0.000001, err=err % inv)

    def _verify_tout(self, tout, str='', secs=-1, err=None):
        tout.replace_variables(VariableMock())
        assert_equal(tout.string, str)
        assert_equal(tout.secs, secs)
        assert_equal(tout.error, err)


class TestTimer(unittest.TestCase):

    def test_time_left(self):
        tout = TestTimeout('1s', variables=VariableMock())
        tout.start()
        assert_true(tout.time_left() > 0.9)
        time.sleep(0.2)
        assert_true(tout.time_left() < 0.9)

    def test_timed_out_with_no_timeout(self):
        tout = TestTimeout(variables=VariableMock())
        tout.start()
        time.sleep(0.01)
        assert_false(tout.timed_out())

    def test_timed_out_with_non_exceeded_timeout(self):
        tout = TestTimeout('10s', variables=VariableMock())
        tout.start()
        time.sleep(0.01)
        assert_false(tout.timed_out())

    def test_timed_out_with_exceeded_timeout(self):
        tout = TestTimeout('1ms', variables=VariableMock())
        tout.start()
        time.sleep(0.02)
        assert_true(tout.timed_out())


class TestComparisons(unittest.TestCase):

    def test_compare_when_none_timeouted(self):
        touts = self._create_timeouts([''] * 10)
        assert_equal(min(touts).string, '')
        assert_equal(max(touts).string, '')

    def test_compare_when_all_timeouted(self):
        touts = self._create_timeouts(['1min','42seconds','43','1h1min','99'])
        assert_equal(min(touts).string, '42 seconds')
        assert_equal(max(touts).string, '1 hour 1 minute')

    def test_compare_with_timeouted_and_non_timeouted(self):
        touts = self._create_timeouts(['','1min','42sec','','43','1h1m','99',''])
        assert_equal(min(touts).string, '42 seconds')
        assert_equal(max(touts).string, '')

    def test_that_compare_uses_starttime(self):
        touts = self._create_timeouts(['1min','42seconds','43','1h1min','99'])
        touts[2].starttime -= 2
        assert_equal(min(touts).string, '43 seconds')
        assert_equal(max(touts).string, '1 hour 1 minute')

    def _create_timeouts(self, tout_strs):
        touts = []
        for tout_str in tout_strs:
            touts.append(TestTimeout(tout_str, variables=VariableMock()))
            touts[-1].start()
        return touts


class TestRun(unittest.TestCase):

    def setUp(self):
        self.tout = TestTimeout('1s', variables=VariableMock())
        self.tout.start()

    def test_passing(self):
        assert_equal(self.tout.run(passing), None)

    def test_returning(self):
        for arg in [10, 'hello', ['l','i','s','t'], unittest]:
            ret = self.tout.run(returning, args=(arg,))
            assert_equal(ret, arg)

    def test_failing(self):
        assert_raises_with_msg(MyException, 'hello world',
                               self.tout.run, failing, ('hello world',))

    def test_sleeping(self):
        assert_equal(self.tout.run(sleeping, args=(0.01,)), 0.01)

    def test_method_executed_normally_if_no_timeout(self):
        os.environ['ROBOT_THREAD_TESTING'] = 'initial value'
        self.tout.run(sleeping, (0.05,))
        assert_equal(os.environ['ROBOT_THREAD_TESTING'], '0.05')

    def test_method_stopped_if_timeout(self):
        os.environ['ROBOT_THREAD_TESTING'] = 'initial value'
        self.tout.secs = 0.001
        # PyThreadState_SetAsyncExc thrown exceptions are not guaranteed
        # to occur in a specific timeframe ,, thus the actual Timeout exception
        # maybe thrown too late in Windows.
        # This is why we need to have an action that really will take some time (sleep 5 secs)
        # to (almost) ensure that the 'ROBOT_THREAD_TESTING' setting is not executed before
        # timeout exception occurs
        assert_raises_with_msg(TimeoutError, 'Test timeout 1 second exceeded.',
                               self.tout.run, sleeping, (5,))
        assert_equal(os.environ['ROBOT_THREAD_TESTING'], 'initial value')

    def test_zero_and_negative_timeout(self):
        for tout in [0, 0.0, -0.01, -1, -1000]:
            self.tout.time_left = lambda: tout
            assert_raises(TimeoutError, self.tout.run, sleeping, (10,))


class TestMessage(unittest.TestCase):

    def test_non_active(self):
        assert_equal(TestTimeout().get_message(), 'Test timeout not active.')

    def test_active(self):
        tout = KeywordTimeout('42s', variables=VariableMock())
        tout.start()
        msg = tout.get_message()
        assert_true(msg.startswith('Keyword timeout 42 seconds active.'), msg)
        assert_true(msg.endswith('seconds left.'), msg)

    def test_failed_default(self):
        tout = TestTimeout('1s', variables=VariableMock())
        tout.starttime = time.time() - 2
        assert_equal(tout.get_message(), 'Test timeout 1 second exceeded.')


if __name__ == '__main__':
    unittest.main()
