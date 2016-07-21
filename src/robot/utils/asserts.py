#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Convenience functions for testing both in unit and higher levels.

Benefits:
  - Integrates 100% with unittest (see example below)
  - Can be easily used without unittest (using unittest.TestCase when you
    only need convenient asserts is not so nice)
  - Saved typing and shorter lines because no need to have 'self.' before
    asserts. These are static functions after all so that is OK.
  - All 'equals' methods (by default) report given values even if optional
    message given. This behavior can be controlled with the optional values
    argument.

Drawbacks:
  - unittest is not able to filter as much non-interesting traceback away
    as with its own methods because AssertionErrors occur outside.

Most of the functions are copied more or less directly from unittest.TestCase
which comes with the following license. Further information about unittest in
general can be found from http://pyunit.sourceforge.net/. This module can be
used freely in same terms as unittest.

unittest license::

    Copyright (c) 1999-2003 Steve Purcell
    This module is free software, and you may redistribute it and/or modify
    it under the same terms as Python itself, so long as this copyright message
    and disclaimer are retained in their original form.

    IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
    SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
    THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
    DAMAGE.

    THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
    PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
    AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
    SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

Examples::

    import unittest
    from robot.utils.asserts import assert_equal

    class MyTests(unittest.TestCase):

        def test_old_style(self):
            self.assertEqual(1, 2, 'my msg')

        def test_new_style(self):
            assert_equal(1, 2, 'my msg')

Example output::

    FF
    ======================================================================
    FAIL: test_old_style (example.MyTests)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "example.py", line 7, in test_old_style
        self.assertEqual(1, 2, 'my msg')
    AssertionError: my msg

    ======================================================================
    FAIL: test_new_style (example.MyTests)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "example.py", line 10, in test_new_style
        assert_equal(1, 2, 'my msg')
      File "/path/to/robot/utils/asserts.py", line 181, in assert_equal
        _report_inequality_failure(first, second, msg, values, '!=')
      File "/path/to/robot/utils/asserts.py", line 229, in _report_inequality_failure
        raise AssertionError(msg)
    AssertionError: my msg: 1 != 2

    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    FAILED (failures=2)
"""

from .robottypes import type_name
from .unic import unic


def fail(msg=None):
    """Fail test immediately with the given message."""
    _report_failure(msg)


def assert_false(expr, msg=None):
    """Fail the test if the expression is True."""
    if expr:
        _report_failure(msg)


def assert_true(expr, msg=None):
    """Fail the test unless the expression is True."""
    if not expr:
        _report_failure(msg)


def assert_not_none(obj, msg=None, values=True):
    """Fail the test if given object is None."""
    _msg = 'is None'
    if obj is None:
        if msg is None:
            msg = _msg
        elif values is True:
            msg = '%s: %s' % (msg, _msg)
        _report_failure(msg)


def assert_none(obj, msg=None, values=True):
    """Fail the test if given object is not None."""
    _msg = '%r is not None' % obj
    if obj is not None:
        if msg is None:
            msg = _msg
        elif values is True:
            msg = '%s: %s' % (msg, _msg)
        _report_failure(msg)


def assert_raises(exc_class, callable_obj, *args, **kwargs):
    """Fail unless an exception of class exc_class is thrown by callable_obj.

    callable_obj is invoked with arguments args and keyword arguments
    kwargs. If a different type of exception is thrown, it will not be
    caught, and the test case will be deemed to have suffered an
    error, exactly as for an unexpected exception.

    If a correct exception is raised, the exception instance is returned
    by this method.
    """
    try:
        callable_obj(*args, **kwargs)
    except exc_class as err:
        return err
    else:
        if hasattr(exc_class,'__name__'):
            exc_name = exc_class.__name__
        else:
            exc_name = str(exc_class)
        _report_failure('%s not raised' % exc_name)


def assert_raises_with_msg(exc_class, expected_msg, callable_obj, *args,
                           **kwargs):
    """Similar to fail_unless_raises but also checks the exception message."""
    try:
        callable_obj(*args, **kwargs)
    except exc_class as err:
        assert_equal(expected_msg, unic(err),
                     'Correct exception but wrong message')
    else:
        if hasattr(exc_class,'__name__'):
            exc_name = exc_class.__name__
        else:
            exc_name = str(exc_class)
        _report_failure('%s not raised' % exc_name)


def assert_equal(first, second, msg=None, values=True):
    """Fail if given objects are unequal as determined by the '==' operator."""
    if not first == second:
        _report_inequality_failure(first, second, msg, values, '!=')


def assert_not_equal(first, second, msg=None, values=True):
    """Fail if given objects are equal as determined by the '==' operator."""
    if first == second:
        _report_inequality_failure(first, second, msg, values, '==')


def assert_almost_equal(first, second, places=7, msg=None, values=True):
    """Fail if the two objects are unequal after rounded to given places.

    inequality is determined by object's difference rounded to the
    given number of decimal places (default 7) and comparing to zero.
    Note that decimal places (from zero) are usually not the same as
    significant digits (measured from the most signficant digit).
    """
    if round(second - first, places) != 0:
        extra = 'within %r places' % places
        _report_inequality_failure(first, second, msg, values, '!=', extra)


def assert_not_almost_equal(first, second, places=7, msg=None, values=True):
    """Fail if the two objects are unequal after rounded to given places.

    Equality is determined by object's difference rounded to to the
    given number of decimal places (default 7) and comparing to zero.
    Note that decimal places (from zero) are usually not the same as
    significant digits (measured from the most significant digit).
    """
    if round(second-first, places) == 0:
        extra = 'within %r places' % places
        _report_inequality_failure(first, second, msg, values, '==', extra)


def _report_failure(msg):
    if msg is None:
        raise AssertionError()
    raise AssertionError(msg)


def _report_inequality_failure(obj1, obj2, msg, values, delim, extra=None):
    if not msg:
        msg = _get_default_message(obj1, obj2, delim)
    elif values:
        msg = '%s: %s' % (msg, _get_default_message(obj1, obj2, delim))
    if values and extra:
        msg += ' ' + extra
    raise AssertionError(msg)


def _get_default_message(obj1, obj2, delim):
    str1 = unic(obj1)
    str2 = unic(obj2)
    if delim == '!=' and str1 == str2:
        return '%s (%s) != %s (%s)' % (str1, type_name(obj1),
                                       str2, type_name(obj2))
    return '%s %s %s' % (str1, delim, str2)
