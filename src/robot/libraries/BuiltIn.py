#  Copyright 2008-2015 Nokia Solutions and Networks
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

import __builtin__
import re
import time

from robot.api import logger
from robot.errors import (ContinueForLoop, DataError, ExecutionFailed,
                          ExecutionFailures, ExecutionPassed, ExitForLoop,
                          PassExecution, ReturnFromKeyword)
from robot.running import Keyword, RUN_KW_REGISTER
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.usererrorhandler import UserErrorHandler
from robot.utils import (asserts, DotDict, escape, format_assign_message,
                         get_error_message, get_time, is_falsy, is_truthy,
                         JYTHON, Matcher, normalize, parse_time, prepr,
                         RERAISED_EXCEPTIONS, plural_or_not as s,
                         secs_to_timestr, seq2str, split_from_equals,
                         timestr_to_secs, type_name, unic)
from robot.variables import (is_list_var, is_var, DictVariableTableValue,
                             VariableTableValue, VariableSplitter)
from robot.version import get_version

if JYTHON:
    from java.lang import String, Number


# TODO: The name of this decorator should be changed. It is used for avoiding
# arguments to be resolved by many other keywords than run keyword variants.
# Should also consider:
# - Exposing this functionality to external libraries. Would require doc
#   enhancements and clean way to expose variables to make resolving them
#   based on needs easier.
# - Removing the functionality that run keyword variants can be overridded
#   by custom keywords without a warning.

def run_keyword_variant(resolve):
    def decorator(method):
        RUN_KW_REGISTER.register_run_keyword('BuiltIn', method.__name__, resolve)
        return method
    return decorator


class _BuiltInBase(object):

    @property
    def _context(self):
        if EXECUTION_CONTEXTS.current is None:
            raise RobotNotRunningError('Cannot access execution context')
        return EXECUTION_CONTEXTS.current

    @property
    def _namespace(self):
        return self._context.namespace

    def _get_namespace(self, top=False):
        ctx = EXECUTION_CONTEXTS.top if top else EXECUTION_CONTEXTS.current
        return ctx.namespace

    @property
    def _variables(self):
        return self._namespace.variables

    def _matches(self, string, pattern):
        # Must use this instead of fnmatch when string may contain newlines.
        matcher = Matcher(pattern, caseless=False, spaceless=False)
        return matcher.match(string)

    def _is_true(self, condition):
        if isinstance(condition, basestring):
            condition = self.evaluate(condition, modules='os,sys')
        return bool(condition)

    def _log_types(self, *args):
        msg = ["Argument types are:"] + [self._get_type(a) for a in args]
        self.log('\n'.join(msg), 'DEBUG')

    def _get_type(self, arg):
        # In IronPython type(u'x') is str. We want to report unicode anyway.
        if isinstance(arg, unicode):
            return "<type 'unicode'>"
        return str(type(arg))


class _Converter(_BuiltInBase):

    def convert_to_integer(self, item, base=None):
        """Converts the given item to an integer number.

        If the given item is a string, it is by default expected to be an
        integer in base 10. There are two ways to convert from other bases:

        - Give base explicitly to the keyword as ``base`` argument.

        - Prefix the given string with the base so that ``0b`` means binary
          (base 2), ``0o`` means octal (base 8), and ``0x`` means hex (base 16).
          The prefix is considered only when ``base`` argument is not given and
          may itself be prefixed with a plus or minus sign.

        The syntax is case-insensitive and possible spaces are ignored.

        Examples:
        | ${result} = | Convert To Integer | 100    |    | # Result is 100   |
        | ${result} = | Convert To Integer | FF AA  | 16 | # Result is 65450 |
        | ${result} = | Convert To Integer | 100    | 8  | # Result is 64    |
        | ${result} = | Convert To Integer | -100   | 2  | # Result is -4    |
        | ${result} = | Convert To Integer | 0b100  |    | # Result is 4     |
        | ${result} = | Convert To Integer | -0x100 |    | # Result is -256  |

        See also `Convert To Number`, `Convert To Binary`, `Convert To Octal`,
        `Convert To Hex`, and `Convert To Bytes`.
        """
        self._log_types(item)
        return self._convert_to_integer(item, base)

    def _convert_to_integer(self, orig, base=None):
        try:
            item = self._handle_java_numbers(orig)
            item, base = self._get_base(item, base)
            if base:
                return int(item, self._convert_to_integer(base))
            return int(item)
        except:
            raise RuntimeError("'%s' cannot be converted to an integer: %s"
                               % (orig, get_error_message()))

    def _handle_java_numbers(self, item):
        if not JYTHON:
            return item
        if isinstance(item, String):
            return unic(item)
        if isinstance(item, Number):
            return item.doubleValue()
        return item

    def _get_base(self, item, base):
        if not isinstance(item, basestring):
            return item, base
        item = normalize(item)
        if item.startswith(('-', '+')):
            sign = item[0]
            item = item[1:]
        else:
            sign = ''
        bases = {'0b': 2, '0o': 8, '0x': 16}
        if base or not item.startswith(tuple(bases)):
            return sign+item, base
        return sign+item[2:], bases[item[:2]]

    def convert_to_binary(self, item, base=None, prefix=None, length=None):
        """Converts the given item to a binary string.

        The ``item``, with an optional ``base``, is first converted to an
        integer using `Convert To Integer` internally. After that it
        is converted to a binary number (base 2) represented as a
        string such as ``1011``.

        The returned value can contain an optional ``prefix`` and can be
        required to be of minimum ``length`` (excluding the prefix and a
        possible minus sign). If the value is initially shorter than
        the required length, it is padded with zeros.

        Examples:
        | ${result} = | Convert To Binary | 10 |         |           | # Result is 1010   |
        | ${result} = | Convert To Binary | F  | base=16 | prefix=0b | # Result is 0b1111 |
        | ${result} = | Convert To Binary | -2 | prefix=B | length=4 | # Result is -B0010 |

        See also `Convert To Integer`, `Convert To Octal` and `Convert To Hex`.
        """
        return self._convert_to_bin_oct_hex(bin, item, base, prefix, length)

    def convert_to_octal(self, item, base=None, prefix=None, length=None):
        """Converts the given item to an octal string.

        The ``item``, with an optional ``base``, is first converted to an
        integer using `Convert To Integer` internally. After that it
        is converted to an octal number (base 8) represented as a
        string such as ``775``.

        The returned value can contain an optional ``prefix`` and can be
        required to be of minimum ``length`` (excluding the prefix and a
        possible minus sign). If the value is initially shorter than
        the required length, it is padded with zeros.

        Examples:
        | ${result} = | Convert To Octal | 10 |            |          | # Result is 12      |
        | ${result} = | Convert To Octal | -F | base=16    | prefix=0 | # Result is -017    |
        | ${result} = | Convert To Octal | 16 | prefix=oct | length=4 | # Result is oct0020 |

        See also `Convert To Integer`, `Convert To Binary` and `Convert To Hex`.
        """
        return self._convert_to_bin_oct_hex(oct, item, base, prefix, length)

    def convert_to_hex(self, item, base=None, prefix=None, length=None,
                       lowercase=False):
        """Converts the given item to a hexadecimal string.

        The ``item``, with an optional ``base``, is first converted to an
        integer using `Convert To Integer` internally. After that it
        is converted to a hexadecimal number (base 16) represented as
        a string such as ``FF0A``.

        The returned value can contain an optional ``prefix`` and can be
        required to be of minimum ``length`` (excluding the prefix and a
        possible minus sign). If the value is initially shorter than
        the required length, it is padded with zeros.

        By default the value is returned as an upper case string, but the
        ``lowercase`` argument a true value (see `Boolean arguments`) turns
        the value (but not the given prefix) to lower case.

        Examples:
        | ${result} = | Convert To Hex | 255 |           |              | # Result is FF    |
        | ${result} = | Convert To Hex | -10 | prefix=0x | length=2     | # Result is -0x0A |
        | ${result} = | Convert To Hex | 255 | prefix=X | lowercase=yes | # Result is Xff   |

        See also `Convert To Integer`, `Convert To Binary` and `Convert To Octal`.
        """
        return self._convert_to_bin_oct_hex(hex, item, base, prefix, length,
                                            lowercase)

    def _convert_to_bin_oct_hex(self, method, item, base, prefix, length,
                                lowercase=False):
        self._log_types(item)
        ret = method(self._convert_to_integer(item, base)).upper().rstrip('L')
        prefix = prefix or ''
        if ret[0] == '-':
            prefix = '-' + prefix
            ret = ret[1:]
        if len(ret) > 1:  # oct(0) -> '0' (i.e. has no prefix)
            prefix_length = {bin: 2, oct: 1, hex: 2}[method]
            ret = ret[prefix_length:]
        if length:
            ret = ret.rjust(self._convert_to_integer(length), '0')
        if is_truthy(lowercase):
            ret = ret.lower()
        return prefix + ret

    def convert_to_number(self, item, precision=None):
        """Converts the given item to a floating point number.

        If the optional ``precision`` is positive or zero, the returned number
        is rounded to that number of decimal digits. Negative precision means
        that the number is rounded to the closest multiple of 10 to the power
        of the absolute precision.

        Examples:
        | ${result} = | Convert To Number | 42.512 |    | # Result is 42.512 |
        | ${result} = | Convert To Number | 42.512 | 1  | # Result is 42.5   |
        | ${result} = | Convert To Number | 42.512 | 0  | # Result is 43.0   |
        | ${result} = | Convert To Number | 42.512 | -1 | # Result is 40.0   |

        Notice that machines generally cannot store floating point numbers
        accurately. This may cause surprises with these numbers in general
        and also when they are rounded. For more information see, for example,
        these resources:

        - http://docs.python.org/2/tutorial/floatingpoint.html
        - http://randomascii.wordpress.com/2012/02/25/comparing-floating-point-numbers-2012-edition

        If you need an integer number, use `Convert To Integer` instead.
        """
        self._log_types(item)
        return self._convert_to_number(item, precision)

    def _convert_to_number(self, item, precision=None):
        number = self._convert_to_number_without_precision(item)
        if precision:
            number = round(number, self._convert_to_integer(precision))
        return number

    def _convert_to_number_without_precision(self, item):
        try:
            if JYTHON:
                item = self._handle_java_numbers(item)
            return float(item)
        except:
            error = get_error_message()
            try:
                return float(self._convert_to_integer(item))
            except RuntimeError:
                raise RuntimeError("'%s' cannot be converted to a floating "
                                   "point number: %s" % (item, error))

    def convert_to_string(self, item):
        """Converts the given item to a Unicode string.

        Uses ``__unicode__`` or ``__str__`` method with Python objects and
        ``toString`` with Java objects.

        Use `Encode String To Bytes` and `Decode Bytes To String` keywords
        in ``String`` library if you need to convert between Unicode and byte
        strings using different encodings. Use `Convert To Bytes` if you just
        want to create byte strings.
        """
        self._log_types(item)
        return self._convert_to_string(item)

    def _convert_to_string(self, item):
        return unic(item)

    def convert_to_boolean(self, item):
        """Converts the given item to Boolean true or false.

        Handles strings ``True`` and ``False`` (case-insensitive) as expected,
        otherwise returns item's
        [http://docs.python.org/2/library/stdtypes.html#truth|truth value]
        using Python's ``bool()`` method.
        """
        self._log_types(item)
        if isinstance(item, basestring):
            if item.upper() == 'TRUE':
                return True
            if item.upper() == 'FALSE':
                return False
        return bool(item)

    def convert_to_bytes(self, input, input_type='text'):
        u"""Converts the given ``input`` to bytes according to the ``input_type``.

        Valid input types are listed below:

        - ``text:`` Converts text to bytes character by character. All
          characters with ordinal below 256 can be used and are converted to
          bytes with same values. Many characters are easiest to represent
          using escapes like ``\\x00`` or ``\\xff``.

        - ``int:`` Converts integers separated by spaces to bytes. Similarly as
          with `Convert To Integer`, it is possible to use binary, octal, or
          hex values by prefixing the values with ``0b``, ``0o``, or ``0x``,
          respectively.

        - ``hex:`` Converts hexadecimal values to bytes. Single byte is always
          two characters long (e.g. ``01`` or ``FF``). Spaces are ignored and
          can be used freely as a visual separator.

        - ``bin:`` Converts binary values to bytes. Single byte is always eight
          characters long (e.g. ``00001010``). Spaces are ignored and can be
          used freely as a visual separator.

        In addition to giving the input as a string, it is possible to use
        lists or other iterables containing individual characters or numbers.
        In that case numbers do not need to be padded to certain length and
        they cannot contain extra spaces.

        Examples (last column shows returned bytes):
        | ${bytes} = | Convert To Bytes | hyv\xe4    |     | # hyv\\xe4        |
        | ${bytes} = | Convert To Bytes | \\xff\\x07 |     | # \\xff\\x07      |
        | ${bytes} = | Convert To Bytes | 82 70      | int | # RF              |
        | ${bytes} = | Convert To Bytes | 0b10 0x10  | int | # \\x02\\x10      |
        | ${bytes} = | Convert To Bytes | ff 00 07   | hex | # \\xff\\x00\\x07 |
        | ${bytes} = | Convert To Bytes | 5246212121 | hex | # RF!!!           |
        | ${bytes} = | Convert To Bytes | 0000 1000  | bin | # \\x08           |
        | ${input} = | Create List      | 1          | 2   | 12                |
        | ${bytes} = | Convert To Bytes | ${input}   | int | # \\x01\\x02\\x0c |
        | ${bytes} = | Convert To Bytes | ${input}   | hex | # \\x01\\x02\\x12 |

        Use `Encode String To Bytes` in ``String`` library if you need to
        convert text to bytes using a certain encoding.

        New in Robot Framework 2.8.2.
        """
        try:
            try:
                ordinals = getattr(self, '_get_ordinals_from_%s' % input_type)
            except AttributeError:
                raise RuntimeError("Invalid input type '%s'." % input_type)
            return ''.join(chr(o) for o in ordinals(input))
        except:
            raise RuntimeError("Creating bytes failed: %s" % get_error_message())

    def _get_ordinals_from_text(self, input):
        for char in input:
            yield self._test_ordinal(ord(char), char, 'Character')

    def _test_ordinal(self, ordinal, original, type):
        if 0 <= ordinal <= 255:
            return ordinal
        raise RuntimeError("%s '%s' cannot be represented as a byte."
                           % (type, original))

    def _get_ordinals_from_int(self, input):
        if isinstance(input, basestring):
            input = input.split()
        elif isinstance(input, (int, long)):
            input = [input]
        for integer in input:
            ordinal = self._convert_to_integer(integer)
            yield self._test_ordinal(ordinal, integer, 'Integer')

    def _get_ordinals_from_hex(self, input):
        for token in self._input_to_tokens(input, length=2):
            ordinal = self._convert_to_integer(token, base=16)
            yield self._test_ordinal(ordinal, token, 'Hex value')

    def _get_ordinals_from_bin(self, input):
        for token in self._input_to_tokens(input, length=8):
            ordinal = self._convert_to_integer(token, base=2)
            yield self._test_ordinal(ordinal, token, 'Binary value')

    def _input_to_tokens(self, input, length):
        if not isinstance(input, basestring):
            return input
        input = ''.join(input.split())
        if len(input) % length != 0:
            raise RuntimeError('Expected input to be multiple of %d.' % length)
        return (input[i:i+length] for i in xrange(0, len(input), length))

    def create_list(self, *items):
        """Returns a list containing given items.

        The returned list can be assigned both to ``${scalar}`` and ``@{list}``
        variables.

        Examples:
        | @{list} =   | Create List | a    | b    | c    |
        | ${scalar} = | Create List | a    | b    | c    |
        | ${ints} =   | Create List | ${1} | ${2} | ${3} |
        """
        return list(items)

    @run_keyword_variant(resolve=0)
    def create_dictionary(self, *items):
        """Creates and returns a dictionary based on given items.

        Items are given using ``key=value`` syntax same way as ``&{dictionary}``
        variables are created in the Variable table. Both keys and values
        can contain variables, and possible equal sign in key can be escaped
        with a backslash like ``escaped\\=key=value``. It is also possible to
        get items from existing dictionaries by simply using them like
        ``&{dict}``.

        If same key is used multiple times, the last value has precedence.
        The returned dictionary is ordered, and values with strings as keys
        can also be accessed using convenient dot-access syntax like
        ``${dict.key}``.

        Examples:
        | &{dict} = | Create Dictionary | key=value | foo=bar |
        | Should Be True | ${dict} == {'key': 'value', 'foo': 'bar'} |
        | &{dict} = | Create Dictionary | ${1}=${2} | &{dict} | foo=new |
        | Should Be True | ${dict} == {1: 2, 'key': 'value', 'foo': 'new'} |
        | Should Be Equal | ${dict.key} | value |

        This keyword was changed in Robot Framework 2.9 in many ways:
        - Moved from ``Collections`` library to ``BuiltIn``.
        - Support also non-string keys in ``key=value`` syntax.
        - Deprecated old syntax to give keys and values separately.
        - Returned dictionary is ordered and dot-accessible.
        """
        separate, combined = self._split_dict_items(items)
        if separate:
            self.log("Giving keys and values separately to 'Create Dictionary' "
                     "keyword is deprecated. Use 'key=value' syntax instead.",
                     level='WARN')
        separate = self._format_separate_dict_items(separate)
        combined = DictVariableTableValue(combined).resolve(self._variables)
        result = DotDict(separate)
        result.update(combined)
        return result

    def _split_dict_items(self, items):
        separate = []
        for item in items:
            name, value = split_from_equals(item)
            if value is not None or VariableSplitter(item).is_dict_variable():
                break
            separate.append(item)
        return separate, items[len(separate):]

    def _format_separate_dict_items(self, separate):
        separate = self._variables.replace_list(separate)
        if len(separate) % 2 != 0:
            raise DataError('Expected even number of keys and values, got %d.'
                            % len(separate))
        return [separate[i:i+2] for i in range(0, len(separate), 2)]


class _Verify(_BuiltInBase):

    def _set_and_remove_tags(self, tags):
        set_tags = [tag for tag in tags if not tag.startswith('-')]
        remove_tags = [tag[1:] for tag in tags if tag.startswith('-')]
        if remove_tags:
            self.remove_tags(*remove_tags)
        if set_tags:
            self.set_tags(*set_tags)

    def fail(self, msg=None, *tags):
        """Fails the test with the given message and optionally alters its tags.

        The error message is specified using the ``msg`` argument.
        It is possible to use HTML in the given error message, similarly
        as with any other keyword accepting an error message, by prefixing
        the error with ``*HTML*``.

        It is possible to modify tags of the current test case by passing tags
        after the message. Tags starting with a hyphen (e.g. ``-regression``)
        are removed and others added. Tags are modified using `Set Tags` and
        `Remove Tags` internally, and the semantics setting and removing them
        are the same as with these keywords.

        Examples:
        | Fail | Test not ready   |             | | # Fails with the given message.    |
        | Fail | *HTML*<b>Test not ready</b> | | | # Fails using HTML in the message. |
        | Fail | Test not ready   | not-ready   | | # Fails and adds 'not-ready' tag.  |
        | Fail | OS not supported | -regression | | # Removes tag 'regression'.        |
        | Fail | My message       | tag    | -t*  | # Removes all tags starting with 't' except the newly added 'tag'. |

        See `Fatal Error` if you need to stop the whole test execution.

        Support for modifying tags was added in Robot Framework 2.7.4 and
        HTML message support in 2.8.
        """
        self._set_and_remove_tags(tags)
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

    def should_not_be_true(self, condition, msg=None):
        """Fails if the given condition is true.

        See `Should Be True` for details about how ``condition`` is evaluated
        and how ``msg`` can be used to override the default error message.
        """
        if not msg:
            msg = "'%s' should not be true." % condition
        asserts.fail_if(self._is_true(condition), msg)

    def should_be_true(self, condition, msg=None):
        """Fails if the given condition is not true.

        If ``condition`` is a string (e.g. ``${rc} < 10``), it is evaluated as
        a Python expression using the `Evaluate` keyword internally and the
        keyword status is decided based on the result. If a non-string item is
        given, the status is got directly from its
        [http://docs.python.org/2/library/stdtypes.html#truth|truth value].

        The default error message (``<condition> should be true``) is not very
        informative, but it can be overridden with the ``msg`` argument.

        Examples:
        | Should Be True | ${rc} < 10  |
        | Should Be True | '${status}' == 'PASS' | # Strings must be quoted |
        | Should Be True | 'foo' in '''${multiline text}''' | # Multiline strings must be in triple quotes |
        | Should Be True | ${number}   | # Passes if ${number} is not zero |
        | Should Be True | ${list}     | # Passes if ${list} is not empty  |

        Starting from Robot Framework 2.9, all current variables are available
        in the evaluation namespace automatically without the ``${}``
        decoration:

        | Should Be True | rc < 10  | # Passes if ${rc} is a number less than 10 |
        | Should Be True | status == 'PASS' | # Expected string must be quoted |

        Starting from Robot Framework 2.8, `Should Be True` automatically
        imports Python's [http://docs.python.org/2/library/os.html|os] and
        [http://docs.python.org/2/library/sys.html|sys] modules that contain
        several useful attributes:

        | Should Be True | os.linesep == '\\n'             | # Unixy   |
        | Should Be True | os.linesep == '\\r\\n'          | # Windows |
        | Should Be True | sys.platform == 'darwin'        | # OS X    |
        | Should Be True | sys.platform.startswith('java') | # Jython  |
        """
        if not msg:
            msg = "'%s' should be true." % condition
        asserts.fail_unless(self._is_true(condition), msg)

    def should_be_equal(self, first, second, msg=None, values=True):
        """Fails if the given objects are unequal.

        Optional ``msg`` and ``values`` arguments specify how to construct
        the error message if this keyword fails:

        - If ``msg`` is not given, the error message is ``<first> != <second>``.
        - If ``msg`` is given and ``values`` gets a true value, the error
          message is ``<msg>: <first> != <second>``.
        - If ``msg`` is given and ``values`` gets a false value, the error
          message is simply ``<msg>``.

        ``values`` is true by default, but can be turned to false by using,
        for example, string ``false`` or ``no values``. See `Boolean arguments`
        section for more details.
        """
        self._log_types(first, second)
        self._should_be_equal(first, second, msg, values)

    def _should_be_equal(self, first, second, msg, values):
        asserts.fail_unless_equal(first, second, msg,
                                  self._include_values(values))

    def _include_values(self, values):
        return is_truthy(values) and str(values).upper() != 'NO VALUES'

    def should_not_be_equal(self, first, second, msg=None, values=True):
        """Fails if the given objects are equal.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        self._log_types(first, second)
        self._should_not_be_equal(first, second, msg, values)

    def _should_not_be_equal(self, first, second, msg, values):
        asserts.fail_if_equal(first, second, msg, self._include_values(values))

    def should_not_be_equal_as_integers(self, first, second, msg=None,
                                        values=True, base=None):
        """Fails if objects are equal after converting them to integers.

        See `Convert To Integer` for information how to convert integers from
        other bases than 10 using ``base`` argument or ``0b/0o/0x`` prefixes.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.

        See `Should Be Equal As Integers` for some usage examples.
        """
        self._log_types(first, second)
        self._should_not_be_equal(self._convert_to_integer(first, base),
                                  self._convert_to_integer(second, base),
                                  msg, values)

    def should_be_equal_as_integers(self, first, second, msg=None, values=True,
                                    base=None):
        """Fails if objects are unequal after converting them to integers.

        See `Convert To Integer` for information how to convert integers from
        other bases than 10 using ``base`` argument or ``0b/0o/0x`` prefixes.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.

        Examples:
        | Should Be Equal As Integers | 42   | ${42} | Error message |
        | Should Be Equal As Integers | ABCD | abcd  | base=16 |
        | Should Be Equal As Integers | 0b1011 | 11  |
        """
        self._log_types(first, second)
        self._should_be_equal(self._convert_to_integer(first, base),
                              self._convert_to_integer(second, base),
                              msg, values)

    def should_not_be_equal_as_numbers(self, first, second, msg=None,
                                       values=True, precision=6):
        """Fails if objects are equal after converting them to real numbers.

        The conversion is done with `Convert To Number` keyword using the
        given ``precision``.

        See `Should Be Equal As Numbers` for examples on how to use
        ``precision`` and why it does not always work as expected. See also
        `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        self._log_types(first, second)
        first = self._convert_to_number(first, precision)
        second = self._convert_to_number(second, precision)
        self._should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_numbers(self, first, second, msg=None, values=True,
                                   precision=6):
        """Fails if objects are unequal after converting them to real numbers.

        The conversion is done with `Convert To Number` keyword using the
        given ``precision``.

        Examples:
        | Should Be Equal As Numbers | ${x} | 1.1 | | # Passes if ${x} is 1.1 |
        | Should Be Equal As Numbers | 1.123 | 1.1 | precision=1  | # Passes |
        | Should Be Equal As Numbers | 1.123 | 1.4 | precision=0  | # Passes |
        | Should Be Equal As Numbers | 112.3 | 75  | precision=-2 | # Passes |

        As discussed in the documentation of `Convert To Number`, machines
        generally cannot store floating point numbers accurately. Because of
        this limitation, comparing floats for equality is problematic and
        a correct approach to use depends on the context. This keyword uses
        a very naive approach of rounding the numbers before comparing them,
        which is both prone to rounding errors and does not work very well if
        numbers are really big or small. For more information about comparing
        floats, and ideas on how to implement your own context specific
        comparison algorithm, see
        http://randomascii.wordpress.com/2012/02/25/comparing-floating-point-numbers-2012-edition/.

        See `Should Not Be Equal As Numbers` for a negative version of this
        keyword and `Should Be Equal` for an explanation on how to override
        the default error message with ``msg`` and ``values``.
        """
        self._log_types(first, second)
        first = self._convert_to_number(first, precision)
        second = self._convert_to_number(second, precision)
        self._should_be_equal(first, second, msg, values)

    def should_not_be_equal_as_strings(self, first, second, msg=None, values=True):
        """Fails if objects are equal after converting them to strings.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        self._log_types(first, second)
        first, second = [self._convert_to_string(i) for i in first, second]
        self._should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_strings(self, first, second, msg=None, values=True):
        """Fails if objects are unequal after converting them to strings.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        self._log_types(first, second)
        first, second = [self._convert_to_string(i) for i in first, second]
        self._should_be_equal(first, second, msg, values)

    def should_not_start_with(self, str1, str2, msg=None, values=True):
        """Fails if the string ``str1`` starts with the string ``str2``.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'starts with')
        asserts.fail_if(str1.startswith(str2), msg)

    def should_start_with(self, str1, str2, msg=None, values=True):
        """Fails if the string ``str1`` does not start with the string ``str2``.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'does not start with')
        asserts.fail_unless(str1.startswith(str2), msg)

    def should_not_end_with(self, str1, str2, msg=None, values=True):
        """Fails if the string ``str1`` ends with the string ``str2``.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'ends with')
        asserts.fail_if(str1.endswith(str2), msg)

    def should_end_with(self, str1, str2, msg=None, values=True):
        """Fails if the string ``str1`` does not end with the string ``str2``.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        msg = self._get_string_msg(str1, str2, msg, values, 'does not end with')
        asserts.fail_unless(str1.endswith(str2), msg)

    def should_not_contain(self, item1, item2, msg=None, values=True):
        """Fails if ``item1`` contains ``item2`` one or more times.

        Works with strings, lists, and anything that supports Python's ``in``
        operator. See `Should Be Equal` for an explanation on how to override
        the default error message with ``msg`` and ``values``.

        Examples:
        | Should Not Contain | ${output}    | FAILED |
        | Should Not Contain | ${some_list} | value  |
        """
        msg = self._get_string_msg(item1, item2, msg, values, 'contains')
        asserts.fail_if(item2 in item1, msg)

    def should_contain(self, item1, item2, msg=None, values=True):
        """Fails if ``item1`` does not contain ``item2`` one or more times.

        Works with strings, lists, and anything that supports Python's ``in``
        operator. See `Should Be Equal` for an explanation on how to override
        the default error message with ``msg`` and ``values``.

        Examples:
        | Should Contain | ${output}    | PASS |
        | Should Contain | ${some_list} | value  |
        """
        msg = self._get_string_msg(item1, item2, msg, values, 'does not contain')
        asserts.fail_unless(item2 in item1, msg)

    def should_contain_x_times(self, item1, item2, count, msg=None):
        """Fails if ``item1`` does not contain ``item2`` ``count`` times.

        Works with strings, lists and all objects that `Get Count` works
        with. The default error message can be overridden with ``msg`` and
        the actual count is always logged.

        Examples:
        | Should Contain X Times | ${output}    | hello  | 2 |
        | Should Contain X Times | ${some list} | value  | 3 |
        """
        count = self._convert_to_integer(count)
        x = self.get_count(item1, item2)
        if not msg:
            msg = "'%s' contains '%s' %d time%s, not %d time%s." \
                    % (unic(item1), unic(item2), x, s(x), count, s(count))
        self.should_be_equal_as_integers(x, count, msg, values=False)

    def get_count(self, item1, item2):
        """Returns and logs how many times ``item2`` is found from ``item1``.

        This keyword works with Python strings and lists and all objects
        that either have ``count`` method or can be converted to Python lists.

        Example:
        | ${count} = | Get Count | ${some item} | interesting value |
        | Should Be True | 5 < ${count} < 10 |
        """
        if not hasattr(item1, 'count'):
            try:
                item1 = list(item1)
            except:
                raise RuntimeError("Converting '%s' to list failed: %s"
                                   % (item1, get_error_message()))
        count = item1.count(item2)
        self.log('Item found from the first item %d time%s' % (count, s(count)))
        return count

    def should_not_match(self, string, pattern, msg=None, values=True):
        """Fails if the given ``string`` matches the given ``pattern``.

        Pattern matching is similar as matching files in a shell, and it is
        always case-sensitive. In the pattern ``*`` matches to anything and
        ``?`` matches to any single character.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        msg = self._get_string_msg(string, pattern, msg, values, 'matches')
        asserts.fail_if(self._matches(string, pattern), msg)

    def should_match(self, string, pattern, msg=None, values=True):
        """Fails unless the given ``string`` matches the given ``pattern``.

        Pattern matching is similar as matching files in a shell, and it is
        always case-sensitive. In the pattern, ``*`` matches to anything and
        ``?`` matches to any single character.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        msg = self._get_string_msg(string, pattern, msg, values,
                                   'does not match')
        asserts.fail_unless(self._matches(string, pattern), msg)

    def should_match_regexp(self, string, pattern, msg=None, values=True):
        """Fails if ``string`` does not match ``pattern`` as a regular expression.

        Regular expression check is implemented using the Python
        [http://docs.python.org/2/library/re.html|re module]. Python's regular
        expression syntax is derived from Perl, and it is thus also very
        similar to the syntax used, for example, in Java, Ruby and .NET.

        Things to note about the regexp syntax in Robot Framework test data:

        1) Backslash is an escape character in the test data, and possible
        backslashes in the pattern must thus be escaped with another backslash
        (e.g. ``\\\\d\\\\w+``).

        2) Strings that may contain special characters, but should be handled
        as literal strings, can be escaped with the `Regexp Escape` keyword.

        3) The given pattern does not need to match the whole string. For
        example, the pattern ``ello`` matches the string ``Hello world!``. If
        a full match is needed, the ``^`` and ``$`` characters can be used to
        denote the beginning and end of the string, respectively. For example,
        ``^ello$`` only matches the exact string ``ello``.

        4) Possible flags altering how the expression is parsed (e.g.
        ``re.IGNORECASE``, ``re.MULTILINE``) can be set by prefixing the
        pattern with the ``(?iLmsux)`` group like ``(?im)pattern``. The
        available flags are ``i`` (case-insensitive), ``m`` (multiline mode),
        ``s`` (dotall mode), ``x`` (verbose), ``u`` (Unicode dependent) and
        ``L`` (locale dependent).

        If this keyword passes, it returns the portion of the string that
        matched the pattern. Additionally, the possible captured groups are
        returned.

        See the `Should Be Equal` keyword for an explanation on how to override
        the default error message with the ``msg`` and ``values`` arguments.

        Examples:
        | Should Match Regexp | ${output} | \\\\d{6}   | # Output contains six numbers  |
        | Should Match Regexp | ${output} | ^\\\\d{6}$ | # Six numbers and nothing more |
        | ${ret} = | Should Match Regexp | Foo: 42 | (?i)foo: \\\\d+ |
        | ${match} | ${group1} | ${group2} = |
        | ...      | Should Match Regexp | Bar: 43 | (Foo|Bar): (\\\\d+) |
        =>
        | ${ret} = 'Foo: 42'
        | ${match} = 'Bar: 43'
        | ${group1} = 'Bar'
        | ${group2} = '43'
        """
        msg = self._get_string_msg(string, pattern, msg, values, 'does not match')
        res = re.search(pattern, string)
        asserts.fail_if_none(res, msg, values=False)
        match = res.group(0)
        groups = res.groups()
        if groups:
            return [match] + list(groups)
        return match

    def should_not_match_regexp(self, string, pattern, msg=None, values=True):
        """Fails if ``string`` matches ``pattern`` as a regular expression.

        See `Should Match Regexp` for more information about arguments.
        """
        msg = self._get_string_msg(string, pattern, msg, values, 'matches')
        asserts.fail_unless_none(re.search(pattern, string), msg, values=False)

    def get_length(self, item):
        """Returns and logs the length of the given item as an integer.

        The item can be anything that has a length, for example, a string,
        a list, or a mapping. The keyword first tries to get the length with
        the Python function ``len``, which calls the  item's ``__len__`` method
        internally. If that fails, the keyword tries to call the item's
        possible ``length`` and ``size`` methods directly. The final attempt is
        trying to get the value of the item's ``length`` attribute. If all
        these attempts are unsuccessful, the keyword fails.

        Examples:
        | ${length} = | Get Length    | Hello, world! |        |
        | Should Be Equal As Integers | ${length}     | 13     |
        | @{list} =   | Create List   | Hello,        | world! |
        | ${length} = | Get Length    | ${list}       |        |
        | Should Be Equal As Integers | ${length}     | 2      |

        See also `Length Should Be`, `Should Be Empty` and `Should Not Be
        Empty`.
        """
        length = self._get_length(item)
        self.log('Length is %d' % length)
        return length

    def _get_length(self, item):
        try:
            return len(item)
        except RERAISED_EXCEPTIONS:
            raise
        except:
            try:
                return item.length()
            except RERAISED_EXCEPTIONS:
                raise
            except:
                try:
                    return item.size()
                except RERAISED_EXCEPTIONS:
                    raise
                except:
                    try:
                        return item.length
                    except RERAISED_EXCEPTIONS:
                        raise
                    except:
                        raise RuntimeError("Could not get length of '%s'." % item)

    def length_should_be(self, item, length, msg=None):
        """Verifies that the length of the given item is correct.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the ``msg`` argument.
        """
        length = self._convert_to_integer(length)
        actual = self.get_length(item)
        if actual != length:
            raise AssertionError(msg or "Length of '%s' should be %d but is %d."
                                        % (item, length, actual))

    def should_be_empty(self, item, msg=None):
        """Verifies that the given item is empty.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the ``msg`` argument.
        """
        if self.get_length(item) > 0:
            raise AssertionError(msg or "'%s' should be empty." % item)

    def should_not_be_empty(self, item, msg=None):
        """Verifies that the given item is not empty.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the ``msg`` argument.
        """
        if self.get_length(item) == 0:
            raise AssertionError(msg or "'%s' should not be empty." % item)

    def _get_string_msg(self, str1, str2, msg, values, delim):
        default = "'%s' %s '%s'" % (unic(str1), delim, unic(str2))
        if not msg:
            msg = default
        elif self._include_values(values):
            msg = '%s: %s' % (msg, default)
        return msg


class _Variables(_BuiltInBase):

    def get_variables(self, no_decoration=False):
        """Returns a dictionary containing all variables in the current scope.

        Variables are returned as a special dictionary that allows accessing
        variables in space, case, and underscore insensitive manner similarly
        as accessing variables in the test data. This dictionary supports all
        same operations as normal Python dictionaries and, for example,
        Collections library can be used to access or modify it. Modifying the
        returned dictionary has no effect on the variables available in the
        current scope.

        By default variables are returned with ``${}``, ``@{}`` or ``&{}``
        decoration based on variable types. Giving a true value (see `Boolean
        arguments`) to the optional argument ``no_decoration`` will return
        the variables without the decoration. This option is new in Robot
        Framework 2.9.

        Example:
        | ${example_variable} =         | Set Variable | example value         |
        | ${variables} =                | Get Variables |                      |
        | Dictionary Should Contain Key | ${variables} | \\${example_variable} |
        | Dictionary Should Contain Key | ${variables} | \\${ExampleVariable}  |
        | Set To Dictionary             | ${variables} | \\${name} | value     |
        | Variable Should Not Exist     | \\${name}    |           |           |
        | ${no decoration} =            | Get Variables | no_decoration=Yes |
        | Dictionary Should Contain Key | ${no decoration} | example_variable |

        Note: Prior to Robot Framework 2.7.4 variables were returned as
        a custom object that did not support all dictionary methods.
        """
        return self._variables.as_dict(decoration=is_falsy(no_decoration))

    @run_keyword_variant(resolve=0)
    def get_variable_value(self, name, default=None):
        """Returns variable value or ``default`` if the variable does not exist.

        The name of the variable can be given either as a normal variable name
        (e.g. ``${NAME}``) or in escaped format (e.g. ``\\${NAME}``). Notice
        that the former has some limitations explained in `Set Suite Variable`.

        Examples:
        | ${x} = | Get Variable Value | ${a} | default |
        | ${y} = | Get Variable Value | ${a} | ${b}    |
        | ${z} = | Get Variable Value | ${z} |         |
        =>
        | ${x} gets value of ${a} if ${a} exists and string 'default' otherwise
        | ${y} gets value of ${a} if ${a} exists and value of ${b} otherwise
        | ${z} is set to Python None if it does not exist previously

        See `Set Variable If` for another keyword to set variables dynamically.
        """
        try:
            return self._variables[self._get_var_name(name)]
        except DataError:
            return self._variables.replace_scalar(default)

    def log_variables(self, level='INFO'):
        """Logs all variables in the current scope with given log level."""
        variables = self.get_variables()
        for name in sorted(variables, key=lambda s: s[2:-1].lower()):
            msg = format_assign_message(name, variables[name], cut_long=False)
            self.log(msg, level)

    @run_keyword_variant(resolve=0)
    def variable_should_exist(self, name, msg=None):
        """Fails unless the given variable exists within the current scope.

        The name of the variable can be given either as a normal variable name
        (e.g. ``${NAME}``) or in escaped format (e.g. ``\\${NAME}``). Notice
        that the former has some limitations explained in `Set Suite Variable`.

        The default error message can be overridden with the ``msg`` argument.

        See also `Variable Should Not Exist` and `Keyword Should Exist`.
        """
        name = self._get_var_name(name)
        msg = self._variables.replace_string(msg) if msg \
            else "Variable %s does not exist." % name
        try:
            self._variables[name]
        except DataError:
            raise AssertionError(msg)

    @run_keyword_variant(resolve=0)
    def variable_should_not_exist(self, name, msg=None):
        """Fails if the given variable exists within the current scope.

        The name of the variable can be given either as a normal variable name
        (e.g. ``${NAME}``) or in escaped format (e.g. ``\\${NAME}``). Notice
        that the former has some limitations explained in `Set Suite Variable`.

        The default error message can be overridden with the ``msg`` argument.

        See also `Variable Should Exist` and `Keyword Should Exist`.
        """
        name = self._get_var_name(name)
        msg = self._variables.replace_string(msg) if msg \
            else "Variable %s exists." % name
        try:
            self._variables[name]
        except DataError:
            pass
        else:
            raise AssertionError(msg)

    def replace_variables(self, text):
        """Replaces variables in the given text with their current values.

        If the text contains undefined variables, this keyword fails.
        If the given ``text`` contains only a single variable, its value is
        returned as-is and it can be any object. Otherwise this keyword
        always returns a string.

        Example:

        The file ``template.txt`` contains ``Hello ${NAME}!`` and variable
        ``${NAME}`` has the value ``Robot``.

        | ${template} =   | Get File          | ${CURDIR}/template.txt |
        | ${message} =    | Replace Variables | ${template}            |
        | Should Be Equal | ${message}        | Hello Robot!           |
        """
        return self._variables.replace_scalar(text)

    def set_variable(self, *values):
        """Returns the given values which can then be assigned to a variables.

        This keyword is mainly used for setting scalar variables.
        Additionally it can be used for converting a scalar variable
        containing a list to a list variable or to multiple scalar variables.
        It is recommended to use `Create List` when creating new lists.

        Examples:
        | ${hi} =   | Set Variable | Hello, world! |
        | ${hi2} =  | Set Variable | I said: ${hi} |
        | ${var1}   | ${var2} =    | Set Variable | Hello | world |
        | @{list} = | Set Variable | ${list with some items} |
        | ${item1}  | ${item2} =   | Set Variable  | ${list with 2 items} |

        Variables created with this keyword are available only in the
        scope where they are created. See `Set Global Variable`,
        `Set Test Variable` and `Set Suite Variable` for information on how to
        set variables so that they are available also in a larger scope.
        """
        if len(values) == 0:
            return ''
        elif len(values) == 1:
            return values[0]
        else:
            return list(values)

    @run_keyword_variant(resolve=0)
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
        self._variables.set_test(name, value)
        self._log_set_variable(name, value)

    @run_keyword_variant(resolve=0)
    def set_suite_variable(self, name, *values):
        """Makes a variable available everywhere within the scope of the current suite.

        Variables set with this keyword are available everywhere within the
        scope of the currently executed test suite. Setting variables with this
        keyword thus has the same effect as creating them using the Variable
        table in the test data file or importing them from variable files.

        Possible child test suites do not see variables set with this keyword
        by default. Starting from Robot Framework 2.9, that can be controlled
        by using ``children=<option>`` as the last argument. If the specified
        ``<option>`` is a non-empty string or any other value considered true
        in Python, the variable is set also to the child suites. Parent and
        sibling suites will never see variables set with this keyword.

        The name of the variable can be given either as a normal variable name
        (e.g. ``${NAME}``) or in escaped format as ``\\${NAME}`` or ``$NAME``.
        Variable value can be given using the same syntax as when variables
        are created in the Variable table.

        If a variable already exists within the new scope, its value will be
        overwritten. Otherwise a new variable is created. If a variable already
        exists within the current scope, the value can be left empty and the
        variable within the new scope gets the value within the current scope.

        Examples:
        | Set Suite Variable | ${SCALAR} | Hello, world! |
        | Set Suite Variable | ${SCALAR} | Hello, world! | children=true |
        | Set Suite Variable | @{LIST}   | First item    | Second item   |
        | Set Suite Variable | &{DICT}   | key=value     | foo=bar       |
        | ${ID} =            | Get ID    |
        | Set Suite Variable | ${ID}     |

        To override an existing value with an empty value, use built-in
        variables ``${EMPTY}``, ``@{EMPTY}`` or ``&{EMPTY}``:

        | Set Suite Variable | ${SCALAR} | ${EMPTY} |
        | Set Suite Variable | @{LIST}   | @{EMPTY} | # New in RF 2.7.4 |
        | Set Suite Variable | &{DICT}   | &{EMPTY} | # New in RF 2.9   |

        *NOTE:* If the variable has value which itself is a variable (escaped
        or not), you must always use the escaped format to set the variable:

        Example:
        | ${NAME} =          | Set Variable | \\${var} |
        | Set Suite Variable | ${NAME}      | value | # Sets variable ${var}  |
        | Set Suite Variable | \\${NAME}    | value | # Sets variable ${NAME} |

        This limitation applies also to `Set Test Variable`, `Set Global
        Variable`, `Variable Should Exist`, `Variable Should Not Exist` and
        `Get Variable Value` keywords.
        """
        name = self._get_var_name(name)
        if (values and isinstance(values[-1], basestring) and
                values[-1].startswith('children=')):
            children = self._variables.replace_scalar(values[-1][9:])
            children = is_truthy(children)
            values = values[:-1]
        else:
            children = False
        value = self._get_var_value(name, values)
        self._variables.set_suite(name, value, children=children)
        self._log_set_variable(name, value)

    @run_keyword_variant(resolve=0)
    def set_global_variable(self, name, *values):
        """Makes a variable available globally in all tests and suites.

        Variables set with this keyword are globally available in all test
        cases and suites executed after setting them. Setting variables with
        this keyword thus has the same effect as creating from the command line
        using the options ``--variable`` or ``--variablefile``. Because this
        keyword can change variables everywhere, it should be used with care.

        See `Set Suite Variable` for more information and examples.
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self._variables.set_global(name, value)
        self._log_set_variable(name, value)

    # Helpers

    def _get_var_name(self, orig):
        name = self._resolve_possible_variable(orig)
        try:
            return self._unescape_variable_if_needed(name)
        except ValueError:
            raise RuntimeError("Invalid variable syntax '%s'." % orig)

    def _resolve_possible_variable(self, name):
        try:
            resolved = self._variables.replace_string(name)
            return self._unescape_variable_if_needed(resolved)
        except (KeyError, ValueError, DataError):
            return name

    def _unescape_variable_if_needed(self, name):
        if name.startswith('\\'):
            name = name[1:]
        if len(name) < 2:
            raise ValueError
        if name[0] in '$@&' and name[1] != '{':
            name = '%s{%s}' % (name[0], name[1:])
        if is_var(name):
            return name
        # Support for possible internal variables (issue 397)
        name = '%s{%s}' % (name[0], self.replace_variables(name[2:-1]))
        if is_var(name):
            return name
        raise ValueError

    def _get_var_value(self, name, values):
        if not values:
            return self._variables[name]
        # TODO: In RF 2.10/3.0 the if branch below can be removed and
        # VariableTableValue used with all variables. See issue #1919.
        if name[0] == '$':
            if len(values) != 1 or VariableSplitter(values[0]).is_list_variable():
                raise DataError("Setting list value to scalar variable '%s' "
                                "is not supported anymore. Create list "
                                "variable '@%s' instead." % (name, name[1:]))
            return self._variables.replace_scalar(values[0])
        return VariableTableValue(values, name).resolve(self._variables)

    def _log_set_variable(self, name, value):
        self.log(format_assign_message(name, value))


class _RunKeyword(_BuiltInBase):

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
            raise RuntimeError('Keyword name must be string.')
        kw = Keyword(name, args=args)
        return kw.run(self._context)

    def run_keywords(self, *keywords):
        """Executes all the given keywords in a sequence.

        This keyword is mainly useful in setups and teardowns when they need to
        take care of multiple actions and creating a new higher level user
        keyword would be an overkill.

        Examples:
        | Run Keywords | Initialize database | Start servers | Clear logs |
        | Run Keywords | ${KW 1} | ${KW 2} |
        | Run Keywords | @{KEYWORDS} |

        In this example, we call `Run Keywords` with three different combination
        of arguments. Keyword names and arguments can come from variables, as
        demonstrated in the second and third row.

        Starting from Robot Framework 2.7.6, keywords can also be run with
        arguments using upper case ``AND`` as a separator between keywords.
        The keywords are executed so that the first argument is the first
        keyword and proceeding arguments until the first ``AND`` are arguments
        to it. First argument after the first ``AND`` is the second keyword and
        proceeding arguments until the next ``AND`` are its arguments. And so on.

        Examples:
        | Run Keywords | Initialize database | db1 | AND | Start servers | server1 | server2 |
        | Run Keywords | Initialize database | ${DB NAME} | AND | Start servers | @{SERVERS} | AND | Clear logs |
        | Run Keywords | ${KW} | AND | @{KW WITH ARGS} |

        Notice that the ``AND`` control argument must be used explicitly and thus
        cannot itself come from a variable. If you need to use literal ``AND``
        string as argument, you can either use variables or escape it with
        a backslash like ``\\AND``.
        """
        self._run_keywords(self._split_run_keywords(list(keywords)))

    def _run_keywords(self, iterable):
        errors = []
        for kw, args in iterable:
            try:
                self.run_keyword(kw, *args)
            except ExecutionPassed as err:
                err.set_earlier_failures(errors)
                raise err
            except ExecutionFailed as err:
                errors.extend(err.get_errors())
                if not err.can_continue(self._context.in_teardown):
                    break
        if errors:
            raise ExecutionFailures(errors)

    def _split_run_keywords(self, keywords):
        if 'AND' not in keywords:
            for name in self._variables.replace_list(keywords):
                yield name, ()
        else:
            for name, args in self._split_run_keywords_from_and(keywords):
                yield name, args

    def _split_run_keywords_from_and(self, keywords):
        while 'AND' in keywords:
            index = keywords.index('AND')
            yield self._resolve_run_keywords_name_and_args(keywords[:index])
            keywords = keywords[index+1:]
        yield self._resolve_run_keywords_name_and_args(keywords)

    def _resolve_run_keywords_name_and_args(self, kw_call):
        kw_call = self._variables.replace_list(kw_call, replace_until=1)
        if not kw_call:
            raise DataError('Incorrect use of AND')
        return kw_call[0], kw_call[1:]

    def run_keyword_if(self, condition, name, *args):
        """Runs the given keyword with the given arguments, if ``condition`` is true.

        The given ``condition`` is evaluated similarly as with `Should Be
        True` keyword, and ``name`` and ``*args`` have same semantics as with
        `Run Keyword`.

        Example, a simple if/else construct:
        | ${status} | ${value} = | `Run Keyword And Ignore Error` | `My Keyword` |
        | `Run Keyword If`     | '${status}' == 'PASS' | `Some Action`    | arg |
        | `Run Keyword Unless` | '${status}' == 'PASS' | `Another Action` |

        In this example, only either `Some Action` or `Another Action` is
        executed, based on the status of `My Keyword`. Instead of `Run Keyword
        And Ignore Error` you can also use `Run Keyword And Return Status`.

        Starting from Robot version 2.7.4, this keyword supports also optional
        ELSE and ELSE IF branches. Both of these are defined in ``*args`` and
        must use exactly format ``ELSE`` or ``ELSE IF``, respectively. ELSE
        branches must contain first the name of the keyword to execute and then
        its possible arguments. ELSE IF branches must first contain a condition,
        like the first argument to this keyword, and then the keyword to execute
        and its possible arguments. It is possible to have ELSE branch after
        ELSE IF and to have multiple ELSE IF branches.

        Given previous example, if/else construct can also be created like this:
        | ${status} | ${value} = | `Run Keyword And Ignore Error` | My Keyword |
        | `Run Keyword If` | '${status}' == 'PASS' | `Some Action` | arg | ELSE | `Another Action` |

        The return value is the one of the keyword that was executed or None if
        no keyword was executed (i.e. if ``condition`` was false). Hence, it is
        recommended to use ELSE and/or ELSE IF branches to conditionally assign
        return values from keyword to variables (to conditionally assign fixed
        values to variables, see `Set Variable If`). This is illustrated by the
        example below:

        | ${var1} =   | `Run Keyword If` | ${rc} == 0     | `Some keyword returning a value` |
        | ...         | ELSE IF          | 0 < ${rc} < 42 | `Another keyword` |
        | ...         | ELSE IF          | ${rc} < 0      | `Another keyword with args` | ${rc} | arg2 |
        | ...         | ELSE             | `Final keyword to handle abnormal cases` | ${rc} |
        | ${var2} =   | `Run Keyword If` | ${condition}  | `Some keyword` |

        In this example, ${var2} will be set to None if ${condition} is false.

        Notice that ``ELSE`` and ``ELSE IF`` control words must be used
        explicitly and thus cannot come from variables. If you need to use
        literal ``ELSE`` and ``ELSE IF`` strings as arguments, you can escape
        them with a backslash like ``\\ELSE`` and ``\\ELSE IF``.

        Starting from Robot Framework 2.8, Python's
        [http://docs.python.org/2/library/os.html|os] and
        [http://docs.python.org/2/library/sys.html|sys] modules are
        automatically imported when evaluating the ``condition``.
        Attributes they contain can thus be used in the condition:

        | `Run Keyword If` | os.sep == '/' | `Unix Keyword`        |
        | ...              | ELSE IF       | sys.platform.startswith('java') | `Jython Keyword` |
        | ...              | ELSE          | `Windows Keyword`     |
        """
        args, branch = self._split_elif_or_else_branch(args)
        if self._is_true(condition):
            return self.run_keyword(name, *args)
        return branch()

    def _split_elif_or_else_branch(self, args):
        if 'ELSE IF' in args:
            args, branch = self._split_branch(args, 'ELSE IF', 2,
                                              'condition and keyword')
            return args, lambda: self.run_keyword_if(*branch)
        if 'ELSE' in args:
            args, branch = self._split_branch(args, 'ELSE', 1, 'keyword')
            return args, lambda: self.run_keyword(*branch)
        return args, lambda: None

    def _split_branch(self, args, control_word, required, required_error):
        index = list(args).index(control_word)
        branch = self._variables.replace_list(args[index+1:], required)
        if len(branch) < required:
            raise DataError('%s requires %s.' % (control_word, required_error))
        return args[:index], branch

    def run_keyword_unless(self, condition, name, *args):
        """Runs the given keyword with the given arguments, if ``condition`` is false.

        See `Run Keyword If` for more information and an example.
        """
        if not self._is_true(condition):
            return self.run_keyword(name, *args)

    def run_keyword_and_ignore_error(self, name, *args):
        """Runs the given keyword with the given arguments and ignores possible error.

        This keyword returns two values, so that the first is either string
        ``PASS`` or ``FAIL``, depending on the status of the executed keyword.
        The second value is either the return value of the keyword or the
        received error message. See `Run Keyword And Return Status` If you are
        only interested in the execution status.

        The keyword name and arguments work as in `Run Keyword`. See
        `Run Keyword If` for a usage example.

        Errors caused by invalid syntax, timeouts, or fatal exceptions are not
        caught by this keyword. Otherwise this keyword itself never fails.
        """
        try:
            return 'PASS', self.run_keyword(name, *args)
        except ExecutionFailed as err:
            if err.dont_continue:
                raise
            return 'FAIL', unicode(err)

    def run_keyword_and_return_status(self, name, *args):
        """Runs the given keyword with given arguments and returns the status as a Boolean value.

        This keyword returns Boolean ``True`` if the keyword that is executed
        succeeds and ``False`` if it fails. This is useful, for example, in
        combination with `Run Keyword If`. If you are interested in the error
        message or return value, use `Run Keyword And Ignore Error` instead.

        The keyword name and arguments work as in `Run Keyword`.

        Example:
        | ${passed} = | `Run Keyword And Return Status` | Keyword | args |
        | `Run Keyword If` | ${passed} | Another keyword |

        Errors caused by invalid syntax, timeouts, or fatal exceptions are not
        caught by this keyword. Otherwise this keyword itself never fails.

        New in Robot Framework 2.7.6.
        """
        status, _ = self.run_keyword_and_ignore_error(name, *args)
        return status == 'PASS'

    def run_keyword_and_continue_on_failure(self, name, *args):
        """Runs the keyword and continues execution even if a failure occurs.

        The keyword name and arguments work as with `Run Keyword`.

        Example:
        | Run Keyword And Continue On Failure | Fail | This is a stupid example |
        | Log | This keyword is executed |

        The execution is not continued if the failure is caused by invalid syntax,
        timeout, or fatal exception.
        """
        try:
            return self.run_keyword(name, *args)
        except ExecutionFailed as err:
            if not err.dont_continue:
                err.continue_on_failure = True
            raise err

    def run_keyword_and_expect_error(self, expected_error, name, *args):
        """Runs the keyword and checks that the expected error occurred.

        The expected error must be given in the same format as in
        Robot Framework reports. It can be a pattern containing
        characters ``?``, which matches to any single character and
        ``*``, which matches to any number of any characters. ``name`` and
        ``*args`` have same semantics as with `Run Keyword`.

        If the expected error occurs, the error message is returned and it can
        be further processed/tested, if needed. If there is no error, or the
        error does not match the expected error, this keyword fails.

        Examples:
        | Run Keyword And Expect Error | My error | Some Keyword | arg1 | arg2 |
        | ${msg} = | Run Keyword And Expect Error | * | My KW |
        | Should Start With | ${msg} | Once upon a time in |

        Errors caused by invalid syntax, timeouts, or fatal exceptions are not
        caught by this keyword.
        """
        try:
            self.run_keyword(name, *args)
        except ExecutionFailed as err:
            if err.dont_continue:
                raise
        else:
            raise AssertionError("Expected error '%s' did not occur."
                                 % expected_error)
        if not self._matches(unicode(err), expected_error):
            raise AssertionError("Expected error '%s' but got '%s'."
                                 % (expected_error, err))
        return unicode(err)

    def repeat_keyword(self, times, name, *args):
        """Executes the specified keyword multiple times.

        ``name`` and ``args`` define the keyword that is executed
        similarly as with `Run Keyword`, and ``times`` specifies how many
        the keyword should be executed. ``times`` can be given as an
        integer or as a string that can be converted to an integer. If it is
        a string, it can have postfix ``times`` or ``x`` (case and space
        insensitive) to make the expression more explicit.

        If ``times`` is zero or negative, the keyword is not executed at
        all. This keyword fails immediately if any of the execution
        rounds fails.

        Examples:
        | Repeat Keyword | 5 times | Go to Previous Page |
        | Repeat Keyword | ${var}  | Some Keyword | arg1 | arg2 |
        """
        times = self._get_times_to_repeat(times)
        self._run_keywords(self._yield_repeated_keywords(times, name, args))

    def _get_times_to_repeat(self, times, require_postfix=False):
        times = normalize(str(times))
        if times.endswith('times'):
            times = times[:-5]
        elif times.endswith('x'):
            times = times[:-1]
        elif require_postfix:
            raise ValueError
        return self._convert_to_integer(times)

    def _yield_repeated_keywords(self, times, name, args):
        if times <= 0:
            self.log("Keyword '%s' repeated zero times." % name)
        for i in xrange(times):
            self.log("Repeating keyword, round %d/%d." % (i+1, times))
            yield name, args

    def wait_until_keyword_succeeds(self, retry, retry_interval, name, *args):
        """Runs the specified keyword and retries if it fails.

        ``name`` and ``args`` define the keyword that is executed similarly
        as with `Run Keyword`. How long to retry running the keyword is
        defined using ``retry`` argument either as timeout or count.
        ``retry_interval`` is the time to wait before trying to run the
        keyword again after the previous run has failed.

        If ``retry`` is given as timeout, it must be in Robot Framework's
        time format (e.g. ``1 minute``, ``2 min 3 s``, ``4.5``) that is
        explained in an appendix of Robot Framework User Guide. If it is
        given as count, it must have ``times`` or ``x`` postfix (e.g.
        ``5 times``, ``10 x``). ``retry_interval`` must always be given in
        Robot Framework's time format.

        If the keyword does not succeed regardless of retries, this keyword
        fails. If the executed keyword passes, its return value is returned.

        Examples:
        | Wait Until Keyword Succeeds | 2 min | 5 sec | My keyword | argument |
        | ${result} = | Wait Until Keyword Succeeds | 3x | 200ms | My keyword |

        All normal failures are caught by this keyword. Errors caused by
        invalid syntax, test or keyword timeouts, or fatal exceptions (caused
        e.g. by `Fatal Error`) are not caught.

        Running the same keyword multiple times inside this keyword can create
        lots of output and considerably increase the size of the generated
        output files. Starting from Robot Framework 2.7, it is possible to
        remove unnecessary keywords from the outputs using
        ``--RemoveKeywords WUKS`` command line option.

        Support for specifying ``retry`` as a number of times to retry is
        a new feature in Robot Framework 2.9.
        """
        maxtime = count = -1
        try:
            count = self._get_times_to_repeat(retry, require_postfix=True)
        except ValueError:
            timeout = timestr_to_secs(retry)
            maxtime = time.time() + timeout
            message = 'for %s' % secs_to_timestr(timeout)
        else:
            if count <= 0:
                raise ValueError('Retry count %d is not positive.' % count)
            message = '%d time%s' % (count, s(count))
        retry_interval = timestr_to_secs(retry_interval)
        while True:
            try:
                return self.run_keyword(name, *args)
            except ExecutionFailed as err:
                if err.dont_continue:
                    raise
                count -= 1
                if time.time() > maxtime > 0 or count == 0:
                    raise AssertionError("Keyword '%s' failed after retrying "
                                         "%s. The last error was: %s"
                                         % (name, message, err))
                self._sleep_in_parts(retry_interval)

    def set_variable_if(self, condition, *values):
        """Sets variable based on the given condition.

        The basic usage is giving a condition and two values. The
        given condition is first evaluated the same way as with the
        `Should Be True` keyword. If the condition is true, then the
        first value is returned, and otherwise the second value is
        returned. The second value can also be omitted, in which case
        it has a default value None. This usage is illustrated in the
        examples below, where ``${rc}`` is assumed to be zero.

        | ${var1} = | Set Variable If | ${rc} == 0 | zero     | nonzero |
        | ${var2} = | Set Variable If | ${rc} > 0  | value1   | value2  |
        | ${var3} = | Set Variable If | ${rc} > 0  | whatever |         |
        =>
        | ${var1} = 'zero'
        | ${var2} = 'value2'
        | ${var3} = None

        It is also possible to have 'else if' support by replacing the
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

        Use `Get Variable Value` if you need to set variables
        dynamically based on whether a variable exist or not.
        """
        values = self._verify_values_for_set_variable_if(list(values))
        if self._is_true(condition):
            return self._variables.replace_scalar(values[0])
        values = self._verify_values_for_set_variable_if(values[1:], True)
        if len(values) == 1:
            return self._variables.replace_scalar(values[0])
        return self.run_keyword('BuiltIn.Set Variable If', *values[0:])

    def _verify_values_for_set_variable_if(self, values, default=False):
        if not values:
            if default:
                return [None]
            raise RuntimeError('At least one value is required')
        if is_list_var(values[0]):
            values[:1] = [escape(item) for item in self._variables[values[0]]]
            return self._verify_values_for_set_variable_if(values)
        return values

    def run_keyword_if_test_failed(self, name, *args):
        """Runs the given keyword with the given arguments, if the test failed.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.

        Prior to Robot Framework 2.9 failures in test teardown itself were
        not detected by this keyword.
        """
        test = self._get_test_in_teardown('Run Keyword If Test Failed')
        if not test.passed or self._context.failure_in_test_teardown:
            return self.run_keyword(name, *args)

    def run_keyword_if_test_passed(self, name, *args):
        """Runs the given keyword with the given arguments, if the test passed.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.

        Prior to Robot Framework 2.9 failures in test teardown itself were
        not detected by this keyword.
        """
        test = self._get_test_in_teardown('Run Keyword If Test Passed')
        if test.passed and not self._context.failure_in_test_teardown:
            return self.run_keyword(name, *args)

    def run_keyword_if_timeout_occurred(self, name, *args):
        """Runs the given keyword if either a test or a keyword timeout has occurred.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        self._get_test_in_teardown('Run Keyword If Timeout Occurred')
        if self._context.timeout_occurred:
            return self.run_keyword(name, *args)

    def _get_test_in_teardown(self, kwname):
        ctx = self._context
        if ctx.test and ctx.in_test_teardown:
            return ctx.test
        raise RuntimeError("Keyword '%s' can only be used in test teardown."
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
        if suite.statistics.critical.failed == 0:
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
        if suite.statistics.critical.failed > 0:
            return self.run_keyword(name, *args)

    def run_keyword_if_all_tests_passed(self, name, *args):
        """Runs the given keyword with the given arguments, if all tests passed.

        This keyword can only be used in a suite teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        suite = self._get_suite_in_teardown('Run Keyword If All Tests Passed')
        if suite.statistics.all.failed == 0:
            return self.run_keyword(name, *args)

    def run_keyword_if_any_tests_failed(self, name, *args):
        """Runs the given keyword with the given arguments, if one or more tests failed.

        This keyword can only be used in a suite teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        suite = self._get_suite_in_teardown('Run Keyword If Any Tests Failed')
        if suite.statistics.all.failed > 0:
            return self.run_keyword(name, *args)

    def _get_suite_in_teardown(self, kwname):
        if not self._context.in_suite_teardown:
            raise RuntimeError("Keyword '%s' can only be used in suite teardown."
                               % kwname)
        return self._context.suite


class _Control(_BuiltInBase):

    def continue_for_loop(self):
        """Skips the current for loop iteration and continues from the next.

        Skips the remaining keywords in the current for loop iteration and
        continues from the next one. Can be used directly in a for loop or
        in a keyword that the loop uses.

        Example:
        | :FOR | ${var}         | IN                     | @{VALUES}         |
        |      | Run Keyword If | '${var}' == 'CONTINUE' | Continue For Loop |
        |      | Do Something   | ${var}                 |

        See `Continue For Loop If` to conditionally continue a for loop without
        using `Run Keyword If` or other wrapper keywords.

        New in Robot Framework 2.8.
        """
        self.log("Continuing for loop from the next iteration.")
        raise ContinueForLoop()

    def continue_for_loop_if(self, condition):
        """Skips the current for loop iteration if the ``condition`` is true.

        A wrapper for `Continue For Loop` to continue a for loop based on
        the given condition. The condition is evaluated using the same
        semantics as with `Should Be True` keyword.

        Example:
        | :FOR | ${var}               | IN                     | @{VALUES} |
        |      | Continue For Loop If | '${var}' == 'CONTINUE' |
        |      | Do Something         | ${var}                 |

        New in Robot Framework 2.8.
        """
        if self._is_true(condition):
            self.continue_for_loop()

    def exit_for_loop(self):
        """Stops executing the enclosing for loop.

        Exits the enclosing for loop and continues execution after it.
        Can be used directly in a for loop or in a keyword that the loop uses.

        Example:
        | :FOR | ${var}         | IN                 | @{VALUES}     |
        |      | Run Keyword If | '${var}' == 'EXIT' | Exit For Loop |
        |      | Do Something   | ${var} |

        See `Exit For Loop If` to conditionally exit a for loop without
        using `Run Keyword If` or other wrapper keywords.
        """
        self.log("Exiting for loop altogether.")
        raise ExitForLoop()

    def exit_for_loop_if(self, condition):
        """Stops executing the enclosing for loop if the ``condition`` is true.

        A wrapper for `Exit For Loop` to exit a for loop based on
        the given condition. The condition is evaluated using the same
        semantics as with `Should Be True` keyword.

        Example:
        | :FOR | ${var}           | IN                 | @{VALUES} |
        |      | Exit For Loop If | '${var}' == 'EXIT' |
        |      | Do Something     | ${var}             |

        New in Robot Framework 2.8.
        """
        if self._is_true(condition):
            self.exit_for_loop()

    @run_keyword_variant(resolve=0)
    def return_from_keyword(self, *return_values):
        """Returns from the enclosing user keyword.

        This keyword can be used to return from a user keyword with PASS status
        without executing it fully. It is also possible to return values
        similarly as with the ``[Return]`` setting. For more detailed information
        about working with the return values, see the User Guide.

        This keyword is typically wrapped to some other keyword, such as
        `Run Keyword If` or `Run Keyword If Test Passed`, to return based
        on a condition:

        | Run Keyword If | ${rc} < 0 | Return From Keyword |
        | Run Keyword If Test Passed | Return From Keyword |

        It is possible to use this keyword to return from a keyword also inside
        a for loop. That, as well as returning values, is demonstrated by the
        `Find Index` keyword in the following somewhat advanced example.
        Notice that it is often a good idea to move this kind of complicated
        logic into a test library.

        | ***** Variables *****
        | @{LIST} =    foo    baz
        |
        | ***** Test Cases *****
        | Example
        |     ${index} =    Find Index    baz    @{LIST}
        |     Should Be Equal    ${index}    ${1}
        |     ${index} =    Find Index    non existing    @{LIST}
        |     Should Be Equal    ${index}    ${-1}
        |
        | ***** Keywords *****
        | Find Index
        |    [Arguments]    ${element}    @{items}
        |    ${index} =    Set Variable    ${0}
        |    :FOR    ${item}    IN    @{items}
        |    \\    Run Keyword If    '${item}' == '${element}'    Return From Keyword    ${index}
        |    \\    ${index} =    Set Variable    ${index + 1}
        |    Return From Keyword    ${-1}    # Also [Return] would work here.

        The most common use case, returning based on an expression, can be
        accomplished directly with `Return From Keyword If`. Both of these
        keywords are new in Robot Framework 2.8.

        See also `Run Keyword And Return` and `Run Keyword And Return If`.
        """
        self.log('Returning from the enclosing user keyword.')
        raise ReturnFromKeyword(return_values)

    @run_keyword_variant(resolve=1)
    def return_from_keyword_if(self, condition, *return_values):
        """Returns from the enclosing user keyword if ``condition`` is true.

        A wrapper for `Return From Keyword` to return based on the given
        condition. The condition is evaluated using the same semantics as
        with `Should Be True` keyword.

        Given the same example as in `Return From Keyword`, we can rewrite the
        `Find Index` keyword as follows:

        | ***** Keywords *****
        | Find Index
        |    [Arguments]    ${element}    @{items}
        |    ${index} =    Set Variable    ${0}
        |    :FOR    ${item}    IN    @{items}
        |    \\    Return From Keyword If    '${item}' == '${element}'    ${index}
        |    \\    ${index} =    Set Variable    ${index + 1}
        |    Return From Keyword    ${-1}    # Also [Return] would work here.

        See also `Run Keyword And Return` and `Run Keyword And Return If`.

        New in Robot Framework 2.8.
        """
        if self._is_true(condition):
            self.return_from_keyword(*return_values)

    @run_keyword_variant(resolve=1)
    def run_keyword_and_return(self, name, *args):
        """Runs the specified keyword and returns from the enclosing user keyword.

        The keyword to execute is defined with ``name`` and ``*args`` exactly
        like with `Run Keyword`. After running the keyword, returns from the
        enclosing user keyword and passes possible return value from the
        executed keyword further. Returning from a keyword has exactly same
        semantics as with `Return From Keyword`.

        Example:
        | `Run Keyword And Return`  | `My Keyword` | arg1 | arg2 |
        | # Above is equivalent to: |
        | ${result} =               | `My Keyword` | arg1 | arg2 |
        | `Return From Keyword`     | ${result}    |      |      |

        Use `Run Keyword And Return If` if you want to run keyword and return
        based on a condition.

        New in Robot Framework 2.8.2.
        """
        ret = self.run_keyword(name, *args)
        self.return_from_keyword(escape(ret))

    @run_keyword_variant(resolve=2)
    def run_keyword_and_return_if(self, condition, name, *args):
        """Runs the specified keyword and returns from the enclosing user keyword.

        A wrapper for `Run Keyword And Return` to run and return based on
        the given ``condition``. The condition is evaluated using the same
        semantics as with `Should Be True` keyword.

        Example:
        | `Run Keyword And Return If` | ${rc} > 0 | `My Keyword` | arg1 | arg2 |
        | # Above is equivalent to:   |
        | `Run Keyword If`            | ${rc} > 0 | `Run Keyword And Return` | `My Keyword ` | arg1 | arg2 |

        Use `Return From Keyword If` if you want to return a certain value
        based on a condition.

        New in Robot Framework 2.8.2.
        """
        if self._is_true(condition):
            self.run_keyword_and_return(name, *args)

    def pass_execution(self, message, *tags):
        """Skips rest of the current test, setup, or teardown with PASS status.

        This keyword can be used anywhere in the test data, but the place where
        used affects the behavior:

        - When used in any setup or teardown (suite, test or keyword), passes
          that setup or teardown. Possible keyword teardowns of the started
          keywords are executed. Does not affect execution or statuses
          otherwise.
        - When used in a test outside setup or teardown, passes that particular
          test case. Possible test and keyword teardowns are executed.

        Possible continuable failures before this keyword is used, as well as
        failures in executed teardowns, will fail the execution.

        It is mandatory to give a message explaining why execution was passed.
        By default the message is considered plain text, but starting it with
        ``*HTML*`` allows using HTML formatting.

        It is also possible to modify test tags passing tags after the message
        similarly as with `Fail` keyword. Tags starting with a hyphen
        (e.g. ``-regression``) are removed and others added. Tags are modified
        using `Set Tags` and `Remove Tags` internally, and the semantics
        setting and removing them are the same as with these keywords.

        Examples:
        | Pass Execution | All features available in this version tested. |
        | Pass Execution | Deprecated test. | deprecated | -regression    |

        This keyword is typically wrapped to some other keyword, such as
        `Run Keyword If`, to pass based on a condition. The most common case
        can be handled also with `Pass Execution If`:

        | Run Keyword If    | ${rc} < 0 | Pass Execution | Negative values are cool. |
        | Pass Execution If | ${rc} < 0 | Negative values are cool. |

        Passing execution in the middle of a test, setup or teardown should be
        used with care. In the worst case it leads to tests that skip all the
        parts that could actually uncover problems in the tested application.
        In cases where execution cannot continue do to external factors,
        it is often safer to fail the test case and make it non-critical.

        New in Robot Framework 2.8.
        """
        message = message.strip()
        if not message:
            raise RuntimeError('Message cannot be empty.')
        self._set_and_remove_tags(tags)
        log_message, level = self._get_logged_test_message_and_level(message)
        self.log('Execution passed with message:\n%s' % log_message, level)
        raise PassExecution(message)

    @run_keyword_variant(resolve=1)
    def pass_execution_if(self, condition, message, *tags):
        """Conditionally skips rest of the current test, setup, or teardown with PASS status.

        A wrapper for `Pass Execution` to skip rest of the current test,
        setup or teardown based the given ``condition``. The condition is
        evaluated similarly as with `Should Be True` keyword, and ``message``
        and ``*tags`` have same semantics as with `Pass Execution`.

        Example:
        | :FOR | ${var}            | IN                     | @{VALUES}               |
        |      | Pass Execution If | '${var}' == 'EXPECTED' | Correct value was found |
        |      | Do Something      | ${var}                 |

        New in Robot Framework 2.8.
        """
        if self._is_true(condition):
            message = self._variables.replace_string(message)
            tags = [self._variables.replace_string(tag) for tag in tags]
            self.pass_execution(message, *tags)


class _Misc(_BuiltInBase):

    def no_operation(self):
        """Does absolutely nothing."""

    def sleep(self, time_, reason=None):
        """Pauses the test executed for the given time.

        ``time`` may be either a number or a time string. Time strings are in
        a format such as ``1 day 2 hours 3 minutes 4 seconds 5milliseconds`` or
        ``1d 2h 3m 4s 5ms``, and they are fully explained in an appendix of
        Robot Framework User Guide. Optional `reason` can be used to explain why
        sleeping is necessary. Both the time slept and the reason are logged.

        Examples:
        | Sleep | 42                   |
        | Sleep | 1.5                  |
        | Sleep | 2 minutes 10 seconds |
        | Sleep | 10s                  | Wait for a reply |
        """
        seconds = timestr_to_secs(time_)
        # Python hangs with negative values
        if seconds < 0:
            seconds = 0
        self._sleep_in_parts(seconds)
        self.log('Slept %s' % secs_to_timestr(seconds))
        if reason:
            self.log(reason)

    def _sleep_in_parts(self, seconds):
        # time.sleep can't be stopped in windows
        # to ensure that we can signal stop (with timeout)
        # split sleeping to small pieces
        endtime = time.time() + float(seconds)
        while True:
            remaining = endtime - time.time()
            if remaining <= 0:
                break
            time.sleep(min(remaining, 0.5))

    def catenate(self, *items):
        """Catenates the given items together and returns the resulted string.

        By default, items are catenated with spaces, but if the first item
        contains the string ``SEPARATOR=<sep>``, the separator ``<sep>`` is
        used instead. Items are converted into strings when necessary.

        Examples:
        | ${str1} = | Catenate | Hello         | world |       |
        | ${str2} = | Catenate | SEPARATOR=--- | Hello | world |
        | ${str3} = | Catenate | SEPARATOR=    | Hello | world |
        =>
        | ${str1} = 'Hello world'
        | ${str2} = 'Hello---world'
        | ${str3} = 'Helloworld'
        """
        if not items:
            return ''
        items = [unic(item) for item in items]
        if items[0].startswith('SEPARATOR='):
            sep = items[0][len('SEPARATOR='):]
            items = items[1:]
        else:
            sep = ' '
        return sep.join(items)

    def log(self, message, level='INFO', html=False, console=False, repr=False):
        u"""Logs the given message with the given level.

        Valid levels are TRACE, DEBUG, INFO (default), HTML, WARN, and ERROR.
        Messages below the current active log level are ignored. See
        `Set Log Level` keyword and ``--loglevel`` command line option
        for more details about setting the level.

        Messages logged with the WARN or ERROR levels will be automatically
        visible also in the console and in the Test Execution Errors section
        in the log file.

        Logging can be configured using optional ``html``, ``console`` and
        ``repr`` arguments. They are off by default, but can be enabled
        by giving them a true value. See `Boolean arguments` section for more
        information about true and false values.

        If the ``html`` argument is given a true value, the message will be
        considered HTML and special characters such as ``<`` in it are not
        escaped. For example, logging ``<img src="image.png">`` creates an
        image when ``html`` is true, but otherwise the message is that exact
        string. An alternative to using the ``html`` argument is using the HTML
        pseudo log level. It logs the message as HTML using the INFO level.

        If the ``console`` argument is true, the message will be written to
        the console where test execution was started from in addition to
        the log file. This keyword always uses the standard output stream
        and adds a newline after the written message. Use `Log To Console`
        instead if either of these is undesirable,

        If the ``repr`` argument is true, the given item will be passed through
        a custom version of Python's ``pprint.pformat()`` function before
        logging it. This is useful, for example, when working with strings or
        bytes containing invisible characters, or when working with nested data
        structures. The custom version differs from the standard one so that it
        omits the ``u`` prefix from Unicode strings and adds ``b`` prefix to
        byte strings.

        Examples:
        | Log | Hello, world!        |          |   | # Normal INFO message.   |
        | Log | Warning, world!      | WARN     |   | # Warning.               |
        | Log | <b>Hello</b>, world! | html=yes |   | # INFO message as HTML.  |
        | Log | <b>Hello</b>, world! | HTML     |   | # Same as above.         |
        | Log | <b>Hello</b>, world! | DEBUG    | html=true | # DEBUG as HTML. |
        | Log | Hello, console!   | console=yes | | # Log also to the console. |
        | Log | Hyv\xe4 \\x00     | repr=yes    | | # Log ``'Hyv\\xe4 \\x00'``. |

        See `Log Many` if you want to log multiple messages in one go, and
        `Log To Console` if you only want to write to the console.

        Arguments ``html``, ``console``, and ``repr`` are new in Robot Framework
        2.8.2.

        Pprint support when ``repr`` is used is new in Robot Framework 2.8.6,
        and it was changed to drop the ``u`` prefix and add the ``b`` prefix
        in Robot Framework 2.9.
        """
        if is_truthy(repr):
            message = prepr(message, width=80)
        logger.write(message, level, is_truthy(html))
        if is_truthy(console):
            logger.console(message)

    @run_keyword_variant(resolve=0)
    def log_many(self, *messages):
        """Logs the given messages as separate entries using the INFO level.

        Supports also logging list and dictionary variable items individually.

        Examples:
        | Log Many | Hello   | ${var}  |
        | Log Many | @{list} | &{dict} |

        See `Log` and `Log To Console` keywords if you want to use alternative
        log levels, use HTML, or log to the console.
        """
        for msg in self._yield_logged_messages(messages):
            self.log(msg)

    def _yield_logged_messages(self, messages):
        for msg in messages:
            var = VariableSplitter(msg)
            value = self._variables.replace_scalar(msg)
            if var.is_list_variable():
                for item in value:
                    yield item
            elif var.is_dict_variable():
                for name, value in value.items():
                    yield '%s=%s' % (name, value)
            else:
                yield value

    def log_to_console(self, message, stream='STDOUT', no_newline=False):
        """Logs the given message to the console.

        By default uses the standard output stream. Using the standard error
        stream is possibly by giving the ``stream`` argument value ``STDERR``
        (case-insensitive).

        By default appends a newline to the logged message. This can be
        disabled by giving the ``no_newline`` argument a true value (see
        `Boolean arguments`).

        Examples:
        | Log To Console | Hello, console!             |                 |
        | Log To Console | Hello, stderr!              | STDERR          |
        | Log To Console | Message starts here and is  | no_newline=true |
        | Log To Console | continued without newline.  |                 |

        This keyword does not log the message to the normal log file. Use
        `Log` keyword, possibly with argument ``console``, if that is desired.

        New in Robot Framework 2.8.2.
        """
        logger.console(message, newline=is_falsy(no_newline), stream=stream)

    @run_keyword_variant(resolve=0)
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
        ``--loglevel``.

        The available levels: TRACE, DEBUG, INFO (default), WARN, ERROR and NONE (no
        logging).
        """
        try:
            old = self._context.output.set_log_level(level)
        except DataError as err:
            raise RuntimeError(unicode(err))
        self._namespace.variables.set_global('${LOG_LEVEL}', level.upper())
        self.log('Log level changed from %s to %s' % (old, level.upper()))
        return old

    def reload_library(self, name_or_instance):
        """Rechecks what keywords the specified library provides.

        Can be called explicitly in the test data or by a library itself
        when keywords it provides have changed.

        The library can be specified by its name or as the active instance of
        the library. The latter is especially useful if the library itself
        calls this keyword as a method.

        New in Robot Framework 2.9.
        """
        library = self._namespace.reload_library(name_or_instance)
        self.log('Reloaded library %s with %s keywords.' % (library.name,
                                                            len(library)))

    @run_keyword_variant(resolve=0)
    def import_library(self, name, *args):
        """Imports a library with the given name and optional arguments.

        This functionality allows dynamic importing of libraries while tests
        are running. That may be necessary, if the library itself is dynamic
        and not yet available when test data is processed. In a normal case,
        libraries should be imported using the Library setting in the Setting
        table.

        This keyword supports importing libraries both using library
        names and physical paths. When paths are used, they must be
        given in absolute format. Forward slashes can be used as path
        separators in all operating systems.

        It is possible to pass arguments to the imported library and also
        named argument syntax works if the library supports it. ``WITH NAME``
        syntax can be used to give a custom name to the imported library.

        Examples:
        | Import Library | MyLibrary |
        | Import Library | ${CURDIR}/../Library.py | arg1 | named=arg2 |
        | Import Library | ${LIBRARIES}/Lib.java | arg | WITH NAME | JavaLib |
        """
        try:
            self._namespace.import_library(name, list(args))
        except DataError as err:
            raise RuntimeError(unicode(err))

    @run_keyword_variant(resolve=0)
    def import_variables(self, path, *args):
        """Imports a variable file with the given path and optional arguments.

        Variables imported with this keyword are set into the test suite scope
        similarly when importing them in the Setting table using the Variables
        setting. These variables override possible existing variables with
        the same names. This functionality can thus be used to import new
        variables, for example, for each test in a test suite.

        The given path must be absolute. Forward slashes can be used as path
        separator regardless the operating system.

        Examples:
        | Import Variables | ${CURDIR}/variables.py   |      |      |
        | Import Variables | ${CURDIR}/../vars/env.py | arg1 | arg2 |
        """
        try:
            self._namespace.import_variables(path, list(args), overwrite=True)
        except DataError as err:
            raise RuntimeError(unicode(err))

    @run_keyword_variant(resolve=0)
    def import_resource(self, path):
        """Imports a resource file with the given path.

        Resources imported with this keyword are set into the test suite scope
        similarly when importing them in the Setting table using the Resource
        setting.

        The given path must be absolute. Forward slashes can be used as path
        separator regardless the operating system.

        Examples:
        | Import Resource | ${CURDIR}/resource.txt |
        | Import Resource | ${CURDIR}/../resources/resource.html |
        """
        try:
            self._namespace.import_resource(path)
        except DataError as err:
            raise RuntimeError(unicode(err))

    def set_library_search_order(self, *search_order):
        """Sets the resolution order to use when a name matches multiple keywords.

        The library search order is used to resolve conflicts when a keyword
        name in the test data matches multiple keywords. The first library
        (or resource, see below) containing the keyword is selected and that
        keyword implementation used. If the keyword is not found from any library
        (or resource), test executing fails the same way as when the search
        order is not set.

        When this keyword is used, there is no need to use the long
        ``LibraryName.Keyword Name`` notation.  For example, instead of
        having

        | MyLibrary.Keyword | arg |
        | MyLibrary.Another Keyword |
        | MyLibrary.Keyword | xxx |

        you can have

        | Set Library Search Order | MyLibrary |
        | Keyword | arg |
        | Another Keyword |
        | Keyword | xxx |

        This keyword can be used also to set the order of keywords in different
        resource files. In this case resource names must be given without paths
        or extensions like:

        | Set Library Search Order | resource | another_resource |

        *NOTE:*
        - The search order is valid only in the suite where this keywords is used.
        - Keywords in resources always have higher priority than
          keywords in libraries regardless the search order.
        - The old order is returned and can be used to reset the search order later.
        - Library and resource names in the search order are both case and space
          insensitive.
        """
        return self._namespace.set_search_order(search_order)

    def keyword_should_exist(self, name, msg=None):
        """Fails unless the given keyword exists in the current scope.

        Fails also if there are more than one keywords with the same name.
        Works both with the short name (e.g. ``Log``) and the full name
        (e.g. ``BuiltIn.Log``).

        The default error message can be overridden with the ``msg`` argument.

        See also `Variable Should Exist`.
        """
        try:
            handler = self._namespace.get_handler(name)
            if isinstance(handler, UserErrorHandler):
                handler.run()
        except DataError as err:
            raise AssertionError(msg or unicode(err))

    def get_time(self, format='timestamp', time_='NOW'):
        """Returns the given time in the requested format.

        *NOTE:* DateTime library added in Robot Framework 2.8.5 contains
        much more flexible keywords for getting the current date and time
        and for date and time handling in general.

        How time is returned is determined based on the given ``format``
        string as follows. Note that all checks are case-insensitive.

        1) If ``format`` contains the word ``epoch``, the time is returned
           in seconds after the UNIX epoch (1970-01-01 00:00:00 UTC).
           The return value is always an integer.

        2) If ``format`` contains any of the words ``year``, ``month``,
           ``day``, ``hour``, ``min``, or ``sec``, only the selected parts are
           returned. The order of the returned parts is always the one
           in the previous sentence and the order of words in ``format``
           is not significant. The parts are returned as zero-padded
           strings (e.g. May -> ``05``).

        3) Otherwise (and by default) the time is returned as a
           timestamp string in the format ``2006-02-24 15:08:31``.

        By default this keyword returns the current local time, but
        that can be altered using ``time`` argument as explained below.
        Note that all checks involving strings are case-insensitive.

        1) If ``time`` is a number, or a string that can be converted to
           a number, it is interpreted as seconds since the UNIX epoch.
           This documentation was originally written about 1177654467
           seconds after the epoch.

        2) If ``time`` is a timestamp, that time will be used. Valid
           timestamp formats are ``YYYY-MM-DD hh:mm:ss`` and
           ``YYYYMMDD hhmmss``.

        3) If ``time`` is equal to ``NOW`` (default), the current local
           time is used. This time is got using Python's ``time.time()``
           function.

        4) If ``time`` is equal to ``UTC``, the current time in
           [http://en.wikipedia.org/wiki/Coordinated_Universal_Time|UTC]
           is used. This time is got using ``time.time() + time.altzone``
           in Python.

        5) If ``time`` is in the format like ``NOW - 1 day`` or ``UTC + 1 hour
           30 min``, the current local/UTC time plus/minus the time
           specified with the time string is used. The time string format
           is described in an appendix of Robot Framework User Guide.

        Examples (expecting the current local time is 2006-03-29 15:06:21):
        | ${time} = | Get Time |             |  |  |
        | ${secs} = | Get Time | epoch       |  |  |
        | ${year} = | Get Time | return year |  |  |
        | ${yyyy}   | ${mm}    | ${dd} =     | Get Time | year,month,day |
        | @{time} = | Get Time | year month day hour min sec |  |  |
        | ${y}      | ${s} =   | Get Time    | seconds and year |  |
        =>
        | ${time} = '2006-03-29 15:06:21'
        | ${secs} = 1143637581
        | ${year} = '2006'
        | ${yyyy} = '2006', ${mm} = '03', ${dd} = '29'
        | @{time} = ['2006', '03', '29', '15', '06', '21']
        | ${y} = '2006'
        | ${s} = '21'

        Examples (expecting the current local time is 2006-03-29 15:06:21 and
        UTC time is 2006-03-29 12:06:21):
        | ${time} = | Get Time |              | 1177654467          | # Time given as epoch seconds        |
        | ${secs} = | Get Time | sec          | 2007-04-27 09:14:27 | # Time given as a timestamp          |
        | ${year} = | Get Time | year         | NOW                 | # The local time of execution        |
        | @{time} = | Get Time | hour min sec | NOW + 1h 2min 3s    | # 1h 2min 3s added to the local time |
        | @{utc} =  | Get Time | hour min sec | UTC                 | # The UTC time of execution          |
        | ${hour} = | Get Time | hour         | UTC - 1 hour        | # 1h subtracted from the UTC  time   |
        =>
        | ${time} = '2007-04-27 09:14:27'
        | ${secs} = 27
        | ${year} = '2006'
        | @{time} = ['16', '08', '24']
        | @{utc} = ['12', '06', '21']
        | ${hour} = '11'

        Support for UTC time was added in Robot Framework 2.7.5 but it did not
        work correctly until 2.7.7.
        """
        return get_time(format, parse_time(time_))

    def evaluate(self, expression, modules=None, namespace=None):
        """Evaluates the given expression in Python and returns the results.

        ``modules`` argument can be used to specify a comma separated
        list of Python modules to be imported and added to the
        namespace of the evaluated ``expression``.

        ``namespace`` argument can be used to pass a custom namespace as
        a dictionary. Possible ``modules`` are added to this namespace.

        When variables are used in the expression with the normal variable
        decoration (e.g. ``${var}``), they will be replaced by their string
        representation before evaluation. Variables that are to be evaluated
        as strings must thus be quoted with single or double quotes (e.g.
        ``"${var}"``). If the variable may contain newlines or quotes, Python's
        triple quoting can be used instead (e.g. ``'''${var}'''``).

        Examples (expecting ``${result}`` is 3.14):
        | ${status} = | Evaluate | 0 < ${result} < 10    | # Would also work with string '3.14' |
        | ${down} =   | Evaluate | int(${result})        |
        | ${up} =     | Evaluate | math.ceil(${result})  | math                |
        | ${random} = | Evaluate | random.randint(0, sys.maxint) | random, sys |
        | ${ns} =     | Create Dictionary | x=${4}       | y=${2}              |
        | ${result} = | Evaluate | x*10 + y              | namespace=${ns}     |
        =>
        | ${status} = True
        | ${down} = 3
        | ${up} = 4.0
        | ${random} = <random integer>
        | ${result} = 42

        All current variables are available in the evaluation namespace
        automatically also without the ``${}`` decoration (e.g. ``var``).
        When used like this, variables are evaluated within the expression
        with their actual value. They must not be quoted even if they would
        contain strings. Variables do not override Python built-ins
        (e.g. ``len``) nor the given ``modules`` or ``namespace``.

        Examples (expecting ``${text}`` is ``'Hello Kitty'``):
        | ${length} = | Evaluate | len(text)    |
        | @{parts} =  | Evaluate | text.split() |
        | ${comp} =   | Evaluate | text == '${text}' |
        =>
        | ${length} = 11
        | ${parts} = ['Hello', 'Kitty']
        | ${comp} = True

        Notice that instead of creating complicated expressions, it is
        recommended to move the logic into a test library.

        Support for ``namespace`` is new in Robot Framework 2.8.4 and
        variables without decoration in the evaluation namespace in 2.9.
        """
        namespace = dict(namespace) if namespace else {}
        modules = modules.replace(' ', '').split(',') if modules else []
        namespace.update((m, __import__(m)) for m in modules if m)
        variables = self._variables.as_dict(decoration=False)
        for key in dir(__builtin__) + list(namespace):
            if key in variables:
                variables.pop(key)
        try:
            if not isinstance(expression, basestring):
                raise TypeError("Expression must be string, got %s."
                                % type_name(expression))
            if not expression:
                raise ValueError("Expression cannot be empty.")
            return eval(expression, namespace, variables)
        except:
            raise RuntimeError("Evaluating expression '%s' failed: %s"
                               % (expression, get_error_message()))

    def call_method(self, object, method_name, *args, **kwargs):
        """Calls the named method of the given object with the provided arguments.

        The possible return value from the method is returned and can be
        assigned to a variable. Keyword fails both if the object does not have
        a method with the given name or if executing the method raises an
        exception.

        Support for ``**kwargs`` is new in Robot Framework 2.9. Since that
        possible equal signs in other arguments must be escaped with a
        backslash like ``\\=``.

        Examples:
        | Call Method      | ${hashtable} | put          | myname  | myvalue |
        | ${isempty} =     | Call Method  | ${hashtable} | isEmpty |         |
        | Should Not Be True | ${isempty} |              |         |         |
        | ${value} =       | Call Method  | ${hashtable} | get     | myname  |
        | Should Be Equal  | ${value}     | myvalue      |         |         |
        | Call Method      | ${object}    | kwargs    | name=value | foo=bar |
        | Call Method      | ${object}    | positional   | escaped\\=equals  |
        """
        try:
            method = getattr(object, method_name)
        except AttributeError:
            raise RuntimeError("Object '%s' does not have method '%s'."
                               % (object, method_name))
        try:
            return method(*args, **kwargs)
        except:
            raise RuntimeError("Calling method '%s' failed: %s"
                               % (method_name, get_error_message()))

    def regexp_escape(self, *patterns):
        """Returns each argument string escaped for use as a regular expression.

        This keyword can be used to escape strings to be used with
        `Should Match Regexp` and `Should Not Match Regexp` keywords.

        Escaping is done with Python's ``re.escape()`` function.

        Examples:
        | ${escaped} = | Regexp Escape | ${original} |
        | @{strings} = | Regexp Escape | @{strings}  |
        """
        if len(patterns) == 0:
            return ''
        if len(patterns) == 1:
            return re.escape(patterns[0])
        return [re.escape(p) for p in patterns]

    def set_test_message(self, message, append=False):
        """Sets message for the current test case.

        If the optional ``append`` argument is given a true value (see `Boolean
        arguments`), the given ``message`` is added after the possible earlier
        message by joining the messages with a space.

        In test teardown this keyword can alter the possible failure message,
        but otherwise failures override messages set by this keyword. Notice
        that in teardown the initial message is available as a built-in variable
        ``${TEST MESSAGE}``.

        It is possible to use HTML format in the message by starting the message
        with ``*HTML*``.

        Examples:
        | Set Test Message | My message           |                          |
        | Set Test Message | is continued.        | append=yes               |
        | Should Be Equal  | ${TEST MESSAGE}      | My message is continued. |
        | Set Test Message | `*`HTML`*` <b>Hello!</b> |                      |

        This keyword can not be used in suite setup or suite teardown.

        Support for ``append`` was added in Robot Framework 2.7.7 and support
        for HTML format in 2.8.
        """
        test = self._namespace.test
        if not test:
            raise RuntimeError("'Set Test Message' keyword cannot be used in "
                               "suite setup or teardown.")
        test.message = self._get_possibly_appended_value(test.message, message,
                                                         append)
        message, level = self._get_logged_test_message_and_level(test.message)
        self.log('Set test message to:\n%s' % message, level)

    def _get_possibly_appended_value(self, initial, new, append):
        if not isinstance(new, unicode):
            new = unic(new)
        if is_truthy(append) and initial:
            return '%s %s' % (initial, new)
        return new

    def _get_logged_test_message_and_level(self, message):
        if message.startswith('*HTML*'):
            return message[6:].lstrip(), 'HTML'
        return message, 'INFO'

    def set_test_documentation(self, doc, append=False):
        """Sets documentation for the current test case.

        By default the possible existing documentation is overwritten, but
        this can be changed using the optional ``append`` argument similarly
        as with `Set Test Message` keyword.

        The current test documentation is available as a built-in variable
        ``${TEST DOCUMENTATION}``. This keyword can not be used in suite
        setup or suite teardown.

        New in Robot Framework 2.7. Support for ``append`` was added in 2.7.7.
        """
        test = self._namespace.test
        if not test:
            raise RuntimeError("'Set Test Documentation' keyword cannot be "
                               "used in suite setup or teardown.")
        test.doc = self._get_possibly_appended_value(test.doc, doc, append)
        self._variables.set_test('${TEST_DOCUMENTATION}', test.doc)
        self.log('Set test documentation to:\n%s' % test.doc)

    def set_suite_documentation(self, doc, append=False, top=False):
        """Sets documentation for the current test suite.

        By default the possible existing documentation is overwritten, but
        this can be changed using the optional ``append`` argument similarly
        as with `Set Test Message` keyword.

        This keyword sets the documentation of the current suite by default.
        If the optional ``top`` argument is given a true value (see `Boolean
        arguments`), the documentation of the top level suite is altered
        instead.

        The documentation of the current suite is available as a built-in
        variable ``${SUITE DOCUMENTATION}``.

        New in Robot Framework 2.7. Support for ``append`` and ``top`` were
        added in 2.7.7.
        """
        top = is_truthy(top)
        suite = self._get_namespace(top).suite
        suite.doc = self._get_possibly_appended_value(suite.doc, doc, append)
        self._variables.set_suite('${SUITE_DOCUMENTATION}', suite.doc, top)
        self.log('Set suite documentation to:\n%s' % suite.doc)

    def set_suite_metadata(self, name, value, append=False, top=False):
        """Sets metadata for the current test suite.

        By default possible existing metadata values are overwritten, but
        this can be changed using the optional ``append`` argument similarly
        as with `Set Test Message` keyword.

        This keyword sets the metadata of the current suite by default.
        If the optional ``top`` argument is given a true value (see `Boolean
        arguments`), the metadata of the top level suite is altered instead.

        The metadata of the current suite is available as a built-in variable
        ``${SUITE METADATA}`` in a Python dictionary. Notice that modifying this
        variable directly has no effect on the actual metadata the suite has.

        New in Robot Framework 2.7.4. Support for ``append`` and ``top`` were
        added in 2.7.7.
        """
        top = is_truthy(top)
        if not isinstance(name, unicode):
            name = unic(name)
        metadata = self._get_namespace(top).suite.metadata
        original = metadata.get(name, '')
        metadata[name] = self._get_possibly_appended_value(original, value, append)
        self._variables.set_suite('${SUITE_METADATA}', metadata.copy(), top)
        self.log("Set suite metadata '%s' to value '%s'." % (name, metadata[name]))

    def set_tags(self, *tags):
        """Adds given ``tags`` for the current test or all tests in a suite.

        When this keyword is used inside a test case, that test gets
        the specified tags and other tests are not affected.

        If this keyword is used in a suite setup, all test cases in
        that suite, recursively, gets the given tags. It is a failure
        to use this keyword in a suite teardown.

        The current tags are available as a built-in variable ``@{TEST TAGS}``.

        See `Remove Tags` if you want to remove certain tags and `Fail` if
        you want to fail the test case after setting and/or removing tags.
        """
        ctx = self._context
        if ctx.test:
            ctx.test.tags.add(tags)
            ctx.variables.set_test('@{TEST_TAGS}', list(ctx.test.tags))
        elif not ctx.in_suite_teardown:
            ctx.suite.set_tags(tags, persist=True)
        else:
            raise RuntimeError("'Set Tags' cannot be used in suite teardown.")
        self.log('Set tag%s %s.' % (s(tags), seq2str(tags)))

    def remove_tags(self, *tags):
        """Removes given ``tags`` from the current test or all tests in a suite.

        Tags can be given exactly or using a pattern where ``*`` matches
        anything and ``?`` matches one character.

        This keyword can affect either one test case or all test cases in a
        test suite similarly as `Set Tags` keyword.

        The current tags are available as a built-in variable ``@{TEST TAGS}``.

        Example:
        | Remove Tags | mytag | something-* | ?ython |

        See `Set Tags` if you want to add certain tags and `Fail` if you want
        to fail the test case after setting and/or removing tags.
        """
        ctx = self._context
        if ctx.test:
            ctx.test.tags.remove(tags)
            ctx.variables.set_test('@{TEST_TAGS}', list(ctx.test.tags))
        elif not ctx.in_suite_teardown:
            ctx.suite.set_tags(remove=tags, persist=True)
        else:
            raise RuntimeError("'Remove Tags' cannot be used in suite teardown.")
        self.log('Removed tag%s %s.' % (s(tags), seq2str(tags)))

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
        library is imported with a custom name, the ``name`` used to get
        the instance must be that name and not the original library name.
        """
        try:
            return self._namespace.get_library_instance(name)
        except DataError as err:
            raise RuntimeError(unicode(err))


class BuiltIn(_Verify, _Converter, _Variables, _RunKeyword, _Control, _Misc):
    """An always available standard library with often needed keywords.

    ``BuiltIn`` is Robot Framework's standard library that provides a set
    of generic keywords needed often. It is imported automatically and
    thus always available. The provided keywords can be used, for example,
    for verifications (e.g. `Should Be Equal`, `Should Contain`),
    conversions (e.g. `Convert To Integer`) and for various other purposes
    (e.g. `Log`, `Sleep`, `Run Keyword If`, `Set Global Variable`).

    = HTML error messages =

    Many of the keywords accept an optional error message to use if the keyword
    fails. Starting from Robot Framework 2.8, it is possible to use HTML in
    these messages by prefixing them with ``*HTML*``. See `Fail` keyword for
    a usage example. Notice that using HTML in messages is not limited to
    BuiltIn library but works with any error message.

    = Boolean arguments =

    Some keywords accept arguments that are handled as Boolean values true or
    false. If such an argument is given as a string, it is considered false if
    it is either empty or case-insensitively equal to ``false`` or ``no``.
    Keywords verifying something that allow dropping actual and expected values
    from the possible error message also consider string ``no values`` as false.
    Other strings are considered true regardless their value, and other
    argument types are tested using same
    [http://docs.python.org/2/library/stdtypes.html#truth-value-testing|rules
    as in Python].

    True examples:
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=True    | # Strings are generally true.    |
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=yes     | # Same as the above.             |
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=${TRUE} | # Python ``True`` is true.       |
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=${42}   | # Numbers other than 0 are true. |


    False examples:
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=False     | # String ``false`` is false.   |
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=no        | # Also string ``no`` is false. |
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=${EMPTY}  | # Empty string is false.       |
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=${FALSE}  | # Python ``False`` is false.   |
    | `Should Be Equal` | ${x} | ${y}  | Custom error | values=no values | # ``no values`` works with ``values`` argument |

    Note that prior to Robot Framework 2.9 some keywords considered all
    non-empty strings, including ``false`` and ``no``, to be true.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()


class RobotNotRunningError(AttributeError):
    """Used when something cannot be done because Robot is not running.

    Based on AttributeError to be backwards compatible with RF < 2.8.5.
    May later be based directly on Exception, so new code should except
    this exception explicitly.
    """
    pass


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

    Keywords executed by registered run keywords can be tested in dry-run mode
    if they have 'name' argument which takes the name of the executed keyword.

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


[register_run_keyword('BuiltIn', getattr(_RunKeyword, a))
 for a in dir(_RunKeyword) if a[0] != '_']
