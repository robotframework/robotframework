#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

import os
import re
import time

from robot.output import LOGGER, OUTPUT, Message
from robot.errors import DataError, ExecutionFailed, ExecutionFailures
from robot import utils
from robot.utils import asserts
from robot.variables import is_var, is_list_var
from robot.running import Keyword, NAMESPACES, RUN_KW_REGISTER
from robot.running.model import ExecutionContext
from robot.version import get_version

if utils.is_jython:
    from java.lang import String, Number, Long, Double


class _Converter:

    def convert_to_integer(self, item):
        """Converts the given item to an integer number."""
        try:
            if utils.is_jython:
                return self._jython_to_integer(item)
            return int(item)
        except:
            raise RuntimeError("'%s' cannot be converted to an integer: %s"
                            % (item, utils.get_error_message()))

    def _jython_to_integer(self, item):
        # This helper handles Java Strings and Numbers as well as Jython
        # not handling overflow automatically
        try:
            return int(item)
        except ValueError:
            return long(item)
        except TypeError:
            if isinstance(item, String):
                return Long.parseLong(item)
            if isinstance(item, Number):
                return item.longValue()
            raise

    def convert_to_number(self, item):
        """Converts the given item to a floating point number."""
        try:
            if utils.is_jython:
                return self._jython_to_number(item)
            return float(item)
        except:
            error = utils.get_error_message()
            try:
                return float(self.convert_to_integer(item))
            except RuntimeError:
                raise RuntimeError("'%s' cannot be converted to a floating point "
                                 "number: %s" % (item, error))

    def _jython_to_number(self, item):
        # This helper handles Java Strings and Numbers
        try:
            return float(item)
        except (TypeError, AttributeError):
            if isinstance(item, String):
                return Double.parseDouble(item)
            if isinstance(item, Number):
                return item.doubleValue()
            raise

    def convert_to_string(self, item):
        """Converts the given item to a Unicode string.

        Uses '__unicode__' or '__str__' method with Python objects and
        'toString' with Java objects.
        """
        return utils.unic(item)

    def convert_to_boolean(self, item):
        """Converts the given item to Boolean true or false.

        Handles strings 'True' and 'False' (case-insensitive) as expected,
        otherwise returns item's truth value using Python's 'bool' method.
        For more information about truth values, see
        http://docs.python.org/lib/truth.html.
        """
        if isinstance(item, basestring):
            if utils.eq(item, 'True'):
                return True
            if utils.eq(item, 'False'):
                return False
        return bool(item)

    def create_list(self, *items):
        """Returns a list containing given items.

        The returned list can be assigned both to ${scalar} and @{list}
        variables. The earlier can be used e.g. with Java keywords expecting
        an array as an argument.

        Examples:
        | @{list} =   | Create List | a    | b    | c    |
        | ${scalar} = | Create List | a    | b    | c    |
        | ${ints} =   | Create List | ${1} | ${2} | ${3} |
        """
        return list(items)


class _Verify:

    def fail(self, msg=None):
        """Fails the test immediately with the given (optional) message.

        See `Fatal Error` if you need to stop the whole test execution.
        """
        raise AssertionError(msg) if msg else AssertionError()

    def fatal_error(self, msg=None):
        """Stops the whole test execution.

        The test or suite where this keyword is used fails with the provided
        message, and subsequent tests fail with a canned message.
        Possible teardowns will nevertheless be executed.

        See `Fail` if you only want to stop one test case unconditionally.
        """
        error = AssertionError(msg) if msg else AssertionError()
        error.ROBOT_EXIT_ON_FAILURE = True
        raise error

    def exit_for_loop(self):
        """Immediately stops executing the enclosing for loop.

        This keyword can be used directly in a for loop or in a keyword that
        the for loop uses. In both cases the test execution continues after
        the for loop. If executed outside of a for loop, the test fails.

        Example:
        | :FOR | ${var} | IN | @{SOME LIST} |
        |      | Run Keyword If | '${var}' == 'EXIT' | Exit For Loop |
        |      | Do Something   | ${var} |

        New in Robot Framework 2.5.2
        """
        # Error message is shown only if there is no enclosing for loop
        error = AssertionError('Exit for loop without enclosing for loop.')
        error.ROBOT_EXIT_FOR_LOOP = True
        raise error

    def should_not_be_true(self, condition, msg=None):
        """Fails if the given condition is true.

        See `Should Be True` for details about how `condition` is evaluated and
        how `msg` can be used to override the default error message.
        """
        if msg is None:
            msg = "'%s' should not be true" % condition
        asserts.fail_if(self._is_true(condition), msg)

    def should_be_true(self, condition, msg=None):
        """Fails if the given condition is not true.

        If `condition` is a string (e.g. '${rc} < 10'), it is evaluated as a
        Python expression using the built-in 'eval' function and the keyword
        status is decided based on the result. If a non-string item is given,
        the status is got directly from its truth value as explained at
        http://docs.python.org/lib/truth.html.

        The default error message ('<condition> should be true') is not very
        informative, but it can be overridden with the `msg` argument.

        Examples:
        | Should Be True | ${rc} < 10  |
        | Should Be True | '${status}' == 'PASS' | # Strings must be quoted |
        | Should Be True | ${number}   | # Passes if ${number} is not zero |
        | Should Be True | ${list}     | # Passes if ${list} is not empty  |
        """
        if msg is None:
            msg = "'%s' should be true" % condition
        asserts.fail_unless(self._is_true(condition), msg)

    def should_be_equal(self, first, second, msg=None, values=True):
        """Fails if the given objects are unequal.

        - If `msg` is not given, the error message is 'first != second'.
        - If `msg` is given and `values` is either Boolean False or the
          string 'False' or 'No Values', the error message is simply `msg`.
        - Otherwise the error message is '`msg`: `first` != `second`'.
        """
        asserts.fail_unless_equal(first, second, msg, self._include_values(values))

    def _include_values(self, values):
        if isinstance(values, basestring):
            return values.lower() not in ['no values', 'false']
        return bool(values)

    def should_not_be_equal(self, first, second, msg=None, values=True):
        """Fails if the given objects are equal.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        asserts.fail_if_equal(first, second, msg, self._include_values(values))

    def should_not_be_equal_as_integers(self, first, second, msg=None, values=True):
        """Fails if objects are equal after converting them to integers.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        first, second = [ self.convert_to_integer(i) for i in first, second ]
        self.should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_integers(self, first, second, msg=None, values=True):
        """Fails if objects are unequal after converting them to integers.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        first, second = [ self.convert_to_integer(i) for i in first, second ]
        self.should_be_equal(first, second, msg, values)

    def should_not_be_equal_as_numbers(self, first, second, msg=None, values=True):
        """Fails if objects are equal after converting them to real numbers.

        The check for equality is done using six decimal places.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        first = round(self.convert_to_number(first), 6)
        second = round(self.convert_to_number(second), 6)
        self.should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_numbers(self, first, second, msg=None, values=True):
        """Fails if objects are unequal after converting them to real numbers.

        The check for equality is done using six decimal places.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        first = round(self.convert_to_number(first), 6)
        second = round(self.convert_to_number(second), 6)
        self.should_be_equal(first, second, msg, values)

    def should_not_be_equal_as_strings(self, first, second, msg=None, values=True):
        """Fails if objects are equal after converting them to strings.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        first, second = [ self.convert_to_string(i) for i in first, second ]
        self.should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_strings(self, first, second, msg=None, values=True):
        """Fails if objects are unequal after converting them to strings.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        first, second = [ self.convert_to_string(i) for i in first, second ]
        self.should_be_equal(first, second, msg, values)

    def should_not_start_with(self, str1, str2, msg=None, values=True):
        """Fails if the string `str1` starts with the string `str2`.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'starts with')
        asserts.fail_if(str1.startswith(str2), msg)

    def should_start_with(self, str1, str2, msg=None, values=True):
        """Fails if the string `str1` does not start with the string `str2`.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'does not start with')
        asserts.fail_unless(str1.startswith(str2), msg)

    def should_not_end_with(self, str1, str2, msg=None, values=True):
        """Fails if the string `str1` ends with the string `str2`.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'ends with')
        asserts.fail_if(str1.endswith(str2), msg)

    def should_end_with(self, str1, str2, msg=None, values=True):
        """Fails if the string `str1` does not end with the string `str2`.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'does not end with')
        asserts.fail_unless(str1.endswith(str2), msg)

    def should_not_contain(self, item1, item2, msg=None, values=True):
        """Fails if `item1` contains `item2` one or more times.

        Works with strings, lists, and anything that supports Python's 'in'
        keyword. See `Should Be Equal` for an explanation on how to override
        the default error message with `msg` and `values`.

        Examples:
        | Should Not Contain | ${output}    | FAILED |
        | Should Not Contain | ${some_list} | value  |
        """
        msg = self._get_string_msg(item1, item2, msg, values, 'contains')
        asserts.fail_if(item2 in item1, msg)

    def should_contain(self, item1, item2, msg=None, values=True):
        """Fails if `item1` does not contain `item2` one or more times.

        Works with strings, lists, and anything that supports Python's 'in'
        keyword. See `Should Be Equal` for an explanation on how to override
        the default error message with `msg` and `values`.

        Examples:
        | Should Contain | ${output}    | PASS |
        | Should Contain | ${some_list} | value  |
        """
        msg = self._get_string_msg(item1, item2, msg, values, 'does not contain')
        asserts.fail_unless(item2 in item1, msg)

    def should_contain_x_times(self, item1, item2, count, msg=None):
        """Fails if `item1` does not contain `item2` `count` times.

        Works with strings, lists and all objects that `Get Count` works
        with. The default error message can be overridden with `msg` and
        the actual count is always logged.

        Examples:
        | Should Contain X Times | ${output}    | hello  | 2 |
        | Should Contain X Times | ${some list} | value  | 3 |
        """
        if not msg:
            msg = "'%s' does not contain '%s' %s times" % (item1, item2, count)
        self.should_be_equal_as_integers(self.get_count(item1, item2),
                                         count, msg, values=False)

    def get_count(self, item1, item2):
        """Returns and logs how many times `item2` is found from `item1`.

        This keyword works with Python strings and lists and all objects
        that either have 'count' method or can be converted to Python lists.

        Example:
        | ${count} = | Get Count | ${some item} | interesting value |
        | Should Be True | 5 < ${count} < 10 |
        """
        if not hasattr(item1, 'count'):
            try:
                item1 = list(item1)
            except:
                raise RuntimeError("Converting '%s' to list failed: %s"
                                % (item1, utils.get_error_message()))
        count = item1.count(item2)
        self.log('Item found from the first item %d time%s'
                 % (count, utils.plural_or_not(count)))
        return count

    def should_not_match(self, string, pattern, msg=None, values=True):
        """Fails if the given `string` matches the given `pattern`.

        Pattern matching is similar as matching files in a shell, and it is
        always case-sensitive. In the pattern '*' matches to anything and '?'
        matches to any single character.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        msg = self._get_string_msg(string, pattern, msg, values, 'matches')
        asserts.fail_if(self._matches(string, pattern), msg)

    def should_match(self, string, pattern, msg=None, values=True):
        """Fails unless the given `string` matches the given `pattern`.

        Pattern matching is similar as matching files in a shell, and it is
        always case-sensitive. In the pattern, '*' matches to anything and '?'
        matches to any single character.

        See `Should Be Equal` for an explanation on how to override the default
        error message with `msg` and `values`.
        """
        msg = self._get_string_msg(string, pattern, msg, values,
                                   'does not match')
        asserts.fail_unless(self._matches(string, pattern), msg)

    def should_match_regexp(self, string, pattern, msg=None, values=True):
        """Fails if `string` does not match `pattern` as a regular expression.

        Regular expression check is done using the Python 're' module, which
        has a pattern syntax derived from Perl, and thus also very similar to
        the one in Java. See the following documents for more details about
        regular expressions in general and Python implementation in particular.

        * http://docs.python.org/lib/module-re.html
        * http://www.amk.ca/python/howto/regex/

        Things to note about the regexp syntax in Robot Framework test data:

        1) Backslash is an escape character in the test data, and possible
        backslashes in the pattern must thus be escaped with another backslash
        (e.g. '\\\\d\\\\w+').

        2) Strings that may contain special characters, but should be handled
        as literal strings, can be escaped with the `Regexp Escape` keyword.

        3) The given pattern does not need to match the whole string. For
        example, the pattern 'ello' matches the string 'Hello world!'. If
        a full match is needed, the '^' and '$' characters can be used to
        denote the beginning and end of the string, respectively. For example,
        '^ello$' only matches the exact string 'ello'.

        4) Possible flags altering how the expression is parsed (e.g.
        re.IGNORECASE, re.MULTILINE) can be set by prefixing the pattern with
        the '(?iLmsux)' group (e.g. '(?im)pattern'). The available flags are
        'IGNORECASE': 'i', 'MULTILINE': 'm', 'DOTALL': 's', 'VERBOSE': 'x',
        'UNICODE': 'u', and 'LOCALE': 'L'.

        If this keyword passes, it returns the portion of the string that
        matched the pattern. Additionally, the possible captured groups are
        returned.

        See the `Should Be Equal` keyword for an explanation on how to override
        the default error message with the `msg` and `values` arguments.

        Examples:
        | Should Match Regexp | ${output} | \\\\d{6}   | # Output contains six numbers  |
        | Should Match Regexp | ${output} | ^\\\\d{6}$ | # Six numbers and nothing more |
        | ${ret} = | Should Match Regexp | Foo: 42 | (?i)foo: \\\\d+ |
        | ${match} | ${group1} | ${group2} = |
        | ...      | Should Match Regexp | Bar: 43 | (Foo|Bar): (\\\\d+) |
        =>
        - ${ret} = 'Foo: 42'
        - ${match} = 'Bar: 43'
        - ${group1} = 'Bar'
        - ${group2} = '43'
        """
        msg = self._get_string_msg(string, pattern, msg, values,
                                   'does not match')
        res = re.search(pattern, string)
        asserts.fail_if_none(res, msg, False)
        match = res.group(0)
        groups = res.groups()
        if groups:
            return [match] + list(groups)
        return match

    def should_not_match_regexp(self, string, pattern, msg=None, values=True):
        """Fails if `string` matches `pattern` as a regular expression.

        See `Should Match Regexp` for more information about arguments.
        """
        msg = self._get_string_msg(string, pattern, msg, values, 'matches')
        asserts.fail_unless_none(re.search(pattern, string), msg, False)

    def get_length(self, item):
        """Returns and logs the length of the given item.

        The keyword first tries to get the length with the Python function
        'len', which calls the item's '__len__' method internally. If that
        fails, the keyword tries to call the item's 'length' and 'size' methods
        directly. The final attempt is trying to get the value of the item's
        'length' attribute. If all these attempts are unsuccessful, the keyword
        fails.
        """
        length = self._get_length(item)
        self.log('Length is %d' % length)
        return length

    def _get_length(self, item):
        try: return len(item)
        except utils.RERAISED_EXCEPTIONS: raise
        except:
            try: return item.length()
            except utils.RERAISED_EXCEPTIONS: raise
            except:
                try: return item.size()
                except utils.RERAISED_EXCEPTIONS: raise
                except:
                    try: return item.length
                    except utils.RERAISED_EXCEPTIONS: raise
                    except:
                        raise RuntimeError("Could not get length of '%s'" % item)

    def length_should_be(self, item, length, msg=None):
        """Verifies that the length of the given item is correct.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the `msg` argument.
        """
        length = self.convert_to_integer(length)
        if self.get_length(item) != length:
            if msg is None:
                msg = "Length of '%s' should be %d but it is %d" \
                        % (item, length, self.get_length(item))
            raise AssertionError(msg)

    def should_be_empty(self, item, msg=None):
        """Verifies that the given item is empty.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the `msg` argument.
        """
        if self.get_length(item) > 0:
            if msg is None:
                msg = "'%s' should be empty" % item
            raise AssertionError(msg)

    def should_not_be_empty(self, item, msg=None):
        """Verifies that the given item is not empty.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the `msg` argument.
        """
        if self.get_length(item) == 0:
            if msg is None:
                msg = "'%s' should not be empty" % item
            raise AssertionError(msg)

    def _get_string_msg(self, str1, str2, msg, values, delim):
        _msg = "'%s' %s '%s'" % (str1, delim, str2)
        if msg is None:
            msg = _msg
        elif values is True:
            msg = '%s: %s' % (msg, _msg)
        return msg


class _Variables:

    def get_variables(self):
        """Returns a dictionary containing all variables in the current scope."""
        return NAMESPACES.current.variables

    def log_variables(self, level='INFO'):
        """Logs all variables in the current scope with given log level."""
        variables = self.get_variables()
        for name in sorted(variables.keys(), key=lambda string: string.lower()):
            msg = utils.format_assign_message(name, variables[name], cut_long=False)
            self.log(msg, level)

    def variable_should_exist(self, name, msg=None):
        """Fails unless the given variable exists within the current scope.

        The name of the variable can be given either as a normal variable name
        (e.g. ${NAME}) or in escaped format (e.g. \\${NAME}). Notice that the
        former works only in Robot Framework 2.1 and newer, and it has some
        limitations explained in `Set Suite Variable`.

        The default error message can be overridden with the `msg` argument.
        """
        name = self._get_var_name(name)
        variables = self.get_variables()
        if msg:
            msg = variables.replace_string(msg)
        else:
            msg = "Variable %s does not exist" % name
        asserts.fail_unless(variables.has_key(name), msg)

    def variable_should_not_exist(self, name, msg=None):
        """Fails if the given variable exists within the current scope.

        The name of the variable can be given either as a normal variable name
        (e.g. ${NAME}) or in escaped format (e.g. \\${NAME}). Notice that the
        former works only in Robot Framework 2.1 and newer, and it has some
        limitations explained in `Set Suite Variable`.

        The default error message can be overridden with the `msg` argument.
        """
        name = self._get_var_name(name)
        variables = self.get_variables()
        if msg:
            msg = variables.replace_string(msg)
        else:
            msg = "Variable %s exists" % name
        asserts.fail_if(variables.has_key(name), msg)

    def replace_variables(self, text):
        """Replaces variables in the given text with their current values.

        If the text contains undefined variables, this keyword fails.

        Example:

        The file 'template.txt' contains 'Hello ${NAME}!' and variable
        '${NAME}' has the value 'Robot'.

        | ${template} =   | Get File          | ${CURDIR}/template.txt |
        | ${message} =    | Replace Variables | ${template}            |
        | Should Be Equal | ${message}        | Hello Robot!           |

        If the given `text` contains only a single variable, its value is
        returned as-is and it can be any object. Otherwise this keyword
        always returns a string.
        """
        return self.get_variables().replace_scalar(text)

    def set_variable(self, *values):
        """Returns the given values which can then be assigned to a variables.

        This keyword is mainly used for setting scalar variables.
        Additionally it can be used for converting a scalar variable
        containing a list to a list variable or to multiple scalar variables.
        It is recommended to use `Create List' when creating new lists.

        Examples:
        | ${hi} =   | Set Variable | Hello, world! |
        | ${hi2} =  | Set Variable | I said: ${hi} |
        | ${var1}   | ${var2} =    | Set Variable | Hello | world |
        | @{list} = | Set Variable | ${list with some items} |
        | ${item1}  | ${item2} =   | Set Variable  | ${list with 2 items} |

        Variables created with this keyword are available only in the
        scope where they are created. See `Set Global Variable`, `Set
        Test Variable` and `Set Suite Variable` for information on how to
        set variables so that they are available also in a larger scope.
        """
        if len(values) == 0:
            return ''
        elif len(values) == 1:
            return values[0]
        else:
            return list(values)

    def set_test_variable(self, name, *values):
        """Makes a variable available everywhere within the scope of the current test.

        Variables set with this keyword are available everywhere within the
        scope of the currently executed test case. For example, if you set a
        variable in a user keyword, it is available both in the test case level
        and also in all other user keywords used in the current test. Other
        test cases will not see variables set with this keyword.

        See `Set Suite Variable` for more information and examples.
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self.get_variables().set_test(name, value)
        self._log_set_variable(name, value)

    def set_suite_variable(self, name, *values):
        """Makes a variable available everywhere within the scope of the current suite.

        Variables set with this keyword are available everywhere within the
        scope of the currently executed test suite. Setting variables with this
        keyword thus has the same effect as creating them using the Variable
        table in the test data file or importing them from variable files.
        Other test suites, including possible child test suites, will not see
        variables set with this keyword.

        The name of the variable can be given either as a normal variable name
        (e.g. ${NAME}) or in escaped format (e.g. \\${NAME}). Notice that the
        former works only in Robot Framework 2.1 and newer.

        If a variable already exists within the new scope, its value will be
        overwritten. Otherwise a new variable is created. If a variable already
        exists within the current scope, the value can be left empty and the
        variable within the new scope gets the value within the current scope.

        Examples:
        | Set Suite Variable | ${GREET} | Hello, world! |
        | ${ID} =            | Get ID   |
        | Set Suite Variable | ${ID}    |

        *NOTE:* If the variable has value which itself is a variable (escaped
        or not), you must always use the escaped format like in the example
        below. This limitation applies to `Set Test/Suite/Global Variable`
        and `Variable Should (Not) Exist` keywords.

        Example:
        | ${NAME} =          | Set Variable | \${variable} |
        | Set Suite Variable | ${NAME}      | new value    | # Does not work |
        | Set Suite Variable | \${NAME}     | new value    | # This works    |
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self.get_variables().set_suite(name, value)
        self._log_set_variable(name, value)

    def set_global_variable(self, name, *values):
        """Makes a variable available globally in all tests and suites.

        Variables set with this keyword are globally available in all test
        cases and suites executed after setting them. Setting variables with
        this keyword thus has the same effect as creating from the command line
        using the options '--variable' or '--variablefile'. Because this
        keyword can change variables everywhere, it should be used with care.

        See `Set Suite Variable` for more information and examples.
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self.get_variables().set_global(name, value)
        self._log_set_variable(name, value)

    # Helpers

    def _get_var_name(self, orig):
        name = self._resolve_possible_variable(orig)
        try:
            return self._unescape_variable_if_needed(name)
        except ValueError:
            raise RuntimeError("Invalid variable syntax '%s'" % orig)

    def _resolve_possible_variable(self, name):
        try:
            resolved = self.get_variables()[name]
            return self._unescape_variable_if_needed(resolved)
        except (KeyError, ValueError, DataError):
            return name

    def _unescape_variable_if_needed(self, name):
        if not (isinstance(name, basestring) and len(name) > 1):
            raise ValueError
        if name.startswith('\\'):
            name = name[1:]
        elif name[0] in ['$','@'] and name[1] != '{':
            name = '%s{%s}' % (name[0], name[1:])
        if is_var(name):
            return name
        # Support for possible internal variables (issue 397)
        name = '%s{%s}' % (name[0], self.replace_variables(name[2:-1]))
        if is_var(name):
            return name
        raise ValueError

    def _get_var_value(self, name, values):
        variables = self.get_variables()
        if not values:
            return variables[name]
        values = variables.replace_list(values)
        if len(values) == 1 and name[0] == '$':
            return values[0]
        return list(values)

    def _log_set_variable(self, name, value):
        self.log(utils.format_assign_message(name, value))


class _RunKeyword:

    # If you use any of these run keyword variants from another library, you
    # should register those keywords with 'register_run_keyword' method. See
    # the documentation of that method at the end of this file. There are also
    # other run keyword variant keywords in BuiltIn which can also be seen
    # at the end of this file.

    def run_keyword(self, name, *args):
        """Executes the given keyword with the given arguments.

        Because the name of the keyword to execute is given as an argument, it
        can be a variable and thus set dynamically, e.g. from a return value of
        another keyword or from the command line.
        """
        if not isinstance(name, basestring):
            raise DataError('Keyword name must be a string')
        kw = Keyword(name, list(args))
        return kw.run(ExecutionContext(NAMESPACES.current, OUTPUT))

    def run_keywords(self, *names):
        """Executes all the given keywords in a sequence without arguments.

        This keyword is mainly useful in setups and teardowns when they need to
        take care of multiple actions and creating a new higher level user
        keyword is overkill. User keywords must nevertheless be used if the
        executed keywords need to take arguments.

        Example:
        |  *Setting*  |   *Value*    |      *Value*        |    *Value*    |
        | Suite Setup | Run Keywords | Initialize database | Start servers |
        """
        errors = []
        for kw in self.get_variables().replace_list(names):
            try:
                self.run_keyword(kw)
            except ExecutionFailed, err:
                errors.extend(err.get_errors())
                context = ExecutionContext(NAMESPACES.current, OUTPUT)
                if not err.can_continue(context.teardown):
                    break
        if errors:
            raise ExecutionFailures(errors)


    def run_keyword_if(self, condition, name, *args):
        """Runs the given keyword with the given arguments, if `condition` is true.

        The given `condition` is evaluated similarly as with `Should Be
        True` keyword, and `name` and `*args` have same semantics as with
        `Run Keyword`.

        Example, a simple if/else construct:
        | ${status} | ${value} = | Run Keyword And Ignore Error | My Keyword |
        | Run Keyword If     | '${status}' == 'PASS' | Some Action    |
        | Run Keyword Unless | '${status}' == 'PASS' | Another Action |

        In this example, only either 'Some Action' or 'Another Action' is
        executed, based on the status of 'My Keyword'.
        """
        if self._is_true(condition):
            return self.run_keyword(name, *args)

    def run_keyword_unless(self, condition, name, *args):
        """Runs the given keyword with the given arguments, if `condition` is false.

        See `Run Keyword If` for more information and an example.
        """
        if not self._is_true(condition):
            return self.run_keyword(name, *args)

    def run_keyword_and_ignore_error(self, name, *args):
        """Runs the given keyword with the given arguments and ignores possible error.

        This keyword returns two values, so that the first is either 'PASS' or
        'FAIL', depending on the status of the executed keyword. The second
        value is either the return value of the keyword or the received error
        message.

        The keyword name and arguments work as in `Run Keyword`. See
        `Run Keyword If` for a usage example.

        Starting from Robot Framework 2.5 errors caused by invalid syntax,
        timeouts, or fatal exceptions are not caught by this keyword.
        """
        try:
            return 'PASS', self.run_keyword(name, *args)
        except ExecutionFailed, err:
            if err.dont_cont:
                raise
            return 'FAIL', unicode(err)

    def run_keyword_and_continue_on_failure(self, name, *args):
        """Runs the keyword and continues execution even if a failure occurs.

        The keyword name and arguments work as with `Run Keyword`.

        Example:
        | Run Keyword And Continue On Failure | Fail | This is a stupid example |
        | Log | This keyword is executed |

        This keyword was added in Robot Framework 2.5. The execution is not
        continued if the failure is caused by invalid syntax, timeout, or 
        fatal exception.
        """
        try:
            return self.run_keyword(name, *args)
        except ExecutionFailed, err:
            if not err.dont_cont:
                err.cont = True
            raise err

    def run_keyword_and_expect_error(self, expected_error, name, *args):
        """Runs the keyword and checks that the expected error occurred.

        The expected error must be given in the same format as in
        Robot Framework reports. It can be a pattern containing
        characters '?', which matches to any single character and
        '*', which matches to any number of any characters. `name` and
        `*args` have same semantics as with `Run Keyword`.

        If the expected error occurs, the error message is returned and it can
        be further processed/tested, if needed. If there is no error, or the
        error does not match the expected error, this keyword fails.

        Examples:
        | Run Keyword And Expect Error | My error | Some Keyword | arg1 | arg2 |
        | ${msg} = | Run Keyword And Expect Error | * | My KW |
        | Should Start With | ${msg} | Once upon a time in |

        Starting from Robot Framework 2.5 errors caused by invalid syntax,
        timeouts, or fatal exceptions are not caught by this keyword.
        """
        try:
            self.run_keyword(name, *args)
        except ExecutionFailed, err:
            if err.dont_cont:
                raise
        else:
            raise AssertionError("Expected error '%s' did not occur"
                                 % expected_error)
        if not self._matches(unicode(err), expected_error):
            raise AssertionError("Expected error '%s' but got '%s'"
                                 % (expected_error, err))
        return unicode(err)

    def repeat_keyword(self, times, name, *args):
        """Executes the specified keyword multiple times.

        `name` and `args` define the keyword that is executed
        similarly as with `Run Keyword`, and `times` specifies how many
        the keyword should be executed. `times` can be given as an
        integer or as a string that can be converted to an integer. It
        can also have postfix 'times' or 'x' (case and space
        insensitive) to make the expression easier to read.

        If `times` is zero or negative, the keyword is not executed at
        all. This keyword fails immediately if any of the execution
        rounds fails.

        Examples:
        | Repeat Keyword | 5 times | Goto Previous Page |
        | Repeat Keyword | ${var}  | Some Keyword | arg1 | arg2 |
        """
        times = utils.normalize(str(times))
        if times.endswith('times'):
            times = times[:-5]
        elif times.endswith('x'):
            times = times[:-1]
        times = self.convert_to_integer(times)
        if times <= 0:
            self.log("Keyword '%s' repeated zero times" % name)
        for i in xrange(times):
            self.log("Repeating keyword, round %d/%d" % (i+1, times))
            self.run_keyword(name, *args)

    def wait_until_keyword_succeeds(self, timeout, retry_interval, name, *args):
        """Waits until the specified keyword succeeds or the given timeout expires.

        `name` and `args` define the keyword that is executed
        similarly as with `Run Keyword`. If the specified keyword does
        not succeed within `timeout`, this keyword fails.
        `retry_interval` is the time to wait before trying to run the
        keyword again after the previous run has failed.

        Both `timeout` and `retry_interval` must be given in Robot Framework's
        time format (e.g. '1 minute', '2 min 3 s', '4.5').

        Example:
        | Wait Until Keyword Succeeds | 2 min | 5 sec | My keyword | arg1 | arg2 |

        Starting from Robot Framework 2.5 errors caused by invalid syntax,
        timeouts, or fatal exceptions are not caught by this keyword.
        """
        timeout = utils.timestr_to_secs(timeout)
        retry_interval = utils.timestr_to_secs(retry_interval)
        maxtime = time.time() + timeout
        error = None
        while not error:
            try:
                return self.run_keyword(name, *args)
            except ExecutionFailed, err:
                if err.dont_cont:
                    raise
                if time.time() > maxtime:
                    error = unicode(err)
                else:
                    time.sleep(retry_interval)
        raise AssertionError("Timeout %s exceeded. The last error was: %s"
                             % (utils.secs_to_timestr(timeout), error))

    def set_variable_if(self, condition, *values):
        """Sets variable based on the given condition.

        The basic usage is giving a condition and two values. The
        given condition is first evaluated the same way as with the
        `Should Be True` keyword. If the condition is true, then the
        first value is returned, and otherwise the second value is
        returned. The second value can also be omitted, in which case
        it has a default value None. This usage is illustrated in the
        examples below, where ${rc} is assumed to be zero.

        | ${var1} = | Set Variable If | ${rc} == 0 | zero     | nonzero |
        | ${var2} = | Set Variable If | ${rc} > 0  | value1   | value2  |
        | ${var3} = | Set Variable If | ${rc} > 0  | whatever |         |
        =>
        - ${var1} = 'zero'
        - ${var2} = 'value2'
        - ${var3} = None

        It is also possible to have 'Else If' support by replacing the
        second value with another condition, and having two new values
        after it. If the first condition is not true, the second is
        evaluated and one of the values after it is returned based on
        its truth value. This can be continued by adding more
        conditions without a limit.

        | ${var} = | Set Variable If | ${rc} == 0        | zero           |
        | ...      | ${rc} > 0       | greater than zero | less then zero |
        |          |
        | ${var} = | Set Variable If |
        | ...      | ${rc} == 0      | zero              |
        | ...      | ${rc} == 1      | one               |
        | ...      | ${rc} == 2      | two               |
        | ...      | ${rc} > 2       | greater than two  |
        | ...      | ${rc} < 0       | less than zero    |
        """
        values = self._verify_values_for_set_variable_if(list(values))
        if self._is_true(condition):
            return NAMESPACES.current.variables.replace_scalar(values[0])
        values = self._verify_values_for_set_variable_if(values[1:], True)
        if len(values) == 1:
            return NAMESPACES.current.variables.replace_scalar(values[0])
        return self.run_keyword('BuiltIn.Set Variable If', *values[0:])

    def _verify_values_for_set_variable_if(self, values, default=False):
        if not values:
            if default:
                return [None]
            raise RuntimeError('At least one value is required')
        if is_list_var(values[0]):
            values[:1] = [ utils.escape(item) for item in
                           NAMESPACES.current.variables[values[0]] ]
            return self._verify_values_for_set_variable_if(values)
        return values

    def run_keyword_if_test_failed(self, name, *args):
        """Runs the given keyword with the given arguments, if the test failed.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        test = self._get_test_in_teardown('Run Keyword If Test Failed')
        if test.status == 'FAIL':
            return self.run_keyword(name, *args)

    def run_keyword_if_test_passed(self, name, *args):
        """Runs the given keyword with the given arguments, if the test passed.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        test = self._get_test_in_teardown('Run Keyword If Test Passed')
        if test.status == 'PASS':
            return self.run_keyword(name, *args)

    def run_keyword_if_timeout_occurred(self, name, *args):
        """Runs the given keyword if either a test or a keyword timeout has occurred.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.

        Available in Robot Framework 2.5 and newer.
        """
        test = self._get_test_in_teardown('Run Keyword If Timeout Occurred')
        if test.timeout.any_timeout_occurred():
            return self.run_keyword(name, *args)

    def _get_test_in_teardown(self, kwname):
        test = NAMESPACES.current.test
        if test is not None and test.status != 'RUNNING':
            return test
        raise RuntimeError("Keyword '%s' can only be used in test teardown"
                        % kwname)

    def run_keyword_if_all_critical_tests_passed(self, name, *args):
        """Runs the given keyword with the given arguments, if all critical tests passed.

        This keyword can only be used in suite teardown. Trying to use it in
        any other place will result in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        suite = self._get_suite_in_teardown('Run Keyword If '
                                            'All Critical Tests Passed')
        if suite.critical_stats.failed == 0:
            return self.run_keyword(name, *args)

    def run_keyword_if_any_critical_tests_failed(self, name, *args):
        """Runs the given keyword with the given arguments, if any critical tests failed.

        This keyword can only be used in a suite teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        suite = self._get_suite_in_teardown('Run Keyword If '
                                            'Any Critical Tests Failed')
        if suite.critical_stats.failed > 0:
            return self.run_keyword(name, *args)

    def run_keyword_if_all_tests_passed(self, name, *args):
        """Runs the given keyword with the given arguments, if all tests passed.

        This keyword can only be used in a suite teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        suite = self._get_suite_in_teardown('Run Keyword If All Tests Passed')
        if suite.all_stats.failed == 0:
            return self.run_keyword(name, *args)

    def run_keyword_if_any_tests_failed(self, name, *args):
        """Runs the given keyword with the given arguments, if one or more tests failed.

        This keyword can only be used in a suite teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        suite = self._get_suite_in_teardown('Run Keyword If Any Tests Failed')
        if suite.all_stats.failed > 0:
            return self.run_keyword(name, *args)

    def _get_suite_in_teardown(self, kwname):
        if NAMESPACES.current.suite.status == 'RUNNING':
            raise RuntimeError("Keyword '%s' can only be used in suite teardown"
                            % kwname)
        return NAMESPACES.current.suite


class _Misc:

    def no_operation(self):
        """Does absolutely nothing."""

    def sleep(self, time_, reason=None):
        """Pauses the test executed for the given time.

        `time` may be either a number or a time string. Time strings are in
        a format such as '1 day 2 hours 3 minutes 4 seconds 5milliseconds' or
        '1d 2h 3m 4s 5ms', and they are fully explained in an appendix of Robot
        Framework User Guide. Optional `reason` can be used to explain why
        sleeping is necessary. Both the time slept and the reason are logged.

        Examples:
        | Sleep | 42                   |
        | Sleep | 1.5                  |
        | Sleep | 2 minutes 10 seconds |
        | Sleep | 10s                  | Wait for a reply |
        """
        seconds = utils.timestr_to_secs(time_)
        # Python hangs with negative values
        if seconds < 0:
            seconds = 0
        time.sleep(seconds)
        self.log('Slept %s' % utils.secs_to_timestr(seconds))
        if reason:
            self.log(reason)

    def catenate(self, *items):
        """Catenates the given items together and returns the resulted string.

        By default, items are catenated with spaces, but if the first item
        contains the string 'SEPARATOR=<sep>', the separator '<sep>' is used.
        Items are converted into strings when necessary.

        Examples:
        | ${str1} = | Catenate | Hello         | world |       |
        | ${str2} = | Catenate | SEPARATOR=--- | Hello | world |
        | ${str3} = | Catenate | SEPARATOR=    | Hello | world |
        =>
        - ${str1} = 'Hello world'
        - ${str2} = 'Hello---world'
        - ${str3} = 'Helloworld'
        """
        if not items:
            return ''
        items = [ utils.unic(item) for item in items ]
        if items[0].startswith('SEPARATOR='):
            sep = items[0][len('SEPARATOR='):]
            items = items[1:]
        else:
            sep = ' '
        return sep.join(items)

    def log(self, message, level="INFO"):
        """Logs the given message with the given level.

        Valid levels are TRACE, DEBUG, INFO (default), HTML and WARN.

        The HTML level is special because it allows writing messages
        without HTML code in them being escaped. For example, logging
        a message '<img src="image.png">' using the HTML level creates
        an image, but with other levels the message would be that exact
        string. Notice that invalid HTML can easily corrupt the whole
        log file so this feature should be used with care. The
        actual log level used for HTML messages is INFO.

        Messages logged with the WARN level will be visible also in
        the console and in the Test Execution Errors section in the
        log file.
        """
        LOGGER.log_message(Message(message, level))

    def log_many(self, *messages):
        """Logs the given messages as separate entries with the INFO level."""
        for msg in messages:
            self.log(msg)

    def comment(self, *messages):
        """Displays the given messages in the log file as keyword arguments.

        This keyword does nothing with the arguments it receives, but as they
        are visible in the log, this keyword can be used to display simple
        messages. Given arguments are ignored so thoroughly that they can even
        contain non-existing variables. If you are interested about variable
        values, you can use the `Log` or `Log Many` keywords.
        """
        pass

    def set_log_level(self, level):
        """Sets the log threshold to the specified level and returns the old level.

        Messages below the level will not logged. The default logging level is
        INFO, but it can be overridden with the command line option
        '--loglevel'.

        The available levels: TRACE, DEBUG, INFO (default), WARN and NONE (no
        logging).
        """
        old = OUTPUT.set_log_level(level)
        self.log('Log level changed from %s to %s' % (old, level.upper()))
        return old

    def import_library(self, name, *args):
        """Imports a library with the given name and optional arguments.

        This functionality allows dynamic importing of libraries while tests
        are running. That may be necessary, if the library itself is dynamic
        and not yet available when test data is processed. In a normal case,
        libraries should be imported using the Library setting in the Setting
        table.

        This keyword supports importing libraries both using library
        names and physical paths. When path are used, they must be
        given in absolute format. Forward slashes can be used as path
        separators in all operating systems. It is possible to use
        arguments as well as to give a custom name with 'WITH NAME'
        syntax. For more information about importing libraries, see
        Robot Framework User Guide.

        Examples:
        | Import Library | MyLibrary |
        | Import Library | ${CURDIR}/Library.py | some | args |
        | Import Library | ${CURDIR}/../libs/Lib.java | arg | WITH NAME | JavaLib |
        """
        NAMESPACES.current.import_library(name.replace('/', os.sep), list(args))

    def import_variables(self, path, *args):
        """Imports a variable file with the given path and optional arguments.

        Variables imported with this keyword are set into the test suite scope
        similarly when importing them in the Setting table using the Variables
        setting. These variables override possible existing variables with
        the same names and this functionality can thus be used to import new
        variables, e.g. for each test in a test suite.

        The given path must be absolute. Forward slashes can be used as path
        separator regardless the operating system.

        Examples:
        | Import Variables | ${CURDIR}/variables.py   |      |      |
        | Import Variables | ${CURDIR}/../vars/env.py | arg1 | arg2 |
        """
        NAMESPACES.current.import_variables(path.replace('/', os.sep),
                                            args, overwrite=True)

    def set_library_search_order(self, *libraries):
        """Sets the resolution order to use when a name matches multiple keywords.

        The library search order is used to resolve conflicts when a
        keyword name in the test data matches multiple keywords. The
        first library containing the keyword is selected and that
        keyword implementation used. If keyword is not found from any
        library, or the library search order is not set, executing the
        specified keyword fails.

        When this keyword is used, there is no need to use the long
        `LibraryName.Keyword Name` notation.  For example, instead of
        having

        | MyLibrary.Keyword | arg |
        | MyLibrary.Another Keyword |
        | MyLibrary.Keyword | xxx |

        you can have

        | Set Library Search Order | MyLibrary |
        | Keyword | arg |
        | Another Keyword |
        | Keyword | xxx |

        The library search order is valid only in the suite where this
        keyword is used in. The old order is returned and can be used
        to reset the search order later.
        """
        old_order = NAMESPACES.current.library_search_order
        NAMESPACES.current.library_search_order = libraries
        return old_order

    def get_time(self, format='timestamp', time_='NOW'):
        """Returns the given time in the requested format.

        How time is returned is determined based on the given `format` string
        as follows. Note that all checks are case-insensitive.

        1) If `format` contains the word 'epoch', the time is returned
           in seconds after the UNIX epoch. The return value is always
           an integer.

        2) If `format` contains any of the words 'year', 'month',
           'day', 'hour', 'min', or 'sec', only the selected parts are
           returned. The order of the returned parts is always the one
           in the previous sentence and the order of words in `format`
           is not significant. The parts are returned as zero-padded
           strings (e.g. May -> '05').

        3) Otherwise (and by default) the time is returned as a
           timestamp string in the format '2006-02-24 15:08:31'.

        By default this keyword returns the current time, but that can be
        altered using `time` argument as explained below. Notice that this
        argument is only available in Robot Framework 2.1.1 and newer.

        1) If `time` is a floating point number, it is interpreted as
           seconds since epoch (Jan 1, 1970 0:00:00). This
           documentation is written about 1177654467 seconds since
           epoch.

        2) If `time` is a valid timestamp, that time will be used. Valid
           timestamp formats are 'YYYY-MM-DD hh:mm:ss' and 'YYYYMMDD hhmmss'.

        3) If `time` is equal to 'NOW' (case-insensitive), the
           current time is used.

        4) If `time` is in the format 'NOW - 1 day' or 'NOW + 1 hour
           30 min', the current time plus/minus the time specified
           with the time string is used. The time string format is
           described in an appendix of Robot Framework User Guide.


        Examples (expecting the current time is 2006-03-29 15:06:21):
        | ${time} = | Get Time |             |  |  |
        | ${secs} = | Get Time | epoch       |  |  |
        | ${year} = | Get Time | return year |  |  |
        | ${yyyy}   | ${mm}    | ${dd} =     | Get Time | year,month,day |
        | @{time} = | Get Time | year month day hour min sec |  |  |
        | ${y}      | ${s} =   | Get Time    | seconds and year |  |
        =>
        - ${time} = '2006-03-29 15:06:21'
        - ${secs} = 1143637581
        - ${year} = '2006'
        - ${yyyy} = '2006', ${mm} = '03', ${dd} = '29'
        - @{time} = ['2006', '03', '29', '15', '06', '21']
        - ${y} = '2006'
        - ${s} = '21'

        | ${time} = | Get Time |      | 1177654467 |
        | ${secs} = | Get Time | sec  | 2007-04-27 09:14:27 |
        | ${year} = | Get Time | year | NOW                | # The time of execution |
        | ${day} = | Get Time | day  | NOW - 1d           | # 1 day subtraced from NOW |
        | @{time} = | Get Time | hour min sec | NOW + 1h 2min 3s   | # 1h 2min 3s added to NOW |
        =>
        - ${time} = '2007-04-27 09:14:27'
        - ${secs} = 27
        - ${year} = '2006'
        - ${day} = '28'
        - @{time} = ['16', '08', '24']

        """
        return utils.get_time(format, utils.parse_time(time_))

    def evaluate(self, expression, modules=None):
        """Evaluates the given expression in Python and returns the results.

        `modules` argument can be used to specify a comma separated
        list of Python modules to be imported and added to the
        namespace of the evaluated `expression`.

        Examples (expecting ${result} is 3.14):
        | ${status} = | Evaluate | 0 < ${result} < 10    |
        | ${down}   = | Evaluate | int(${result})        |
        | ${up}     = | Evaluate | math.ceil(${result})  | math |
        | ${random} = | Evaluate | random.randint(0, sys.maxint) | random,sys |
        =>
        - ${status} = True
        - ${down} = 3
        - ${up} = 4.0
        - ${random} = <random integer>

        Notice that instead of creating complicated expressions, it is
        recommended to move the logic into a test library.
        """
        modules = modules.replace(' ','').split(',') if modules else []
        namespace = dict([ (m, __import__(m)) for m in modules if m != '' ])
        try:
            return eval(expression, namespace)
        except:
            raise RuntimeError("Evaluating expression '%s' failed: %s"
                            % (expression, utils.get_error_message()))

    def call_method(self, object, method_name, *args):
        """Calls the named method of the given object with the provided arguments.

        The possible return value from the method is returned and can be
        assigned to a variable. Keyword fails both if the object does not have
        a method with the given name or if executing the method raises an
        exception.

        Examples:
        | Call Method      | ${hashtable} | put          | myname  | myvalue |
        | ${isempty} =     | Call Method  | ${hashtable} | isEmpty |         |
        | Should Not Be True | ${isempty} |              |         |         |
        | ${value} =       | Call Method  | ${hashtable} | get     | myname  |
        | Should Be Equal  | ${value}     | myvalue      |         |         |
        """
        try:
            method = getattr(object, method_name)
        except AttributeError:
            raise RuntimeError("Object '%s' does not have a method '%s'"
                               % (object, method_name))
        return method(*args)

    def regexp_escape(self, *patterns):
        """Returns each argument string escaped for use as a regular expression.

        This keyword can be used to escape strings to be used with
        `Should Match Regexp` and `Should Not Match Regexp` keywords.

        Escaping is done with Python's re.escape() function.

        Examples:
        | ${escaped} = | Regexp Escape | ${original} |
        | @{strings} = | Regexp Escape | @{strings}  |
        """
        if len(patterns) == 0:
            return ''
        if len(patterns) == 1:
            return re.escape(patterns[0])
        return [ re.escape(pattern) for pattern in patterns ]

    def set_test_message(self, message):
        """Sets message for for the current test.

        This is overridden by possible failure message, except when this keyword
        is used in test case teardown. In test case teardown this overrides
        messages even for failed tests.

        This keyword can not be used in suite setup or suite teardown.
        """
        test = NAMESPACES.current.test
        if test is None:
            raise RuntimeError("'Set Test Message' keyword cannot be used in "
                               "suite setup or teardown")
        test.message = message
        self.log('Set test message to:\n%s' % message)

    def set_tags(self, *tags):
        """Adds given `tags` for the current test or all tests in a suite.

        When this keyword is used inside a test case, that test gets
        the specified tags and other tests are not affected.

        If this keyword is used in a suite setup, all test cases in
        that suite, recursively, gets the given tags. It is a failure
        to use this keyword in a suite teardown.

        See `Remove Tags` for another keyword to modify tags at test
        execution time.
        """
        tags = utils.normalize_tags(tags)
        handler = lambda test: utils.normalize_tags(test.tags + tags)
        self._set_or_remove_tags(handler)
        self.log('Set tag%s %s.' % (utils.plural_or_not(tags),
                                    utils.seq2str(tags)))

    def remove_tags(self, *tags):
        """Removes given `tags` from the current test or all tests in a suite.

        Tags can be given exactly or using a pattern where '*' matches
        anything and '?' matches one character.

        This keyword can affect either one test case or all test cases in a
        test suite similarly as `Set Tags` keyword.

        Example:
        | Remove Tags | mytag | something-* | ?ython |
        """
        tags = utils.normalize_tags(tags)
        handler = lambda test: [ t for t in test.tags
                                 if not utils.matches_any(t, tags) ]
        self._set_or_remove_tags(handler)
        self.log('Removed tag%s %s.' % (utils.plural_or_not(tags),
                                        utils.seq2str(tags)))

    def _set_or_remove_tags(self, handler, suite=None, test=None):
        if not (suite or test):
            ns = NAMESPACES.current
            if ns.test is None:
                if ns.suite.status != 'RUNNING':
                    raise RuntimeError("'Set Tags' and 'Remove Tags' keywords "
                                       "cannot be used in suite teardown.")
                self._set_or_remove_tags(handler, suite=ns.suite)
            else:
                self._set_or_remove_tags(handler, test=ns.test)
                ns.variables.set_test('@{TEST_TAGS}', ns.test.tags)
            ns.suite._set_critical_tags(ns.suite.critical)
        elif suite:
            for sub in suite.suites:
                self._set_or_remove_tags(handler, suite=sub)
            for test in suite.tests:
                self._set_or_remove_tags(handler, test=test)
        else:
            test.tags = handler(test)

    def get_library_instance(self, name):
        """Returns the currently active instance of the specified test library.

        This keyword makes it easy for test libraries to interact with
        other test libraries that have state. This is illustrated by
        the Python example below:

        | from robot.libraries.BuiltIn import BuiltIn
        |
        | def title_should_start_with(expected):
        |     seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
        |     title = seleniumlib.get_title()
        |     if not title.startswith(expected):
        |         raise AssertionError("Title '%s' did not start with '%s'"
        |                              % (title, expected))

        It is also possible to use this keyword in the test data and
        pass the returned library instance to another keyword. If a
        library is imported with a custom name, the `name` used to get
        the instance must be that name and not the original library
        name.
        """
        return NAMESPACES.current.get_library_instance(name)


class BuiltIn(_Verify, _Converter, _Variables, _RunKeyword, _Misc):
    """An always available standard library with often needed keywords.

    `BuiltIn` is Robot Framework's standard library that provides a set
    of generic keywords needed often. It is imported automatically and
    thus always available. The provided keywords can be used, for example,
    for verifications (e.g. `Should Be Equal`, `Should Contain`),
    conversions (e.g. `Convert To Integer`) and for various other purposes
    (e.g. `Log`, `Sleep`, `Run Keyword If`, `Set Global Variable`).
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()

    def _matches(self, string, pattern):
        # Must use this instead of fnmatch when string may contain newlines.
        return utils.matches(string, pattern, caseless=False, spaceless=False)

    def _is_true(self, condition):
        if isinstance(condition, basestring):
            try:
                condition = eval(condition)
            except:
                raise RuntimeError("Evaluating condition '%s' failed: %s"
                                   % (condition, utils.get_error_message()))
        return bool(condition)


def register_run_keyword(library, keyword, args_to_process=None):
    """Registers 'run keyword' so that its arguments can be handled correctly.

    1) Why is this method needed

    Keywords running other keywords internally (normally using `Run Keyword`
    or some variants of it in BuiltIn) must have the arguments meant to the
    internally executed keyword handled specially to prevent processing them
    twice. This is done ONLY for keywords registered using this method.

    If the register keyword has same name as any keyword from Robot Framework
    standard libraries, it can be used without getting warnings. Normally
    there is a warning in such cases unless the keyword is used in long
    format (e.g. MyLib.Keyword).

    Starting from Robot Framework 2.5.2, keywords executed by registered run
    keywords can be tested with dryrun runmode with following limitations:
    - Registered keyword must have 'name' argument which takes keyword's name or
    Registered keyword must have '*names' argument which takes keywords' names
    - Keyword name does not contain variables

    2) How to use this method

    `library` is the name of the library where the registered keyword is
    implemented.

    `keyword` can be either a function or method implementing the
    keyword, or name of the implemented keyword as a string.

    `args_to_process` is needed when `keyword` is given as a string, and it
    defines how many of the arguments to the registered keyword must be
    processed normally. When `keyword` is a method or function, this
    information is got directly from it so that varargs (those specified with
    syntax '*args') are not processed but others are.

    3) Examples

    from robot.libraries.BuiltIn import BuiltIn, register_run_keyword

    def my_run_keyword(name, *args):
        # do something
        return BuiltIn().run_keyword(name, *args)

    # Either one of these works
    register_run_keyword(__name__, my_run_keyword)
    register_run_keyword(__name__, 'My Run Keyword', 1)

    -------------

    from robot.libraries.BuiltIn import BuiltIn, register_run_keyword

    class MyLibrary:
        def my_run_keyword_if(self, expression, name, *args):
            # do something
            return BuiltIn().run_keyword_if(expression, name, *args)

    # Either one of these works
    register_run_keyword('MyLibrary', MyLibrary.my_run_keyword_if)
    register_run_keyword('MyLibrary', 'my_run_keyword_if', 2)
    """
    RUN_KW_REGISTER.register_run_keyword(library, keyword, args_to_process)


for name in [ attr for attr in dir(_RunKeyword) if not attr.startswith('_') ]:
    register_run_keyword('BuiltIn', getattr(_RunKeyword, name))
for name in ['set_test_variable', 'set_suite_variable', 'set_global_variable',
             'variable_should_exist', 'variable_should_not_exist', 'comment']:
    register_run_keyword('BuiltIn', name, 0)
del name, attr
