#  Copyright 2008 Nokia Siemens Networks Oyj
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


import time as _time
import re

from robot import output
from robot.utils import asserts
from robot.errors import DataError
from robot import utils
from robot.variables import is_var, is_list_var
from robot.running import NAMESPACES, Keyword


def _is_true(expr):
    if utils.is_str(expr):
        expr = eval(expr)
    if expr:
        return True
    return False
    
    
class Converter:
    
    def convert_to_integer(self, item):
        """Converts given item to an integer number."""
        try:
            return long(item)
        except:
            raise DataError("%s cannot be converted to an integer" % item)

    def convert_to_number(self, item):
        """Converts given item to a floating point number."""
        try:
            return float(item)
        except:
            raise DataError("%s cannot be converted to a floating point number" 
                            % item)

    def convert_to_string(self, item):
        """Converts given item to a string.
        
        Note that if item is a Java object its 'toString' method is called.
        """
        return utils.unic(item)
    
    def convert_to_boolean(self, item):
        """Converts given item to boolean.
        
        Handles also strings 'True' and 'False' (case insensitive) as expected.
        """
        if utils.is_str(item):
            if utils.eq(item, 'True'):
                return True
            if utils.eq(item, 'False'):
                return False
        try:
            return bool(item)
        except:
            raise DataError("%s cannot be converted to a boolean" % item)

    def create_list(self, *items):
        """Returns a list containing given items.
    
        Returned list can be assigned both to ${scalar} and @{list} variables.
        Earlier can be used e.g. with Java keywords expecting an array as an
        argument.

        Examples:
        | @{list} =   | Create List | a    | b    | c    |
        | ${scaler} = | Create List | a    | b    | c    |
        | ${ints} =   | Create List | ${1} | ${2} | ${3} |
        """
        return list(items)


class Verify:

    # Wrappers for robot.asserts

    def fail(self, msg=None):
        """Fails the test immediately with the given message."""
        asserts.fail(msg)

    def should_not_be_true(self, expr, msg=None):
        """Fails if the the given expression (or item) is true.
                
        See 'Should Be True' for details about how 'expr' is evaluated and
        'msg' can be used to override the default error message.
        
        New in Robot 1.8.3. This is intended to replace old keyword 
        'Fail If', which still continues work.
        """
        if msg is None:
            msg = "'%s' should not be true" % expr
        asserts.fail_if(_is_true(expr), msg)

    def should_be_true(self, expr, msg=None):
        """Fails if the given expression (or item) is not true.
        
        If 'expr' is a string (e.g. '${rc} < 10'), it is evaluated as a Python 
        expression using built-in 'eval' function and keyword status is decided
        based on the result. If a non-string item is given, the status is got
        directly from its truth value as explained at
        http://docs.python.org/lib/truth.html.
         
        Default error message ('<expr> should be true') may not be too
        informative, but it can be overridden with 'msg' argument.
        
        Examples:
        | Should Be True | ${rc} < 10  |     
        | Should Be True | '${status}' == 'PASS' | # Strings must be quoted |
        | Should Be True | ${number}   | # Passes if ${number} is not zero |
        | Should Be True | ${list}     | # Passes if ${list} is not empty  | 
        
        New in Robot 1.8.3. This is intended to replace old keyword 
        'Fail Unless', which still continues work.
        """
        if msg is None:
            msg = "'%s' should be true" % expr
        asserts.fail_unless(_is_true(expr), msg)

    def should_be_equal(self, first, second, msg=None, values=True):
        """Fail if given objects are unequal.
        
        - If 'msg' is not given the possible error message is 'first != second'.
        - If 'msg' is given and 'values' is either boolean False or string 
          'False' or 'No Values' the error message is simply 'msg'.
        - Otherwise the error message is 'msg: first != second'.
        """
        values = utils.to_boolean(values, false_strs=['No Values'], default=True)
        asserts.fail_unless_equal(first, second, msg, values)

    def should_not_be_equal(self, first, second, msg=None, values=True):
        """Fail if given objects are equal.
             
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        values = utils.to_boolean(values, false_strs=['No Values'], default=True)
        asserts.fail_if_equal(first, second, msg, values)

    def should_not_be_equal_as_integers(self, first, second, msg=None, values=True):
        """Fail if objects are equal after converting them to integers.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        first, second = [ self.convert_to_integer(item) for item in first, second ]
        self.should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_integers(self, first, second, msg=None, values=True):
        """Fail if objects are unequal after converting them to integers.

        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        first, second = [ self.convert_to_integer(item) for item in first, second ]
        self.should_be_equal(first, second, msg, values)

    def should_not_be_equal_as_numbers(self, first, second, msg=None, values=True):
        """Fail if objects are equal after converting them to real numbers.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.        
        """
        first, second = [ self.convert_to_number(item) for item in first, second ]
        self.should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_numbers(self, first, second, msg=None, values=True):
        """Fail if objects are unequal after converting them to real numbers.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        first, second = [ self.convert_to_number(item) for item in first, second ]
        self.should_be_equal(first, second, msg, values)
        
    def should_not_be_equal_as_strings(self, first, second, msg=None, values=True):
        """Fail if objects are equal after converting them to strings.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        first, second = [ self.convert_to_string(item) for item in first, second ]
        self.should_not_be_equal(first, second, msg, values)
        
    def should_be_equal_as_strings(self, first, second, msg=None, values=True):
        """Fail if objects are unequal after converting them to strings.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        first, second = [ self.convert_to_string(item) for item in first, second ]
        self.should_be_equal(first, second, msg, values)

    def should_not_start_with(self, str1, str2, msg=None, values=True):
        """Fail if string 'str1' starts with string 'str2'.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'starts with')
        asserts.fail_if(str1.startswith(str2), msg)

    def should_start_with(self, str1, str2, msg=None, values=True):
        """Fail if string 'str1' does not start with string 'str2'.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'does not start with')
        asserts.fail_unless(str1.startswith(str2), msg)

    def should_not_end_with(self, str1, str2, msg=None, values=True):
        """Fail if string 'str1' ends with string 'str2'.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'ends with')
        asserts.fail_if(str1.endswith(str2), msg)

    def should_end_with(self, str1, str2, msg=None, values=True):
        """Fail if string 'str1' does not end with string 'str2'.

        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.        
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'does not end with')
        asserts.fail_unless(str1.endswith(str2), msg)

    def should_not_contain(self, str1, str2, msg=None, values=True):
        """Fail if string 'str1' contains string 'str2' one or more times.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'contains')
        asserts.fail_if(str1.count(str2) > 0, msg)

    def should_contain(self, str1, str2, msg=None, values=True):
        """Fail if string 'str1' does not contain string 'str2' one or more times.
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'does not contain')
        asserts.fail_unless(str1.count(str2) > 0, msg)

    def should_not_match(self, string, pattern, msg=None, values=True):
        """Fail if the given 'string' matches the given 'pattern'.

        Pattern matching is similar as matching files in a shell and it is
        always case-sensitive. In the pattern '*' matches to anything and '?'
        matches to any single character.  
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        msg = self._get_string_msg(string, pattern, msg, values, 'matches')
        asserts.fail_if(self._matches(string, pattern), msg)

    def should_match(self, string, pattern, msg=None, values=True):
        """Fail unless the given 'string' matches the given 'pattern'.

        Pattern matching is similar as matching files in a shell and it is
        always case-sensitive. In the pattern '*' matches to anything and '?'
        matches to any single character.  
        
        See 'Should Be Equal' for explanation on how to override default error
        message with 'msg' and 'values'.
        """
        msg = self._get_string_msg(string, pattern, msg, values, 'does not match')
        asserts.fail_unless(self._matches(string, pattern), msg)

    def should_match_regexp(self, string, pattern, msg=None, values=True):
        """Fail if 'string' does not match 'pattern' as a regular expression.

        Regular expression check is done using Python 're' module which has 
        a pattern syntax derived from Perl and thus also very similar to the 
        one in Java. See following documents from more details about regexps
        in general and Python implementation in particular.
        
        * http://docs.python.org/lib/module-re.html
        * http://www.amk.ca/python/howto/regex/

        Things to note about the regexp syntax in Robot Framework test data:

        1) Backslash is an escape character in the test data and possible backslaches 
        in the pattern must thus be escaped with another backslash (e.g. '\\\\d\\\\w+').
        
        2) Strings that may contain special characters but should be handled as
        literal strings can be escaped with 'Regexp Escape' keyword.

        3) Given pattern does not need to match the whole string. For example pattern 
        'ello' matches string 'Hello world!'. If full match is needed, '^' and '$'
        characters can be used to denote the beginning and end of the string,
        respectively. For example '^ello$' only matches exact string 'ello'.

        4) Possible flags altering how the expression is parsed (e.g. re.IGNORECASE,
        re.MULTILINE) can be set by prefixing the pattern with '(?iLmsux)' group 
        (e.g. '(?im)pattern'). Available flags are 'IGNORECASE': 'i', 'MULTILINE': 
        'm', 'DOTALL': 's', 'VERBOSE': 'x', 'UNICODE': 'u' and 'LOCALE': 'L'. 
        
        If this keyword passes, it returns the portion of the string that matched
        the pattern. Additionally possible captured groups are returned.   
        
        See 'Should Be Equal' keyword for explanation on how to override the default
        error message with 'msg' and 'values' arguments.
        
        Examples:
        | Should Match Regexp | ${output} | \\\\d{6}   | # Output contains six numbers  |
        | Should Match Regexp | ${output} | ^\\\\d{6}$ | # Six numbers and nothing more |
        | ${ret} = | Should Match Regexp | Foo: 42 | (?i)foo: \\\\d+ |
        | ${match} | ${group1} | ${group2} = |
        | ...      | Should Match Regexp | Bar: 43 | (Foo|Bar): (\\\\d+) |
        =>
        ${ret} = 'Foo: 42', 
        ${match} = 'Bar: 43'
        ${group1} = 'Bar'
        ${group2} = '43'
        """ 
        msg = self._get_string_msg(string, pattern, msg, values, 'does not match')
        res = re.search(pattern, string)
        asserts.fail_if_none(res, msg, False)
        match = res.group(0)
        groups = res.groups()
        if groups:
            return [match] + list(groups)
        return match
        
    def should_not_match_regexp(self, string, pattern, msg=None, values=True):
        """Fail if 'string' matches 'pattern' as a regular expression.
        
        See 'Should Match Regexp' for more information about arguments.
        """
        msg = self._get_string_msg(string, pattern, msg, values, 'matches')
        asserts.fail_unless_none(re.search(pattern, string), msg, False)
        
    def get_length(self, item):
        """Returns the length of the given item.
        
        The keyword first tries to get the length with Python function 'len'
        which calls item's '__len__' method internally. If that fails, the
        keyword tries to call item's 'length' and 'size' methods direcly.
        Final attempt is trying to get the value of item's 'length' attribute. 
        If all these attempts are unsuccessful the keyword fails.
        
        New in Robot 1.8.2.
        """
        try:     return len(item)
        except:  pass
        try:     return item.length()
        except:  pass
        try:     return item.size()
        except:  pass
        try:     return item.length
        except:  raise DataError("Could not get length of '%s'" % item)
        
    def length_should_be(self, item, length, msg=None):
        """Verifies that length of the given item is correct.
        
        Length of the item is got using 'Get Length' keyword. The default error
        message can be overridden with 'msg' argument.
        
        New in Robot 1.8.2.
        """
        try:
            length = int(length)
        except ValueError:
            raise DataError("Given length '%s' cannot be converted to an integer"
                             % length)
        if self.get_length(item) != length:
            if msg is None:
                msg = "Length of '%s' should be %d but it is %d" \
                        % (item, length, self.get_length(item))
            raise AssertionError(msg)
        
    def should_be_empty(self, item, msg=None):
        """Verifies that the given item is empty.
        
        Length of the item is got using 'Get Length' keyword. The default error
        message can be overridden with 'msg' argument.
        
        New in Robot 1.8.2.
        """
        if self.get_length(item) > 0:
            if msg is None:
                msg = "'%s' should be empty" % item
            raise AssertionError(msg)
        
    def should_not_be_empty(self, item, msg=None):
        """Verifies that the given item is non-empty.
        
        Length of the item is got using 'Get Length' keyword. The default error
        message can be overridden with 'msg' argument.
        
        New in Robot 1.8.2.
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

    
class Variables:
    
    def log_variables(self, level='INFO'):
        """Logs all variables in the current scope with given log level."""
        variables = self._get_variables()
        names = variables.keys()
        names.sort()
        for name in names:
            value = variables[name]
            if utils.is_list(value):
                value = '[ %s ]' % ' | '.join([utils.unic(v) for v in value ])
            else:
                value = utils.unic(value)
            self.log('%s = %s' % (name, value), level)

    def variable_should_exist(self, name, msg=None):
        """Fails unless the variable with given name exists in current scope.
        
        Variable name must be given in escaped format e.g. like \\${scalar} or
        \\@{list} to prevent it from being resolved. Alternatively, in this
        case it is possible to give the variable name in special format without
        curly braces e.g. like $scalar or @list.
        
        The default error message can be overridden with the 'msg' argument.
        """
        name = self._get_var_name(name)
        variables = self._get_variables()
        if msg is None:
            msg = "Variable %s does not exist" % name
        asserts.fail_unless(variables.has_key(name), msg)
        
    def variable_should_not_exist(self, name, msg=None):
        """Fails if the variable with given name exists in current scope.
        
        Variable name must be given in escaped format e.g. like \\${scalar} or
        \\@{list} to prevent it from being resolved. Alternatively, in this
        case it is possible to give the variable name in special format without
        curly braces e.g. like $scalar or @list.
        
        The default error message can be overridden with the 'msg' argument.
        """
        name = self._get_var_name(name)
        variables = self._get_variables()
        if msg is None:
            msg = "Variable %s exists" % name
        asserts.fail_if(variables.has_key(name), msg)


    def replace_variables(self, text):
        """Replaces variables in given text with their current values.
        
        If text contains undefined variables, this keyword fails.
        
        
        Example:
        File 'template.txt' contains 'Hello ${NAME}!' and variable '${NAME}' 
        has value 'Robot'
        
        | ${template} = | Get File | ${CURDIR}${/}template.txt} |
        | ${message} = | Replace Variables | ${template} |
        | Should Be Equal | ${message} | Hello Robot! |
        """
        return self._get_variables().replace_string(text)
    
    def set_variable(self, *args):
        """Returns given arguments -- can be used to set variables.
        
        Examples:
        | ${var} =  | Set Variable | Hello  |
        | ${var1}   | ${var2} =    | Set Variable | Hello  | world  |
        | @{list} = | Set Variable | Hi     | again  |    | # list variable   |
        | ${scal} = | Set Variable | Hi     | again  |    | # scalar variable |
        => 
        ${var} = 'Hello'
        ${var1} = 'Hello' & ${var2} = 'world'
        @{list} = ['Hi','again'] i.e. @{list}[0] = 'Hi' & @{list}[1] = 'again'
        ${scal} = ['Hi','again']
        """
        if len(args) == 0:
            return ''
        elif len(args) == 1:
            return args[0]
        else:
            return list(args)

    def set_variable_if(self, expr, value1, value2=None):
        """If 'expr' is true returns 'value1' and otherwise returns 'value2'.
        
        'expr' is evaluated as with 'Should Be True' keyword.
        
        Examples:
        | ${var1} = | Set Variable If | 1 > 0 | v1 | v2 | 
        | ${var2} = | Set Variable If | False | v1 | v2 | 
        | ${var3} = | Set Variable If | 1 > 0 and False | v1 |
        =>
        ${var1} = 'v1'  
        ${var2} = 'v2'
        ${var3} = None
        
        New in Robot 1.8.3.
        """
        if _is_true(expr):
            return value1
        return value2

    def set_test_variable(self, name, *values):
        """Makes variable available everywhere in the scope of the current test.
        
        Variables set with this keyword are available everywhere in the scope of
        the currently executed test case. For example, if you set a variable in
        a user keyword it will be available both in the test case level and also
        in all other user keywords used in the current test. Other test cases
        will not see variables set with this keyword.
        
        See 'Set Suite Variable' for more information and examples.
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self._get_variables().set_test(name, value)
        self._log_set_variable(name, value)
        
    def set_suite_variable(self, name, *values):
        """Makes variable available everywhere in the scope of the current suite.
        
        Variables set with this keyword are available everywhere in the scope of
        the currently executed test suite. Setting variables with this keyword
        thus has the same effect as creating them using Variable table in the
        test data file or importing them from variable files. Other test suites
        will not see variables set with this keyword.
        
        Variable name must be given either in escaped format (e.g. \\${scalar}
        or \\@{list}) or without curly braces (e.g. $scalar or @list) to prevent
        it from being resolved.
        
        If variable already exist in the new scope its value will be overwritten
        and otherwise a new variable is created. If variable already exists in
        the current scope the value can be left empty and variable in the new
        scope gets the value in the current scope.

        Examples:
        | Set Suite Variable | $GREET  | Hello, world! |        
        | ${ID} = | Get ID |
        | Set Suite Variable | \\${ID} |
         """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self._get_variables().set_suite(name, value)
        self._log_set_variable(name, value)
        
    def set_global_variable(self, name, *values):
        """Makes variable available globally in all tests and suites.
        
        Variables set with this keyword are globally available in all test cases
        and suites executed after setting it. Setting variables with this
        keyword thus has the same effect as creating from using command line 
        options --variable or --variablefile. Because this keyword can change
        variables everywhere it should be used with care.
        
        See 'Set Suite Variable' for more information and examples.
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self._get_variables().set_global(name, value)
        self._log_set_variable(name, value)
    
    # Helpers
    
    def _get_variables(self):
        return NAMESPACES.current.variables
        
    def _get_var_name(self, name):
        if is_var(name):
            return name
        if utils.is_str(name) and name != '' and name[0] in ['$','@']:
            newname = name[0] + '{' + name[1:] + '}'
            if is_var(newname):
                return newname
        raise DataError("Invalid variable syntax '%s'" % name)
        
    def _get_var_value(self, name, values):
        if len(values) == 0:
            variables = self._get_variables()
            return variables[name]
        elif len(values) == 1 and name[0] == '$':
            return values[0]
        else:
            return list(values)

    def _log_set_variable(self, name, value):
        if is_list_var(name):
            value = '[ %s ]' % ' | '.join([utils.unic(v) for v in value ])
        else:
            value = utils.unic(value)
        self.log('%s = %s' % (name, utils.cut_long_assign_msg(value)))


class RunKeyword:
    
    def run_keyword(self, name, *args):
        """Executes the given keyword with given arguments.
        
        Because the name of the keyword to execute is given as an argument, it
        can be a variable and thus set dynamically e.g. from a return value of
        another keyword or from command line.
        """
        kw = Keyword(name, [ utils.escape(arg) for arg in args ])
        return kw.run(output.OUTPUT, NAMESPACES.current)
    
    def run_keyword_if(self, expr, name, *args):
        """Runs given keyword with given arguments if 'expr' is true.
        
        'expr' is evaluated same way as with 'Should Be True' keyword.
        
        Example, simple if/else construct:
        | ${status} | ${value} = | Run Keyword And Ignore Error | My Keyword |
        | Run Keyword If     | '${status}' == 'PASS' | Some Action    |
        | Run Keyword Unless | '${status}' == 'PASS' | Another Action |
        
        In this example, only either 'Some Action' or 'Another Action' is
        executed, based on the status of 'My Keyword'.
        
        New in Robot 1.8.3.
        """
        if _is_true(expr):
            return self.run_keyword(name, *args)
    
    def run_keyword_unless(self, expr, name, *args):
        """Runs given keyword with given arguments if 'expr' is false.

        See 'Run Keyword If' for more information and an example.
        
        New in Robot 1.8.3.
        """
        if not _is_true(expr):
            return self.run_keyword(name, *args)
    
    def run_keyword_and_ignore_error(self, name, *args):
        """Runs given keyword with given arguments and ignores possible error.
        
        This keyword returns two values so that the first is either 'PASS' or
        'FAIL' depending on the status of the executed keyword. The second value
        is either the return value of the keyword or received error message.
        
        Keyword name and arguments work as in 'Run Keyword'.
        
        See 'Run Keyword If' for a usage example.
        
        Note: In versions prior to Robot 1.8.3, this keyword only returns the
        return value or error message of the executed keyword.
        """
        try:
            return 'PASS', self.run_keyword(name, *args)
        except:
            return 'FAIL', utils.get_error_message()
    
    def run_keyword_and_expect_error(self, expected_error, name, *args):
        """Runs keyword and checks that the expected error occurred.
        
        The expected error must be given in the same format as in Robot reports. 
        It can be a pattern containing characters '?' which matches to any 
        single character and '*' which matches to any number of any characters.
        
        If the expected error occurs, the error message is returned and it can
        be further processed/tested if needed. If there is no error, or the 
        error does not match to the expected error, this keyword fails.
        
        Examples:
        | Run Keyword And Expect Error | My error | Some Keyword | arg1 | arg2 |
        | ${msg} = | Run Keyword And Expect Error | * | My KW | 
        | Should Start With | ${msg} | Once upon a time in | 
        """
        try:
            self.run_keyword(name, *args)
        except:
            error = utils.get_error_message()
        else:
            raise AssertionError("Expected error '%s' did not occur" % expected_error)
        if not self._matches(error, expected_error):
            raise AssertionError("Expected error '%s' but got '%s'" 
                                 % (expected_error, error))
        return error

    def wait_until_keyword_succeeds(self, timeout, retry_interval, name, *args):
        """Waits until the specified keyword succeeds or given timeout expires.
        
        'name' and 'args' define the keyword that is executed. If the specified 
        keyword does not succeed within 'timeout', this keyword fails.        
        'retry_interval' is the time to wait before trying to run the keyword
        again after the previous run has failed. 
        
        Both 'timeout' and 'retry_interval' must be given in Robot's time 
        format (e.g. '1 minute', '2 min 3 s', '4.5').
        
        Example:
        | Wait Until Keyword Succeeds | 2 min | 5 sec | My keyword | arg1 | arg2 |
        
        New in Robot 1.8.1.
        """
        timeout = utils.timestr_to_secs(timeout)
        retry_interval = utils.timestr_to_secs(retry_interval)
        starttime = _time.time()
        while _time.time() - starttime < timeout:
            try:
                return self.run_keyword(name, *args)
            except:
                _time.sleep(retry_interval)
        raise Exception("Timeout %s exceeded" % utils.secs_to_timestr(timeout))
    
    def run_keyword_if_test_failed(self, name, *args):
        """Runs given keyword with given arguments if test failed.
        
        This keyword can only be used in test teardown. Trying to use it in any
        other place will result in an error.
        
        Otherwise, this keyword works exactly like 'Run Keyword', see its 
        documentation for more details. 
        """
        test = self._get_test_in_teardown('Run Keyword If Test Failed')
        if test.status == 'FAIL':
            return self.run_keyword(name, *args)
        
    def run_keyword_if_test_passed(self, name, *args):
        """Runs given keyword with given arguments if test passed.
        
        This keyword can only be used in test teardown. Trying to use it in any
        other place will result in an error.
        
        Otherwise, this keyword works exactly like 'Run Keyword', see its 
        documentation for more details. 
        """
        test = self._get_test_in_teardown('Run Keyword If Test Passed')
        if test.status == 'PASS':
            return self.run_keyword(name, *args)
        
    def _get_test_in_teardown(self, kwname):
        test = NAMESPACES.current.test
        if test is not None and test.state == 'TEARDOWN':
            return test
        raise DataError("Keyword '%s' can only be used in test teardown" 
                        % kwname)
        
    def run_keyword_if_all_critical_tests_passed(self, name, *args):
        """Runs given keyword with given arguments if all critical tests passed.
        
        This keyword can only be used in suite teardown. Trying to use it in any
        other place will result in an error.
        
        Otherwise, this keyword works exactly like 'Run Keyword', see its 
        documentation for more details. 
        """
        kwname = 'Run Keyword If All Critical Tests Passed'
        suite = self._get_suite_in_teardown(kwname)
        if suite.critical_stats.failed == 0:
            return self.run_keyword(name, *args)
        
    def run_keyword_if_any_critical_tests_failed(self, name, *args):
        """Runs given keyword with given arguments if any critical tests failed.
        
        This keyword can only be used in suite teardown. Trying to use it in any
        other place will result in an error.
        
        Otherwise, this keyword works exactly like 'Run Keyword', see its 
        documentation for more details. 
        """
        kwname = 'Run Keyword If Any Critical Tests Failed'
        suite = self._get_suite_in_teardown(kwname)
        if suite.critical_stats.failed > 0:
            return self.run_keyword(name, *args)
        
    def run_keyword_if_all_tests_passed(self, name, *args):
        """Runs given keyword with given arguments if all tests passed.
        
        This keyword can only be used in suite teardown. Trying to use it in any
        other place will result in an error.
        
        Otherwise, this keyword works exactly like 'Run Keyword', see its 
        documentation for more details. 
        """
        suite = self._get_suite_in_teardown('Run Keyword If All Tests Passed')
        if suite.all_stats.failed == 0:
            return self.run_keyword(name, *args)
            
    def run_keyword_if_any_tests_failed(self, name, *args):
        """Runs given keyword with given arguments if one or more tests failed.
        
        This keyword can only be used in suite teardown. Trying to use it in any
        other place will result in an error.
        
        Otherwise, this keyword works exactly like 'Run Keyword', see its 
        documentation for more details.
        """
        suite = self._get_suite_in_teardown('Run Keyword If Any Tests Failed')
        if suite.all_stats.failed > 0:
            return self.run_keyword(name, *args)

    def _get_suite_in_teardown(self, kwname):
        suite = NAMESPACES.current.suite
        if suite.state == 'TEARDOWN':
            return suite
        raise DataError("Keyword '%s' can only be used in suite teardown" 
                        % kwname)


class Misc:
    
    def no_operation(self):
        """No operation."""

    def sleep(self, time):
        """Sleeps the given time.
        
        'time' may be either a number or a time string. Time strings are in
        format like '1day 2h 3min 4s 5ms'. See Robot documentation 'TimeSyntax'
        for complete details on time strings. 
        """
        # TODO: Better link to TimeSyntax
        seconds = utils.timestr_to_secs(time)
        _time.sleep(seconds)
        self.log('Slept %s' % utils.secs_to_timestr(seconds))

    def catenate(self, *items):
        """Catenates given items together and returns the resulted string.
        
        By default items are catenated with spaces but if the first item 
        contains string 'SEPARATOR=<sep>' the separator '<sep>' is used. Items
        are converted into strings when necessary.
        
        Examples:
        | ${str1} = | Catenate | Hello       | world  |        |
        | ${str2} = | Catenate | SEPARATOR=- | Hello  | world  |
        | ${str3} = | Catenate | SEPARATOR=  | Hello  | world  |
        =>
        ${str1} = 'Hello world'
        ${str2} = 'Hello-world'
        ${str3} = 'Helloworld'
        """
        if len(items) == 0:
            return u''
        items = [ utils.unic(item) for item in items ]
        if items[0].startswith('SEPARATOR='):
            sep = items[0][len('SEPARATOR='):]
            items = items[1:]
        else:
            sep = u' '
        return sep.join(items)

    def log(self, message, level="INFO"):
        """Logs given message with given level"""
        level = level.upper()
        if not output.LEVELS.has_key(level):
            raise DataError("Invalid log level '%s'" % level)
        print '*%s* %s' % (level, message)

    def log_many(self, *messages):
        """Logs given messages as separate entries with info level"""
        for msg in messages:
            self.log(msg)

    def set_log_level(self, level):
        """Sets log threshold to specified level and returns the old level.
        
        Messages below the level will not logged. The default logging level is
        INFO but it can be overridden with command line option '--loglevel'.
        
        Available levels: TRACE, DEBUG, INFO (default), WARN and NONE (no logging).
        """
        old = output.OUTPUT.set_level(level)
        self.log('Log level changed from %s to %s' % (old, level.upper()))
        return old
        
    def comment(self, *messages):
        """Displays given messages in log file as keyword arguments.
        
        This keyword does nothing with the arguments it receives but as they
        are visible in the log this keyword can be used to display simple
        messages. In more complicated cases Log or Log Many keywords should be
        used.
        """
        pass

    def syslog(self, message, level="INFO"):
        """Logs given message with givel level to Robot's syslog"""
        output.SYSLOG.write(message, level)
        
    def import_library(self, name, *args):
        """Imports library with given name and optional arguments.
        
        This functionality allows dynamic importing of libraries while tests
        are running. That may be necessary if the library itself is dynamic
        and not yet available when test data is processed. In a normal case
        libraries should be imported using Library setting in Setting Table.
        """
        NAMESPACES.current.import_library(name, args)
        
    def import_variables(self, path, *args):
        """Imports variable file with given path and optional arguments.
        
        Variables imported with this keyword are set into the test suite scope
        similarly when importing them in Setting Table using Variables setting.
        These variables override possible existing variables with same names
        and this functionality can thus be used to import new variables e.g.
        for each test in a test suite.
        
        The given path must be absolute and path separators ('/' or '\\') must
        be set correctly. This is often easiest done using built-in variables 
        '${CURDIR}' and '${/}' as shown in examples below.
        
        | Import Variables | ${CURDIR}${/}variables.py         |      |      |
        | Import Variables | ${CURDIR}${/}..${/}vars${/}env.py | arg1 | arg2 |
        """
        NAMESPACES.current.import_variables(path, args, overwrite=True)
        
    def get_time(self, format='timestamp'):
        """Return the current time in requested format. 
        
        How time is returned is deternined based on the given 'format' string
        as follows. Note that all checks are case insensitive.
        
        - If 'format' contains word 'epoch' the time is returned in seconds 
          after the unix epoch. Return value is always an integer.
        - If 'format' contains any of the words 'year', 'month', 'day', 'hour',
          'min' or 'sec' only selected parts are returned. The order of the
          returned parts is always the one in previous sentence and order of
          words in 'format' is not significant. Parts are returned as zero
          padded strings (e.g. May -> '05').
        - Otherwise (and by default) the time is returned as a timestamp string 
          in format '2006-02-24 15:08:31'
        
        Examples (expecting current time is 2006-03-29 15:06:21):
        | ${time} = | Get Time |             |  |  |
        | ${secs} = | Get Time | epoch       |  |  |
        | ${year} = | Get Time | return year |  |  |
        | ${yyyy}   | ${mm}    | ${dd} =     | Get Time | year,month,day |
        | @{time} = | Get Time | year,month,day,hour,min,sec |  |  |
        | ${y}      | ${s} =   | Get Time    | seconds and year |  |
        => 
        ${time} = '2006-03-29 15:06:21'
        ${secs} = 1143637581
        ${year} = '2006'
        ${yyyy} = '2006', ${mm} = '03', ${dd} = '29'
        @{time} = [ '2006', '03', '29', '15', '06', '21' ]
        ${y} = '2006'
        ${s} = '21'
        """
        return utils.get_time(format)

    def evaluate(self, expression):
        """Evaluates the given expression in Python and return results.
        
        Examples (expecting ${RC} is -1):
        | ${status} = | Evaluate | 0 < ${RC} < 10          |
        | ${dict} =   | Evaluate | { 'a':1, 'b':2, 'c':3 } |
        =>
        ${status} = False
        ${dict} = { 'a':1, 'b':2, 'c':3 }
        """
        try:
            return eval(expression)
        except Exception, err:
            raise Exception("Evaluating expression '%s' failed. Error: %s" 
                            % (expression, err))
        
    def call_method(self, object, method_name, *args):
        """Calls named method of the given object with provided arguments.
        
        Possible return value from the method is returned and can be assigned
        to a variable. Keyword fails both if the object does not have a method
        with the given name or if executing the method raises an exception.
        
        Examples:
        | Call Method        | ${hashtable} | put          | myname  | myvalue |
        | ${isempty} =       | Call Method  | ${hashtable} | isEmpty |         |
        | Should Not Be True | ${isempty}   |              |         |         |
        | ${value} =         | Call Method  | ${hashtable} | get     | myname  |
        | Should Be Equal    | ${value}     | myvalue      |         |         |        
        """
        try:
            method = getattr(object, method_name)
        except AttributeError:
            raise Exception("Object '%s' does not have a method '%s'" 
                            % (object, method_name))
        return method(*args)

    def grep(self, text, pattern, pattern_type='literal string'):
        """Returns the text grepped using 'pattern'.
        
        'pattern_type' defines how the given pattern is interpreted as explained
        below. It is case insensitive and may contain other text. For example
        'regexp', 'REGEXP' and 'Pattern is a regexp' are all considered equal.
        
        - If 'pattern_type' contains either string 'simple' or 'glob' the 
          'pattern' is considered a simple pattern and lines returned only if 
          they match it. (1) 
        - If 'pattern_type' contains either string 'regular expression' or
          'regexp' the 'pattern' is considered a regular expression and only 
          lines matching it returned. (2)
        - If 'pattern_type' contains string 'case insensitive' the 'pattern' is 
          considered a literal string and lines returned if they contain the 
          string regardless of the case.
        - Otherwise the pattern is considered a literal string and lines
          returned if they contain the string exactly. This is the default.
        
        1) Simple pattern matching is similar as matching files in a shell and 
        it is always case-sensitive. In the pattern '*' matches to anything 
        and '?' matches to any single character.  
        
        2) Regular expression check is done using Python 're' module which has 
        a pattern syntax derived from Perl and thus also very similar to the 
        one in Java. See following documents from more details about regexps
        in general and their Python implementation in particular.
        
        're' Module Documentation: http://docs.python.org/lib/module-re.html
        Regular Expression HOWTO: http://www.amk.ca/python/howto/regex/
        
        Note that if you want to use flags (e.g. re.IGNORECASE) you have to
        embed them into the pattern (e.g. '(?i)pattern'). Note also that 
        backslash is an escape character in Robot test data and possible
        backslaches in patterns must thus be escaped with another backslash
        (e.g. '\\\\d\\\\w+').
        """
        if pattern == '':
            return text
        lines = text.splitlines()
        if utils.contains_any(pattern_type, ['simple','glob']):
            lines = [ line for line in lines if self._matches(line, pattern) ]
        elif utils.contains_any(pattern_type, ['regular expression','regexp']):
            grep = re.compile(pattern)
            lines = [ line for line in lines if grep.search(line) is not None ]
        elif utils.contains(pattern_type, 'case insensitive'):
            pattern = pattern.lower()
            lines = [ line for line in lines if line.lower().count(pattern) > 0 ]
        else:
            lines = [ line for line in lines if line.count(pattern) > 0 ]
        return '\n'.join(lines)
    
    def regexp_escape(self, *patterns):
        """Returns each argument string escaped for use as regular expression.
        
        This keyword can be used to escape strings to be used with 'Should
        Match Regexp' and 'Should Not Match Regexp' keywords.
        
        Escaping is done with Python's re.escape() function.
        
        Examples:
        | ${escaped} = | Regexp Escape | ${original} |
        | @{strings} = | Regexp Escape | @{strings}  |
        
        New in Robot 1.8.3.
        """
        if len(patterns) == 0:
            return ''
        if len(patterns) == 1:
            return re.escape(patterns[0])
        return [ re.escape(pattern) for pattern in patterns ]


 # TODO: Rename 'Verify' -> '_Verify', etc. because helper classes aren't part
 # of our public API.
 
class BuiltIn(Verify, Converter, Variables, RunKeyword, Misc):
    """BuiltIn library provides a set of often needed generic keywords.

    These keywords are available automatically without importing any library.
    They allow functionality for verifying different things (e.g. Should Be 
    Equal), conversions (e.g. Convert To Integer) and for many miscellaneous 
    things (e.g. Sleep).
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def _matches(self, string, pattern):
        return utils.matches(string, pattern, caseless=False, spaceless=False)
