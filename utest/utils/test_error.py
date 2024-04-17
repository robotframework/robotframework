import re
import sys
import traceback
import unittest

from robot.utils.asserts import assert_equal, assert_true, assert_raises
from robot.utils.error import get_error_details, get_error_message, ErrorDetails


def format_traceback(no_tb=False):
    e, v, tb = sys.exc_info()
    # This is needed when testing chaining and cause without traceback.
    # We set `err.__traceback__ = None` in tests and apparently that makes
    # `tb` here `None´ with Python 3.11 but not with others.
    if sys.version_info < (3, 11) and no_tb:
        tb = None
    return ''.join(traceback.format_exception(e, v, tb)).rstrip()


def format_message():
    return ''.join(traceback.format_exception_only(*sys.exc_info()[:2])).rstrip()


class TestGetErrorDetails(unittest.TestCase):

    def test_get_error_details(self):
        for exception, args, exp_msg in [
                    (AssertionError, ['My Error'], 'My Error'),
                    (AssertionError, [None], 'None'),
                    (AssertionError, [], 'AssertionError'),
                    (Exception, ['Another Error'], 'Another Error'),
                    (ValueError, ['Something'], 'ValueError: Something'),
                    (AssertionError, ['Msg\nin 3\nlines'], 'Msg\nin 3\nlines'),
                    (ValueError, ['2\nlines'], 'ValueError: 2\nlines')]:
            try:
                raise exception(*args)
            except:
                error1 = ErrorDetails()
                error2 = ErrorDetails(full_traceback=False)
                message1, tb1 = get_error_details()
                message2, tb2 = get_error_details(full_traceback=False)
                message3 = get_error_message()
                python_msg = format_message()
                python_tb = format_traceback()
            for msg in message1, message2, message3, error1.message, error2.message:
                assert_equal(msg, exp_msg)
            assert_true(tb1.startswith('Traceback (most recent call last):'))
            assert_true(tb1.endswith(exp_msg))
            assert_true(tb2.startswith('Traceback (most recent call last):'))
            assert_true(exp_msg not in tb2)
            assert_equal(tb1, error1.traceback)
            assert_equal(tb2, error2.traceback)
            assert_equal(tb1, python_tb)
            assert_equal(tb1, f'{tb2}\n{python_msg}')

    def test_chaining(self):
        try:
            1/0
        except Exception:
            try:
                raise ValueError
            except Exception:
                try:
                    raise RuntimeError('last error')
                except Exception as err:
                    assert_equal(ErrorDetails(err).traceback, format_traceback())

    def test_chaining_without_traceback(self):
        try:
            try:
                raise ValueError('lower')
            except ValueError as err:
                raise RuntimeError('higher') from err
        except Exception as err:
            err.__traceback__ = None
            assert_equal(ErrorDetails(err).traceback, format_traceback(no_tb=True))

    def test_cause(self):
        try:
            raise ValueError('err') from TypeError('cause')
        except ValueError as err:
            assert_equal(ErrorDetails(err).traceback, format_traceback())

    def test_cause_without_traceback(self):
        try:
            raise ValueError('err') from TypeError('cause')
        except ValueError as err:
            err.__traceback__ = None
            assert_equal(ErrorDetails(err).traceback, format_traceback(no_tb=True))


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
        except Exception as error:
            # first tb entry originates from this file and must be excluded
            error.__traceback__ = error.__traceback__.tb_next
            tb = ErrorDetails(error).traceback
        else:
            raise AssertionError
        # Remove lines indicating error location with `^^^^` used by Python 3.11+ and `~~~~^` variants in Python 3.13+.
        tb = '\n'.join(line for line in tb.splitlines() if line.strip('^~ '))
        if not re.match(expected, tb):
            raise AssertionError('\nExpected:\n%s\n\nActual:\n%s' % (expected, tb))


if __name__ == "__main__":
    unittest.main()
