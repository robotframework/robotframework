import os
import time
import unittest

from thread_resources import failing, MyException, passing, returning, sleeping

from robot.errors import DataError, TimeoutExceeded
from robot.running.timeouts import KeywordTimeout, TestTimeout
from robot.utils.asserts import (
    assert_equal, assert_false, assert_raises, assert_raises_with_msg, assert_true
)
from robot.variables import Variables


class TestInit(unittest.TestCase):

    def test_no_params(self):
        self._verify(TestTimeout(), "NONE")

    def test_timeout_string(self):
        for tout_str, exp_str, exp_secs in [
            ("1s", "1 second", 1),
            ("10 sec", "10 seconds", 10),
            ("2h 1minute", "2 hours 1 minute", 7260),
            ("42", "42 seconds", 42),
        ]:
            self._verify(TestTimeout(tout_str), exp_str, exp_secs)

    def test_invalid_timeout_string(self):
        for inv in ["invalid", "1s 1"]:
            error = f"Setting test timeout failed: Invalid time string '{inv}'."
            self._verify(TestTimeout(inv), inv, error=error)

    def test_variables(self):
        variables = Variables()
        variables["${timeout}"] = "42"
        self._verify(TestTimeout("${timeout} s", variables), "42 seconds", 42)
        error = "Setting test timeout failed: Variable '${bad}' not found."
        self._verify(TestTimeout("${bad} s", variables), "${bad} s", error=error)

    def _verify(self, obj, string, timeout=None, error=None):
        assert_equal(obj.string, string)
        assert_equal(obj.timeout, timeout if not error else 0.000001)
        assert_equal(obj.error, error)


class TestTimer(unittest.TestCase):

    def test_time_left(self):
        tout = TestTimeout("1s", start=True)
        assert_true(tout.time_left() > 0.9)
        time.sleep(0.1)
        assert_true(tout.time_left() <= 0.9)
        assert_false(tout.timed_out())

    def test_exceeded(self):
        tout = TestTimeout("1ms", start=True)
        time.sleep(0.02)
        assert_true(tout.time_left() < 0)
        assert_true(tout.timed_out())

    def test_not_started(self):
        assert_raises_with_msg(
            ValueError,
            "Timeout is not started.",
            TestTimeout(1).time_left,
        )

    def test_cannot_start_inactive_timeout(self):
        assert_raises_with_msg(
            ValueError,
            "Cannot start inactive timeout.",
            TestTimeout().start,
        )
        assert_raises_with_msg(
            ValueError,
            "Cannot start inactive timeout.",
            TestTimeout,
            start=True,
        )


class TestComparison(unittest.TestCase):

    def setUp(self):
        self.timeouts = []
        for string in ["1 min", "42 s", "45", "1 h 1 min", "99"]:
            self.timeouts.append(TestTimeout(string, start=True))

    def test_compare(self):
        assert_equal(min(self.timeouts).string, "42 seconds")
        assert_equal(max(self.timeouts).string, "1 hour 1 minute")

    def test_compare_uses_start_time(self):
        self.timeouts[2].start_time -= 10
        self.timeouts[3].start_time -= 3600
        assert_equal(min(self.timeouts).string, "45 seconds")
        assert_equal(max(self.timeouts).string, "1 minute 39 seconds")

    def test_cannot_compare_inactive(self):
        self.timeouts.append(TestTimeout())
        assert_raises_with_msg(
            ValueError,
            "Cannot compare inactive timeout.",
            min,
            self.timeouts,
        )


class TestRun(unittest.TestCase):

    def setUp(self):
        self.timeout = TestTimeout("1s", start=True)

    def test_passing(self):
        assert_equal(self.timeout.run(passing), None)

    def test_returning(self):
        for arg in [10, "hello", ["l", "i", "s", "t"], unittest]:
            ret = self.timeout.run(returning, args=(arg,))
            assert_equal(ret, arg)

    def test_failing(self):
        assert_raises_with_msg(
            MyException,
            "hello world",
            self.timeout.run,
            failing,
            ("hello world",),
        )

    def test_timeout_not_exceeded(self):
        os.environ["ROBOT_THREAD_TESTING"] = "initial value"
        assert_equal(self.timeout.run(sleeping, [0.05]), 0.05)
        assert_equal(os.environ["ROBOT_THREAD_TESTING"], "0.05")

    def test_timeout_exceeded(self):
        os.environ["ROBOT_THREAD_TESTING"] = "initial value"
        assert_raises_with_msg(
            TimeoutExceeded,
            "Test timeout 10 milliseconds exceeded.",
            TestTimeout(0.01, start=True).run,
            sleeping,
        )
        assert_equal(os.environ["ROBOT_THREAD_TESTING"], "initial value")

    def test_zero_and_negative_timeout(self):
        for tout in [0, 0.0, -0.01, -1, -1000]:
            self.timeout.time_left = lambda: tout
            assert_raises(TimeoutExceeded, self.timeout.run, sleeping)

    def test_pause_runner(self):
        runner = TestTimeout(0.01, start=True).get_runner()
        runner.pause()
        runner.run(sleeping, [0.05])  # No timeout because runner is paused.
        assert_raises_with_msg(
            TimeoutExceeded,
            "Test timeout 10 milliseconds exceeded.",
            runner.resume,  # Timeout is raised on resume.
        )

    def test_pause_nested(self):
        runner = TestTimeout(0.01, start=True).get_runner()
        for i in range(7):
            runner.pause()
        runner.resume()
        runner.run(sleeping, [0.05])
        for i in range(5):
            runner.resume()  # Not fully resumed so still no timeout.
        assert_raises_with_msg(
            TimeoutExceeded,
            "Test timeout 10 milliseconds exceeded.",
            runner.resume,  # Timeout is raised when fully resumed.
        )

    def test_timeout_close_to_function_end(self):
        delay = 0.05
        while delay < 0.15:
            try:
                result = TestTimeout(0.1, start=True).run(sleeping, [delay])
            except TimeoutExceeded as err:
                assert_equal(str(err), "Test timeout 100 milliseconds exceeded.")
            else:
                assert_equal(result, delay)
            delay += 0.02

    def test_no_support(self):
        from robot.running.timeouts.nosupport import NoSupportRunner
        from robot.running.timeouts.runner import Runner

        orig_runner = Runner.runner_implementation
        Runner.runner_implementation = NoSupportRunner
        try:
            assert_raises_with_msg(
                DataError,
                "Timeouts are not supported on this platform.",
                self.timeout.run,
                passing,
            )
        finally:
            Runner.runner_implementation = orig_runner


class TestMessage(unittest.TestCase):

    def test_non_active(self):
        assert_equal(TestTimeout().get_message(), "Test timeout not active.")

    def test_active(self):
        msg = KeywordTimeout("42s", start=True).get_message()
        assert_true(msg.startswith("Keyword timeout 42 seconds active."), msg)
        assert_true(msg.endswith("seconds left."), msg)

    def test_failed_default(self):
        tout = TestTimeout("1s")
        tout.start_time = time.time() - 2
        assert_equal(tout.get_message(), "Test timeout 1 second exceeded.")


if __name__ == "__main__":
    unittest.main()
