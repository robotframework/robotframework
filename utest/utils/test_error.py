import unittest
import sys
import re

from robot.utils.asserts import assert_equal, assert_true, assert_raises
from robot.utils.error import get_error_details, get_error_message, PythonErrorDetails


class TestGetErrorDetails(unittest.TestCase):

    def test_get_error_details_python(self):
        for exception, msg, exp_msg in [
                    (AssertionError, 'My Error', 'My Error'),
                    (AssertionError, None, 'None'),
                    (Exception, 'Another Error', 'Another Error'),
                    (ValueError, 'Something', 'ValueError: Something'),
                    (AssertionError, 'Msg\nin 3\nlines', 'Msg\nin 3\nlines'),
                    (ValueError, '2\nlines', 'ValueError: 2\nlines')]:
            try:
                raise exception(msg)
            except:
                message, details = get_error_details()
                assert_equal(message, get_error_message())
            assert_equal(message, exp_msg)
            assert_true(details.startswith('Traceback'))
            assert_true(exp_msg not in details)

    def test_get_error_details_python_class(self):
        for exception in [AssertionError, ValueError, ZeroDivisionError]:
            try:
                raise exception
            except:
                message, details = get_error_details()
                assert_equal(message, get_error_message())
            exp_msg = exception.__name__
            assert_equal(message, exception.__name__)
            assert_true(details.startswith('Traceback'))
            assert_true(exp_msg not in details)


class TestRemoveRobotEntriesFromTraceback(unittest.TestCase):

    def test_both_robot_and_non_robot_entries(self):
        def raises():
            raise Exception
        self._verify_traceback(r'''
Traceback \(most recent call last\):
  File ".*", line \d+, in raises
    raise Exception
'''.strip(), assert_raises, AssertionError, raises)

    def test_remove_entries_with_lambda_and_multiple_entries(self):
        def raises():
            1/0
        raising_lambda = lambda: raises()
        self._verify_traceback(r'''
Traceback \(most recent call last\):
  File ".*", line \d+, in <lambda.*>
    raising_lambda = lambda: raises\(\)
  File ".*", line \d+, in raises
    1/0
'''.strip(), assert_raises, AssertionError, raising_lambda)

    def test_only_robot_entries(self):
        self._verify_traceback(r'''
Traceback \(most recent call last\):
  None
'''.strip(), assert_equal, 1, 2)

    def _verify_traceback(self, expected, method, *args):
        try:
            method(*args)
        except Exception:
            type, value, tb = sys.exc_info()
            # first tb entry originates from this file and must be excluded
            traceback = PythonErrorDetails(type, value, tb.tb_next).traceback
        else:
            raise AssertionError
        if not re.match(expected, traceback):
            raise AssertionError('\nExpected:\n%s\n\nActual:\n%s' % (expected, traceback))


if __name__ == "__main__":
    unittest.main()
