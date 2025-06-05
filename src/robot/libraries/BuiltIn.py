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

import difflib
import re
import time
from collections import OrderedDict
from collections.abc import Sequence

from robot.api import logger, SkipExecution
from robot.api.deco import keyword
from robot.errors import (
    BreakLoop, ContinueLoop, DataError, ExecutionFailed, ExecutionFailures,
    ExecutionPassed, PassExecution, ReturnFromKeyword, VariableError
)
from robot.running import Keyword, RUN_KW_REGISTER, TypeInfo
from robot.running.context import EXECUTION_CONTEXTS
from robot.utils import (
    DotDict, escape, format_assign_message, get_error_message, get_time, html_escape,
    is_falsy, is_list_like, is_truthy, Matcher, normalize, normalize_whitespace,
    parse_re_flags, parse_time, plural_or_not as s, prepr, safe_str, secs_to_timestr,
    seq2str, split_from_equals, timestr_to_secs, unescape
)
from robot.utils.asserts import assert_equal, assert_not_equal
from robot.variables import (
    DictVariableResolver, evaluate_expression, is_dict_variable, is_list_variable,
    search_variable, VariableResolver
)
from robot.version import get_version

# FIXME: Clean-up registering run keyword variants!
# https://github.com/robotframework/robotframework/issues/2190


def run_keyword_variant(resolve, dry_run=False):
    def decorator(method):
        RUN_KW_REGISTER.register_run_keyword(
            "BuiltIn",
            method.__name__,
            resolve,
            deprecation_warning=False,
            dry_run=dry_run,
        )
        return method

    return decorator


class _BuiltInBase:

    @property
    def robot_running(self) -> bool:
        """Return True/False depending on is Robot Framework running or not.

        Can be used by libraries and other extensions.

        New in Robot Framework 6.1.
        """
        return EXECUTION_CONTEXTS.current is not None

    @property
    def dry_run_active(self) -> bool:
        """Return True/False depending on is dry-run active or not.

        Can be used by libraries and other extensions. Notice that library
        keywords are not run at all in dry-run, but library ``__init__``
        can utilize this information.

        New in Robot Framework 6.1.
        """
        return self.robot_running and self._context.dry_run

    @property
    def _context(self):
        return self._get_context()

    def _get_context(self, top=False):
        ctx = EXECUTION_CONTEXTS.current if not top else EXECUTION_CONTEXTS.top
        if ctx is None:
            raise RobotNotRunningError("Cannot access execution context")
        return ctx

    @property
    def _namespace(self):
        return self._get_context().namespace

    @property
    def _variables(self):
        return self._namespace.variables

    def _matches(self, string, pattern, caseless=False):
        # Must use this instead of fnmatch when string may contain newlines.
        matcher = Matcher(pattern, caseless=caseless, spaceless=False)
        return matcher.match(string)

    def _is_true(self, condition):
        if isinstance(condition, str):
            condition = self.evaluate(condition)
        return bool(condition)

    def _log_types(self, *args):
        self._log_types_at_level("DEBUG", *args)

    def _log_types_at_level(self, level, *args):
        msg = ["Argument types are:"] + [self._get_type(a) for a in args]
        self.log("\n".join(msg), level)

    def _get_type(self, arg):
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
            item, base = self._get_base(orig, base)
            if base:
                return int(item, self._convert_to_integer(base))
            return int(item)
        except Exception:
            raise RuntimeError(
                f"'{orig}' cannot be converted to an integer: {get_error_message()}"
            )

    def _get_base(self, item, base):
        if not isinstance(item, str):
            return item, base
        item = normalize(item)
        if item.startswith(("-", "+")):
            sign = item[0]
            item = item[1:]
        else:
            sign = ""
        bases = {"0b": 2, "0o": 8, "0x": 16}
        if base or not item.startswith(tuple(bases)):
            return sign + item, base
        return sign + item[2:], bases[item[:2]]

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
        return self._convert_to_bin_oct_hex(item, base, prefix, length, "b")

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
        return self._convert_to_bin_oct_hex(item, base, prefix, length, "o")

    def convert_to_hex(
        self,
        item,
        base=None,
        prefix=None,
        length=None,
        lowercase=False,
    ):
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
        spec = "x" if lowercase else "X"
        return self._convert_to_bin_oct_hex(item, base, prefix, length, spec)

    def _convert_to_bin_oct_hex(self, item, base, prefix, length, format_spec):
        self._log_types(item)
        ret = format(self._convert_to_integer(item, base), format_spec)
        prefix = prefix or ""
        if ret[0] == "-":
            prefix = "-" + prefix
            ret = ret[1:]
        if length:
            ret = ret.rjust(self._convert_to_integer(length), "0")
        return prefix + ret

    def convert_to_number(self, item, precision=None):
        """Converts the given item to a floating point number.

        If the optional ``precision`` is positive or zero, the returned number
        is rounded to that number of decimal digits. Negative precision means
        that the number is rounded to the closest multiple of 10 to the power
        of the absolute precision. If a number is equally close to a certain
        precision, it is always rounded away from zero.

        Examples:
        | ${result} = | Convert To Number | 42.512 |    | # Result is 42.512 |
        | ${result} = | Convert To Number | 42.512 | 1  | # Result is 42.5   |
        | ${result} = | Convert To Number | 42.512 | 0  | # Result is 43.0   |
        | ${result} = | Convert To Number | 42.512 | -1 | # Result is 40.0   |

        Notice that machines generally cannot store floating point numbers
        accurately. This may cause surprises with these numbers in general
        and also when they are rounded. For more information see, for example,
        these resources:

        - http://docs.python.org/tutorial/floatingpoint.html
        - http://randomascii.wordpress.com/2012/02/25/comparing-floating-point-numbers-2012-edition

        If you want to avoid possible problems with floating point numbers,
        you can implement custom keywords using Python's
        [http://docs.python.org/library/decimal.html|decimal] or
        [http://docs.python.org/library/fractions.html|fractions] modules.

        If you need an integer number, use `Convert To Integer` instead.
        """
        self._log_types(item)
        return self._convert_to_number(item, precision)

    def _convert_to_number(self, item, precision=None):
        number = self._convert_to_number_without_precision(item)
        if precision is not None:
            number = float(round(number, self._convert_to_integer(precision)))
        return number

    def _convert_to_number_without_precision(self, item):
        try:
            return float(item)
        except (ValueError, TypeError):
            error = get_error_message()
            try:
                return float(self._convert_to_integer(item))
            except RuntimeError:
                raise RuntimeError(
                    f"'{item}' cannot be converted to a floating point number: {error}"
                )

    def convert_to_string(self, item):
        """Converts the given item to a Unicode string.

        Strings are also [https://en.wikipedia.org/wiki/Unicode_equivalence|
        NFC normalized].

        Use `Encode String To Bytes` and `Decode Bytes To String` keywords
        in ``String`` library if you need to convert between Unicode and byte
        strings using different encodings. Use `Convert To Bytes` if you just
        want to create byte strings.
        """
        self._log_types(item)
        return safe_str(item)

    def convert_to_boolean(self, item):
        """Converts the given item to Boolean true or false.

        Handles strings ``True`` and ``False`` (case-insensitive) as expected,
        otherwise returns item's
        [http://docs.python.org/library/stdtypes.html#truth|truth value]
        using Python's ``bool()`` method.
        """
        self._log_types(item)
        if isinstance(item, str):
            if item.upper() == "TRUE":
                return True
            if item.upper() == "FALSE":
                return False
        return bool(item)

    def convert_to_bytes(self, input, input_type="text"):
        r"""Converts the given ``input`` to bytes according to the ``input_type``.

        Valid input types are listed below:

        - ``text:`` Converts text to bytes character by character. All
          characters with ordinal below 256 can be used and are converted to
          bytes with same values. Many characters are easiest to represent
          using escapes like ``\x00`` or ``\xff``. In practice this is the same
          as Latin-1 encoding.

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
        | ${bytes} = | Convert To Bytes | hyvä      |     | # hyv\xe4      |
        | ${bytes} = | Convert To Bytes | hyv\xe4   |     | # hyv\xe4      |
        | ${bytes} = | Convert To Bytes | \xff\x07  |     | # \xff\x07     |
        | ${bytes} = | Convert To Bytes | 82 70     | int | # RF           |
        | ${bytes} = | Convert To Bytes | 0b10 0x10 | int | # \x02\x10     |
        | ${bytes} = | Convert To Bytes | ff 00 07  | hex | # \xff\x00\x07 |
        | ${bytes} = | Convert To Bytes | 52462121  | hex | # RF!!         |
        | ${bytes} = | Convert To Bytes | 0000 1000 | bin | # \x08         |
        | ${input} = | Create List      | 1         | 2   | 12             |
        | ${bytes} = | Convert To Bytes | ${input}  | int | # \x01\x02\x0c |
        | ${bytes} = | Convert To Bytes | ${input}  | hex | # \x01\x02\x12 |

        Use `Encode String To Bytes` in ``String`` library if you need to
        convert text to bytes using a certain encoding.
        """
        try:
            try:
                get_ordinals = getattr(self, f"_get_ordinals_from_{input_type}")
            except AttributeError:
                raise RuntimeError(f"Invalid input type '{input_type}'.")
            return bytes(o for o in get_ordinals(input))
        except Exception:
            raise RuntimeError("Creating bytes failed: " + get_error_message())

    def _get_ordinals_from_text(self, input):
        for char in input:
            ordinal = char if isinstance(char, int) else ord(char)
            yield self._test_ordinal(ordinal, char, "Character")

    def _test_ordinal(self, ordinal, original, type):
        if 0 <= ordinal <= 255:
            return ordinal
        raise RuntimeError(f"{type} '{original}' cannot be represented as a byte.")

    def _get_ordinals_from_int(self, input):
        if isinstance(input, str):
            input = input.split()
        elif isinstance(input, int):
            input = [input]
        for integer in input:
            ordinal = self._convert_to_integer(integer)
            yield self._test_ordinal(ordinal, integer, "Integer")

    def _get_ordinals_from_hex(self, input):
        for token in self._input_to_tokens(input, length=2):
            ordinal = self._convert_to_integer(token, base=16)
            yield self._test_ordinal(ordinal, token, "Hex value")

    def _get_ordinals_from_bin(self, input):
        for token in self._input_to_tokens(input, length=8):
            ordinal = self._convert_to_integer(token, base=2)
            yield self._test_ordinal(ordinal, token, "Binary value")

    def _input_to_tokens(self, input, length):
        if not isinstance(input, str):
            return input
        input = "".join(input.split())
        if len(input) % length != 0:
            raise RuntimeError(f"Expected input to be multiple of {length}.")
        return (input[i : i + length] for i in range(0, len(input), length))

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
        """Creates and returns a dictionary based on the given ``items``.

        Items are typically given using the ``key=value`` syntax same way as
        ``&{dictionary}`` variables are created in the Variable table. Both
        keys and values can contain variables, and possible equal sign in key
        can be escaped with a backslash like ``escaped\\=key=value``. It is
        also possible to get items from existing dictionaries by simply using
        them like ``&{dict}``.

        Alternatively items can be specified so that keys and values are given
        separately. This and the ``key=value`` syntax can even be combined,
        but separately given items must be first. If same key is used multiple
        times, the last value has precedence.

        The returned dictionary is ordered, and values with strings as keys
        can also be accessed using a convenient dot-access syntax like
        ``${dict.key}``. Technically the returned dictionary is Robot
        Framework's own ``DotDict`` instance. If there is a need, it can be
        converted into a regular Python ``dict`` instance by using the
        `Convert To Dictionary` keyword from the Collections library.

        Examples:
        | &{dict} = | Create Dictionary | key=value | foo=bar | | | # key=value syntax |
        | Should Be True | ${dict} == {'key': 'value', 'foo': 'bar'} |
        | &{dict2} = | Create Dictionary | key | value | foo | bar | # separate key and value |
        | Should Be Equal | ${dict} | ${dict2} |
        | &{dict} = | Create Dictionary | ${1}=${2} | &{dict} | foo=new | | # using variables |
        | Should Be True | ${dict} == {1: 2, 'key': 'value', 'foo': 'new'} |
        | Should Be Equal | ${dict.key} | value | | | | # dot-access |
        """
        separate, combined = self._split_dict_items(items)
        result = DotDict(self._format_separate_dict_items(separate))
        combined = DictVariableResolver(combined).resolve(self._variables)
        result.update(combined)
        return result

    def _split_dict_items(self, items):
        separate = []
        for item in items:
            name, value = split_from_equals(item)
            if value is not None or is_dict_variable(item):
                break
            separate.append(item)
        return separate, items[len(separate) :]

    def _format_separate_dict_items(self, separate):
        separate = self._variables.replace_list(separate)
        if len(separate) % 2 != 0:
            raise DataError(
                f"Expected even number of keys and values, got {len(separate)}."
            )
        return [separate[i : i + 2] for i in range(0, len(separate), 2)]


class _Verify(_BuiltInBase):

    def _set_and_remove_tags(self, tags):
        set_tags = [tag for tag in tags if not tag.startswith("-")]
        remove_tags = [tag[1:] for tag in tags if tag.startswith("-")]
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
        """
        self._set_and_remove_tags(tags)
        raise AssertionError(msg) if msg is not None else AssertionError()

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
        if self._is_true(condition):
            raise AssertionError(msg or f"'{condition}' should not be true.")

    def should_be_true(self, condition, msg=None):
        """Fails if the given condition is not true.

        If ``condition`` is a string (e.g. ``${rc} < 10``), it is evaluated as
        a Python expression as explained in `Evaluating expressions` and the
        keyword status is decided based on the result. If a non-string item is
        given, the status is got directly from its
        [http://docs.python.org/library/stdtypes.html#truth|truth value].

        The default error message (``<condition> should be true``) is not very
        informative, but it can be overridden with the ``msg`` argument.

        Examples:
        | Should Be True | ${rc} < 10            |
        | Should Be True | '${status}' == 'PASS' | # Strings must be quoted |
        | Should Be True | ${number}   | # Passes if ${number} is not zero |
        | Should Be True | ${list}     | # Passes if ${list} is not empty  |

        Variables used like ``${variable}``, as in the examples above, are
        replaced in the expression before evaluation. Variables are also
        available in the evaluation namespace, and can be accessed using
        special ``$variable`` syntax as explained in the `Evaluating
        expressions` section.

        Examples:
        | Should Be True | $rc < 10          |
        | Should Be True | $status == 'PASS' | # Expected string must be quoted |
        """
        if not self._is_true(condition):
            raise AssertionError(msg or f"'{condition}' should be true.")

    def should_be_equal(
        self,
        first,
        second,
        msg=None,
        values=True,
        ignore_case=False,
        formatter="str",
        strip_spaces=False,
        collapse_spaces=False,
        type=None,
        types=None,
    ):
        r"""Fails if the given objects are unequal.

        Optional ``msg``, ``values`` and ``formatter`` arguments specify how
        to construct the error message if this keyword fails:

        - If ``msg`` is not given, the error message is ``<first> != <second>``.
        - If ``msg`` is given and ``values`` gets a true value (default),
          the error message is ``<msg>: <first> != <second>``.
        - If ``msg`` is given and ``values`` gets a false value (see
          `Boolean arguments`), the error message is simply ``<msg>``.
        - ``formatter`` controls how to format the values. Possible values are
          ``str`` (default), ``repr`` and ``ascii``, and they work similarly
          as Python built-in functions with same names. See `String
          representations` for more details.

        If ``ignore_case`` is given a true value (see `Boolean arguments`) and
        both arguments are strings, comparison is done case-insensitively.
        If both arguments are multiline strings, this keyword uses
        `multiline string comparison`.

        If ``strip_spaces`` is given a true value (see `Boolean arguments`)
        and both arguments are strings, the comparison is done without leading
        and trailing spaces. If ``strip_spaces`` is given a string value
        ``LEADING`` or ``TRAILING`` (case-insensitive), the comparison is done
        without leading or trailing spaces, respectively.

        If ``collapse_spaces`` is given a true value (see `Boolean arguments`) and both
        arguments are strings, the comparison is done with all white spaces replaced by
        a single space character.

        The ``type`` and ``types`` arguments control optional type conversion:
        - If ``type`` is used, the argument ``second`` is converted to that type.
          In addition to that, the argument ``first`` is validated to match the type.
        - If ``types`` is used, both ``first`` and ``second`` are converted.
        - Supported types are the same as supported by
          [https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#supported-conversions|
          automatic argument conversion] such as ``int``, ``bytes`` and ``list``.
          Also parameterized types like ``list[int]`` and unions like ``int | float``
          are supported.
        - When using ``type``, a special value ``auto`` can be used to convert
          ``second`` to the same type that ``first`` has.
        - Using both ``type`` and ``types`` at the same time is an error.

        Examples:
        | Should Be Equal | ${x} | expected |
        | Should Be Equal | ${x} | expected | Custom error message |
        | Should Be Equal | ${x} | expected | Custom message | values=False |
        | Should Be Equal | ${x} | expected | ignore_case=True | formatter=repr |
        | Should Be Equal | ${x} | \x00\x01 | type=bytes |
        | Should Be Equal | ${x} | ${y}     | types=int|float |

        ``strip_spaces`` is new in Robot Framework 4.0 and
        ``collapse_spaces`` is new in Robot Framework 4.1.
        ``type`` and ``types`` are new in Robot Framework 7.2.
        """
        if type or types:
            first, second = self._type_convert(first, second, type, types)
        self._log_types_at_info_if_different(first, second)
        if isinstance(first, str) and isinstance(second, str):
            if ignore_case:
                first = first.casefold()
                second = second.casefold()
            if strip_spaces:
                first = self._strip_spaces(first, strip_spaces)
                second = self._strip_spaces(second, strip_spaces)
            if collapse_spaces:
                first = self._collapse_spaces(first)
                second = self._collapse_spaces(second)
        self._should_be_equal(first, second, msg, values, formatter)

    def _type_convert(self, first, second, type, types, type_builtin=type):
        if type and types:
            raise TypeError("Cannot use both 'type' and 'types' arguments.")
        if types:
            type = types
        elif isinstance(type, str) and type.upper() == "AUTO":
            type = type_builtin(first)
        converter = TypeInfo.from_type_hint(type).get_converter()
        if types:
            first = converter.convert(first, "first")
        elif not converter.no_conversion_needed(first):
            raise ValueError(
                f"Argument 'first' got value {first!r} that does not "
                f"match type {type!r}."
            )
        return first, converter.convert(second, "second")

    def _should_be_equal(self, first, second, msg, values, formatter="str"):
        include_values = self._include_values(values)
        formatter = self._get_formatter(formatter)
        if first == second:
            return
        if include_values and isinstance(first, str) and isinstance(second, str):
            self._raise_multi_diff(first, second, msg, formatter)
        assert_equal(first, second, msg, include_values, formatter)

    def _log_types_at_info_if_different(self, first, second):
        level = "DEBUG" if type(first) is type(second) else "INFO"
        self._log_types_at_level(level, first, second)

    def _raise_multi_diff(self, first, second, msg, formatter):
        first_lines = first.splitlines(keepends=True)
        second_lines = second.splitlines(keepends=True)
        if len(first_lines) < 3 or len(second_lines) < 3:
            return
        self.log(f"{first.rstrip()}\n\n!=\n\n{second.rstrip()}")
        diffs = list(
            difflib.unified_diff(
                first_lines,
                second_lines,
                fromfile="first",
                tofile="second",
                lineterm="",
            )
        )
        diffs[3:] = [item[0] + formatter(item[1:]).rstrip() for item in diffs[3:]]
        prefix = "Multiline strings are different:"
        if msg:
            prefix = f"{msg}: {prefix}"
        raise AssertionError("\n".join([prefix, *diffs]))

    def _include_values(self, values):
        return is_truthy(values) and str(values).upper() != "NO VALUES"

    def _strip_spaces(self, value, strip_spaces):
        if not isinstance(value, str):
            return value
        if not isinstance(strip_spaces, str):
            return value.strip() if strip_spaces else value
        if strip_spaces.upper() == "LEADING":
            return value.lstrip()
        if strip_spaces.upper() == "TRAILING":
            return value.rstrip()
        return value.strip() if is_truthy(strip_spaces) else value

    def _collapse_spaces(self, value):
        return re.sub(r"\s+", " ", value) if isinstance(value, str) else value

    def should_not_be_equal(
        self,
        first,
        second,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if the given objects are equal.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.

        If ``ignore_case`` is given a true value (see `Boolean arguments`) and
        both arguments are strings, comparison is done case-insensitively.

        If ``strip_spaces`` is given a true value (see `Boolean arguments`)
        and both arguments are strings, the comparison is done without leading
        and trailing spaces. If ``strip_spaces`` is given a string value
        ``LEADING`` or ``TRAILING`` (case-insensitive), the comparison is done
        without leading or trailing spaces, respectively.

        If ``collapse_spaces`` is given a true value (see `Boolean arguments`) and both
        arguments are strings, the comparison is done with all white spaces replaced by
        a single space character.

        ``strip_spaces`` is new in Robot Framework 4.0 and ``collapse_spaces`` is new
        in Robot Framework 4.1.
        """
        self._log_types_at_info_if_different(first, second)
        if isinstance(first, str) and isinstance(second, str):
            if ignore_case:
                first = first.casefold()
                second = second.casefold()
            if strip_spaces:
                first = self._strip_spaces(first, strip_spaces)
                second = self._strip_spaces(second, strip_spaces)
            if collapse_spaces:
                first = self._collapse_spaces(first)
                second = self._collapse_spaces(second)
        self._should_not_be_equal(first, second, msg, values)

    def _should_not_be_equal(self, first, second, msg, values):
        assert_not_equal(first, second, msg, self._include_values(values))

    def should_not_be_equal_as_integers(
        self,
        first,
        second,
        msg=None,
        values=True,
        base=None,
    ):
        """Fails if objects are equal after converting them to integers.

        See `Convert To Integer` for information how to convert integers from
        other bases than 10 using ``base`` argument or ``0b/0o/0x`` prefixes.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.

        See `Should Be Equal As Integers` for some usage examples.
        """
        self._log_types_at_info_if_different(first, second)
        self._should_not_be_equal(
            self._convert_to_integer(first, base),
            self._convert_to_integer(second, base),
            msg,
            values,
        )

    def should_be_equal_as_integers(
        self,
        first,
        second,
        msg=None,
        values=True,
        base=None,
    ):
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
        self._log_types_at_info_if_different(first, second)
        self._should_be_equal(
            self._convert_to_integer(first, base),
            self._convert_to_integer(second, base),
            msg,
            values,
        )

    def should_not_be_equal_as_numbers(
        self,
        first,
        second,
        msg=None,
        values=True,
        precision=6,
    ):
        """Fails if objects are equal after converting them to real numbers.

        The conversion is done with `Convert To Number` keyword using the
        given ``precision``.

        See `Should Be Equal As Numbers` for examples on how to use
        ``precision`` and why it does not always work as expected. See also
        `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        self._log_types_at_info_if_different(first, second)
        first = self._convert_to_number(first, precision)
        second = self._convert_to_number(second, precision)
        self._should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_numbers(
        self,
        first,
        second,
        msg=None,
        values=True,
        precision=6,
    ):
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

        If you want to avoid possible problems with floating point numbers,
        you can implement custom keywords using Python's
        [http://docs.python.org/library/decimal.html|decimal] or
        [http://docs.python.org/library/fractions.html|fractions] modules.

        See `Should Not Be Equal As Numbers` for a negative version of this
        keyword and `Should Be Equal` for an explanation on how to override
        the default error message with ``msg`` and ``values``.
        """
        self._log_types_at_info_if_different(first, second)
        first = self._convert_to_number(first, precision)
        second = self._convert_to_number(second, precision)
        self._should_be_equal(first, second, msg, values)

    def should_not_be_equal_as_strings(
        self,
        first,
        second,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if objects are equal after converting them to strings.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.

        If ``ignore_case`` is given a true value (see `Boolean arguments`),
        comparison is done case-insensitively.

        If ``strip_spaces`` is given a true value (see `Boolean arguments`)
        and both arguments are strings, the comparison is done without leading
        and trailing spaces. If ``strip_spaces`` is given a string value
        ``LEADING`` or ``TRAILING`` (case-insensitive), the comparison is done
        without leading or trailing spaces, respectively.

        If ``collapse_spaces`` is given a true value (see `Boolean arguments`) and both
        arguments are strings, the comparison is done with all white spaces replaced by
        a single space character.

        Strings are always [https://en.wikipedia.org/wiki/Unicode_equivalence|
        NFC normalized].

        ``strip_spaces`` is new in Robot Framework 4.0 and ``collapse_spaces`` is new
        in Robot Framework 4.1.
        """
        self._log_types_at_info_if_different(first, second)
        first = safe_str(first)
        second = safe_str(second)
        if ignore_case:
            first = first.casefold()
            second = second.casefold()
        if strip_spaces:
            first = self._strip_spaces(first, strip_spaces)
            second = self._strip_spaces(second, strip_spaces)
        if collapse_spaces:
            first = self._collapse_spaces(first)
            second = self._collapse_spaces(second)
        self._should_not_be_equal(first, second, msg, values)

    def should_be_equal_as_strings(
        self,
        first,
        second,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        formatter="str",
        collapse_spaces=False,
    ):
        """Fails if objects are unequal after converting them to strings.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg``, ``values`` and ``formatter``.

        If ``ignore_case`` is given a true value (see `Boolean arguments`),
        comparison is done case-insensitively. If both arguments are
        multiline strings, this keyword uses `multiline string comparison`.

        If ``strip_spaces`` is given a true value (see `Boolean arguments`)
        and both arguments are strings, the comparison is done without leading
        and trailing spaces. If ``strip_spaces`` is given a string value
        ``LEADING`` or ``TRAILING`` (case-insensitive), the comparison is done
        without leading or trailing spaces, respectively.

        If ``collapse_spaces`` is given a true value (see `Boolean arguments`) and both
        arguments are strings, the comparison is done with all white spaces replaced by
        a single space character.

        Strings are always [https://en.wikipedia.org/wiki/Unicode_equivalence|NFC normalized].

        ``strip_spaces`` is new in Robot Framework 4.0
        and ``collapse_spaces`` is new in Robot Framework 4.1.
        """
        self._log_types_at_info_if_different(first, second)
        first = safe_str(first)
        second = safe_str(second)
        if ignore_case:
            first = first.casefold()
            second = second.casefold()
        if strip_spaces:
            first = self._strip_spaces(first, strip_spaces)
            second = self._strip_spaces(second, strip_spaces)
        if collapse_spaces:
            first = self._collapse_spaces(first)
            second = self._collapse_spaces(second)
        self._should_be_equal(first, second, msg, values, formatter)

    def should_not_start_with(
        self,
        str1,
        str2,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if the string ``str1`` starts with the string ``str2``.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``, as well as for semantics
        of the ``ignore_case``, ``strip_spaces``, and ``collapse_spaces`` options.
        """
        if ignore_case:
            str1 = str1.casefold()
            str2 = str2.casefold()
        if strip_spaces:
            str1 = self._strip_spaces(str1, strip_spaces)
            str2 = self._strip_spaces(str2, strip_spaces)
        if collapse_spaces:
            str1 = self._collapse_spaces(str1)
            str2 = self._collapse_spaces(str2)
        if str1.startswith(str2):
            raise AssertionError(
                self._get_string_msg(str1, str2, msg, values, "starts with")
            )

    def should_start_with(
        self,
        str1,
        str2,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if the string ``str1`` does not start with the string ``str2``.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``, as well as for semantics
        of the ``ignore_case``, ``strip_spaces``, and ``collapse_spaces`` options.
        """
        if ignore_case:
            str1 = str1.casefold()
            str2 = str2.casefold()
        if strip_spaces:
            str1 = self._strip_spaces(str1, strip_spaces)
            str2 = self._strip_spaces(str2, strip_spaces)
        if collapse_spaces:
            str1 = self._collapse_spaces(str1)
            str2 = self._collapse_spaces(str2)
        if not str1.startswith(str2):
            raise AssertionError(
                self._get_string_msg(str1, str2, msg, values, "does not start with")
            )

    def should_not_end_with(
        self,
        str1,
        str2,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if the string ``str1`` ends with the string ``str2``.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``, as well as for semantics
        of the ``ignore_case``, ``strip_spaces``, and ``collapse_spaces`` options.
        """
        if ignore_case:
            str1 = str1.casefold()
            str2 = str2.casefold()
        if strip_spaces:
            str1 = self._strip_spaces(str1, strip_spaces)
            str2 = self._strip_spaces(str2, strip_spaces)
        if collapse_spaces:
            str1 = self._collapse_spaces(str1)
            str2 = self._collapse_spaces(str2)
        if str1.endswith(str2):
            raise AssertionError(
                self._get_string_msg(str1, str2, msg, values, "ends with")
            )

    def should_end_with(
        self,
        str1,
        str2,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if the string ``str1`` does not end with the string ``str2``.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``, as well as for semantics
        of the ``ignore_case``, ``strip_spaces``, and ``collapse_spaces`` options.
        """
        if ignore_case:
            str1 = str1.casefold()
            str2 = str2.casefold()
        if strip_spaces:
            str1 = self._strip_spaces(str1, strip_spaces)
            str2 = self._strip_spaces(str2, strip_spaces)
        if collapse_spaces:
            str1 = self._collapse_spaces(str1)
            str2 = self._collapse_spaces(str2)
        if not str1.endswith(str2):
            raise AssertionError(
                self._get_string_msg(str1, str2, msg, values, "does not end with")
            )

    def should_not_contain(
        self,
        container,
        item,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if ``container`` contains ``item`` one or more times.

        Works with strings, lists, and anything that supports Python's ``in``
        operator.

        See `Should Be Equal` for an explanation on how to override the default
        error message with arguments ``msg`` and ``values``. ``ignore_case``
        has exactly the same semantics as with `Should Contain`.

        If ``strip_spaces`` is given a true value (see `Boolean arguments`)
        and both arguments are strings, the comparison is done without leading
        and trailing spaces. If ``strip_spaces`` is given a string value
        ``LEADING`` or ``TRAILING`` (case-insensitive), the comparison is done
        without leading or trailing spaces, respectively.

        If ``collapse_spaces`` is given a true value (see `Boolean arguments`) and both
        arguments are strings, the comparison is done with all white spaces replaced by
        a single space character.

        Examples:
        | Should Not Contain | ${some list} | value  |
        | Should Not Contain | ${output}    | FAILED | ignore_case=True |

        ``strip_spaces`` is new in Robot Framework 4.0 and ``collapse_spaces`` is new
        in Robot Framework 4.1.
        """
        # TODO: It is inconsistent that errors show original case in 'container'
        # 'item' is in lower case. Should rather show original case everywhere
        # and add separate '(case-insensitive)' not to the error message.
        # This same logic should be used with all keywords supporting
        # case-insensitive comparisons.
        orig_container = container
        if ignore_case and isinstance(item, str):
            item = item.casefold()
            if isinstance(container, str):
                container = container.casefold()
            elif is_list_like(container):
                container = {
                    x.casefold() if isinstance(x, str) else x for x in container
                }
        if strip_spaces and isinstance(item, str):
            item = self._strip_spaces(item, strip_spaces)
            if isinstance(container, str):
                container = self._strip_spaces(container, strip_spaces)
            elif is_list_like(container):
                container = {self._strip_spaces(x, strip_spaces) for x in container}
        if collapse_spaces and isinstance(item, str):
            item = self._collapse_spaces(item)
            if isinstance(container, str):
                container = self._collapse_spaces(container)
            elif is_list_like(container):
                container = {self._collapse_spaces(x) for x in container}
        if item in container:
            raise AssertionError(
                self._get_string_msg(orig_container, item, msg, values, "contains")
            )

    def should_contain(
        self,
        container,
        item,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if ``container`` does not contain ``item`` one or more times.

        Works with strings, lists, bytes, and anything that supports Python's ``in``
        operator.

        See `Should Be Equal` for an explanation on how to override the default
        error message with arguments ``msg`` and ``values``.

        If ``ignore_case`` is given a true value (see `Boolean arguments`) and
        compared items are strings, it indicates that comparison should be
        case-insensitive. If the ``container`` is a list-like object, string
        items in it are compared case-insensitively.

        If ``strip_spaces`` is given a true value (see `Boolean arguments`)
        and both arguments are strings, the comparison is done without leading
        and trailing spaces. If ``strip_spaces`` is given a string value
        ``LEADING`` or ``TRAILING`` (case-insensitive), the comparison is done
        without leading or trailing spaces, respectively.

        If ``collapse_spaces`` is given a true value (see `Boolean arguments`) and both
        arguments are strings, the comparison is done with all white spaces replaced by
        a single space character.

        If the ``container`` is bytes and the ``item`` is a string, the ``item``
        is automatically converted to bytes. Conversion is done using the ISO-8859-1
        encoding that maps each Unicode code point directly to a matching byte.

        Examples:
        | Should Contain | ${output}    | PASS  |
        | Should Contain | ${some list} | value | msg=Failure! | values=False |
        | Should Contain | ${some list} | value | ignore_case=True |

        ``strip_spaces`` is new in Robot Framework 4.0, ``collapse_spaces`` is new
        in Robot Framework 4.1 and automatically converting ``item`` to bytes
        is new in Robot Framework 7.1.
        """
        orig_container = container
        if isinstance(container, (bytes, bytearray)):
            if isinstance(item, str):
                try:
                    item = item.encode("ISO-8859-1")
                except UnicodeEncodeError:
                    raise ValueError(f"{item!r} cannot be encoded into bytes.")
            elif isinstance(item, int) and item not in range(256):
                raise ValueError(f"Byte must be in range 0-255, got {item}.")
        if ignore_case and isinstance(item, str):
            item = item.casefold()
            if isinstance(container, str):
                container = container.casefold()
            elif is_list_like(container):
                container = {
                    x.casefold() if isinstance(x, str) else x for x in container
                }
        if strip_spaces and isinstance(item, str):
            item = self._strip_spaces(item, strip_spaces)
            if isinstance(container, str):
                container = self._strip_spaces(container, strip_spaces)
            elif is_list_like(container):
                container = {self._strip_spaces(x, strip_spaces) for x in container}
        if collapse_spaces and isinstance(item, str):
            item = self._collapse_spaces(item)
            if isinstance(container, str):
                container = self._collapse_spaces(container)
            elif is_list_like(container):
                container = {self._collapse_spaces(x) for x in container}
        if item not in container:
            raise AssertionError(
                self._get_string_msg(
                    orig_container,
                    item,
                    msg,
                    values,
                    "does not contain",
                )
            )

    def should_contain_any(
        self,
        container,
        *items,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if ``container`` does not contain any of the ``*items``.

        Works with strings, lists, and anything that supports Python's ``in``
        operator.

        Supports additional configuration parameters ``msg``, ``values``,
        ``ignore_case`` and ``strip_spaces``, and ``collapse_spaces``
        which have exactly the same semantics as arguments with same
        names have with `Should Contain`. These arguments must always
        be given using ``name=value`` syntax after all ``items``.

        Examples:
        | Should Contain Any | ${string} | substring 1 | substring 2 |
        | Should Contain Any | ${list}   | item 1 | item 2 | item 3 |
        | Should Contain Any | ${list}   | item 1 | item 2 | item 3 | ignore_case=True |
        | Should Contain Any | ${list}   | @{items} | msg=Custom message | values=False |
        """
        if not items:
            raise RuntimeError("One or more item required.")
        orig_container = container
        if ignore_case:
            items = [x.casefold() if isinstance(x, str) else x for x in items]
            if isinstance(container, str):
                container = container.casefold()
            elif is_list_like(container):
                container = {
                    x.casefold() if isinstance(x, str) else x for x in container
                }
        if strip_spaces:
            items = [self._strip_spaces(x, strip_spaces) for x in items]
            if isinstance(container, str):
                container = self._strip_spaces(container, strip_spaces)
            elif is_list_like(container):
                container = {self._strip_spaces(x, strip_spaces) for x in container}
        if collapse_spaces:
            items = [self._collapse_spaces(x) for x in items]
            if isinstance(container, str):
                container = self._collapse_spaces(container)
            elif is_list_like(container):
                container = {self._collapse_spaces(x) for x in container}
        if not any(item in container for item in items):
            raise AssertionError(
                self._get_string_msg(
                    orig_container,
                    seq2str(items, lastsep=" or "),
                    msg,
                    values,
                    "does not contain any of",
                    quote_item2=False,
                )
            )

    def should_not_contain_any(
        self,
        container,
        *items,
        msg=None,
        values=True,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if ``container`` contains one or more of the ``*items``.

        Works with strings, lists, and anything that supports Python's ``in``
        operator.

        Supports additional configuration parameters ``msg``, ``values``,
        ``ignore_case`` and ``strip_spaces``, and ``collapse_spaces``
        which have exactly the same semantics as arguments with same
        names have with `Should Contain`. These arguments must always
        be given using ``name=value`` syntax after all ``items``.

        Examples:
        | Should Not Contain Any | ${string} | substring 1 | substring 2 |
        | Should Not Contain Any | ${list}   | item 1 | item 2 | item 3 |
        | Should Not Contain Any | ${list}   | item 1 | item 2 | item 3 | ignore_case=True |
        | Should Not Contain Any | ${list}   | @{items} | msg=Custom message | values=False |
        """
        if not items:
            raise RuntimeError("One or more item required.")
        orig_container = container
        if ignore_case:
            items = [x.casefold() if isinstance(x, str) else x for x in items]
            if isinstance(container, str):
                container = container.casefold()
            elif is_list_like(container):
                container = {
                    x.casefold() if isinstance(x, str) else x for x in container
                }
        if strip_spaces:
            items = [self._strip_spaces(x, strip_spaces) for x in items]
            if isinstance(container, str):
                container = self._strip_spaces(container, strip_spaces)
            elif is_list_like(container):
                container = {self._strip_spaces(x, strip_spaces) for x in container}
        if collapse_spaces:
            items = [self._collapse_spaces(x) for x in items]
            if isinstance(container, str):
                container = self._collapse_spaces(container)
            elif is_list_like(container):
                container = {self._collapse_spaces(x) for x in container}
        if any(item in container for item in items):
            raise AssertionError(
                self._get_string_msg(
                    orig_container,
                    seq2str(items, lastsep=" or "),
                    msg,
                    values,
                    "contains one or more of",
                    quote_item2=False,
                )
            )

    def should_contain_x_times(
        self,
        container,
        item,
        count,
        msg=None,
        ignore_case=False,
        strip_spaces=False,
        collapse_spaces=False,
    ):
        """Fails if ``container`` does not contain ``item`` ``count`` times.

        Works with strings, lists and all objects that `Get Count` works
        with. The default error message can be overridden with ``msg`` and
        the actual count is always logged.

        If ``ignore_case`` is given a true value (see `Boolean arguments`) and
        compared items are strings, it indicates that comparison should be
        case-insensitive. If the ``container`` is a list-like object, string
        items in it are compared case-insensitively.

        If ``strip_spaces`` is given a true value (see `Boolean arguments`)
        and both arguments are strings, the comparison is done without leading
        and trailing spaces. If ``strip_spaces`` is given a string value
        ``LEADING`` or ``TRAILING`` (case-insensitive), the comparison is done
        without leading or trailing spaces, respectively.

        If ``collapse_spaces`` is given a true value (see `Boolean arguments`) and both
        arguments are strings, the comparison is done with all white spaces replaced by
        a single space character.

        Examples:
        | Should Contain X Times | ${output}    | hello | 2 |
        | Should Contain X Times | ${some list} | value | 3 | ignore_case=True |

        ``strip_spaces`` is new in Robot Framework 4.0 and ``collapse_spaces`` is new
        in Robot Framework 4.1.
        """
        count = self._convert_to_integer(count)
        orig_container = container
        if isinstance(item, str):
            if ignore_case:
                item = item.casefold()
                if isinstance(container, str):
                    container = container.casefold()
                elif is_list_like(container):
                    container = [
                        x.casefold() if isinstance(x, str) else x for x in container
                    ]
            if strip_spaces:
                item = self._strip_spaces(item, strip_spaces)
                if isinstance(container, str):
                    container = self._strip_spaces(container, strip_spaces)
                elif is_list_like(container):
                    container = [self._strip_spaces(x, strip_spaces) for x in container]
            if collapse_spaces:
                item = self._collapse_spaces(item)
                if isinstance(container, str):
                    container = self._collapse_spaces(container)
                elif is_list_like(container):
                    container = [self._collapse_spaces(x) for x in container]
        x = self.get_count(container, item)
        if not msg:
            msg = (
                f"{orig_container!r} contains '{item}' {x} time{s(x)}, "
                f"not {count} time{s(count)}."
            )
        self.should_be_equal_as_integers(x, count, msg, values=False)

    def get_count(self, container, item):
        """Returns and logs how many times ``item`` is found from ``container``.

        This keyword works with Python strings and lists and all objects
        that either have ``count`` method or can be converted to Python lists.

        Example:
        | ${count} = | Get Count | ${some item} | interesting value |
        | Should Be True | 5 < ${count} < 10 |
        """
        if not hasattr(container, "count"):
            try:
                container = list(container)
            except Exception:
                raise RuntimeError(
                    f"Converting '{container}' to list failed: {get_error_message()}"
                )
        count = container.count(item)
        self.log(f"Item found from container {count} time{s(count)}.")
        return count

    def should_not_match(
        self,
        string,
        pattern,
        msg=None,
        values=True,
        ignore_case=False,
    ):
        """Fails if the given ``string`` matches the given ``pattern``.

        Pattern matching is similar as matching files in a shell with
        ``*``, ``?`` and ``[chars]`` acting as wildcards. See the
        `Glob patterns` section for more information.

        If ``ignore_case`` is given a true value (see `Boolean arguments`),
        the comparison is case-insensitive.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values`.
        """
        if self._matches(string, pattern, caseless=ignore_case):
            raise AssertionError(
                self._get_string_msg(string, pattern, msg, values, "matches")
            )

    def should_match(self, string, pattern, msg=None, values=True, ignore_case=False):
        """Fails if the given ``string`` does not match the given ``pattern``.

        Pattern matching is similar as matching files in a shell with
        ``*``, ``?`` and ``[chars]`` acting as wildcards. See the
        `Glob patterns` section for more information.

        If ``ignore_case`` is given a true value (see `Boolean arguments`) and
        compared items are strings, it indicates that comparison should be
        case-insensitive.

        See `Should Be Equal` for an explanation on how to override the default
        error message with ``msg`` and ``values``.
        """
        if not self._matches(string, pattern, caseless=ignore_case):
            raise AssertionError(
                self._get_string_msg(string, pattern, msg, values, "does not match")
            )

    def should_match_regexp(self, string, pattern, msg=None, values=True, flags=None):
        """Fails if ``string`` does not match ``pattern`` as a regular expression.

        See the `Regular expressions` section for more information about
        regular expressions and how to use then in Robot Framework test data.

        Notice that the given pattern does not need to match the whole string.
        For example, the pattern ``ello`` matches the string ``Hello world!``.
        If a full match is needed, the ``^`` and ``$`` characters can be used
        to denote the beginning and end of the string, respectively.
        For example, ``^ello$`` only matches the exact string ``ello``.

        Possible flags altering how the expression is parsed (e.g. ``re.IGNORECASE``,
        ``re.MULTILINE``) can be given using the ``flags`` argument (e.g.
        ``flags=IGNORECASE | MULTILINE``) or embedded to the pattern (e.g.
        ``(?im)pattern``).

        If this keyword passes, it returns the portion of the string that
        matched the pattern. Additionally, the possible captured groups are
        returned.

        See the `Should Be Equal` keyword for an explanation on how to override
        the default error message with the ``msg`` and ``values`` arguments.

        Examples:
        | Should Match Regexp | ${output} | \\\\d{6}   | # Output contains six numbers  |
        | Should Match Regexp | ${output} | ^\\\\d{6}$ | # Six numbers and nothing more |
        | ${ret} = | Should Match Regexp | Foo: 42 | foo: \\\\d+ | flags=IGNORECASE |
        | ${ret} = | Should Match Regexp | Foo: 42 | (?i)foo: \\\\d+ |
        | ${match} | ${group1} | ${group2} = |
        | ...      | Should Match Regexp | Bar: 43 | (Foo|Bar): (\\\\d+) |
        =>
        | ${ret} = 'Foo: 42'
        | ${match} = 'Bar: 43'
        | ${group1} = 'Bar'
        | ${group2} = '43'

        The ``flags`` argument is new in Robot Framework 6.0.
        """
        res = re.search(pattern, string, flags=parse_re_flags(flags))
        if res is None:
            raise AssertionError(
                self._get_string_msg(string, pattern, msg, values, "does not match")
            )
        match = res.group(0)
        groups = res.groups()
        if groups:
            return [match, *groups]
        return match

    def should_not_match_regexp(
        self,
        string,
        pattern,
        msg=None,
        values=True,
        flags=None,
    ):
        """Fails if ``string`` matches ``pattern`` as a regular expression.

        See `Should Match Regexp` for more information about arguments.
        """
        if re.search(pattern, string, flags=parse_re_flags(flags)) is not None:
            raise AssertionError(
                self._get_string_msg(string, pattern, msg, values, "matches")
            )

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
        self.log(f"Length is {length}.")
        return length

    def _get_length(self, item):
        try:
            return len(item)
        except Exception:
            try:
                return item.length()
            except Exception:
                try:
                    return item.size()
                except Exception:
                    try:
                        return item.length
                    except Exception:
                        raise RuntimeError(f"Could not get length of '{item}'.")

    def length_should_be(self, item, length, msg=None):
        """Verifies that the length of the given item is correct.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the ``msg`` argument.
        """
        length = self._convert_to_integer(length)
        actual = self.get_length(item)
        if actual != length:
            raise AssertionError(
                msg or f"Length of '{item}' should be {length} but is {actual}."
            )

    def should_be_empty(self, item, msg=None):
        """Verifies that the given item is empty.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the ``msg`` argument.
        """
        if self.get_length(item) > 0:
            raise AssertionError(msg or f"'{item}' should be empty.")

    def should_not_be_empty(self, item, msg=None):
        """Verifies that the given item is not empty.

        The length of the item is got using the `Get Length` keyword. The
        default error message can be overridden with the ``msg`` argument.
        """
        if self.get_length(item) == 0:
            raise AssertionError(msg or f"'{item}' should not be empty.")

    def _get_string_msg(
        self,
        item1,
        item2,
        custom_message,
        include_values,
        delimiter,
        quote_item1=True,
        quote_item2=True,
    ):
        if custom_message and not self._include_values(include_values):
            return custom_message
        item1 = f"'{safe_str(item1)}'" if quote_item1 else safe_str(item1)
        item2 = f"'{safe_str(item2)}'" if quote_item2 else safe_str(item2)
        default_message = f"{item1} {delimiter} {item2}"
        if not custom_message:
            return default_message
        return f"{custom_message}: {default_message}"


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
        the variables without the decoration.

        Example:
        | ${example_variable} =         | Set Variable | example value         |
        | ${variables} =                | Get Variables |                      |
        | Dictionary Should Contain Key | ${variables} | \\${example_variable} |
        | Dictionary Should Contain Key | ${variables} | \\${ExampleVariable}  |
        | Set To Dictionary             | ${variables} | \\${name} | value     |
        | Variable Should Not Exist     | \\${name}    |           |           |
        | ${no decoration} =            | Get Variables | no_decoration=Yes |
        | Dictionary Should Contain Key | ${no decoration} | example_variable |
        """
        return self._variables.as_dict(decoration=is_falsy(no_decoration))

    @keyword(types=None)
    @run_keyword_variant(resolve=0)
    def get_variable_value(self, name, default=None):
        r"""Returns variable value or ``default`` if the variable does not exist.

        The name of the variable can be given either as a normal variable name
        like ``${name}`` or in escaped format like ``$name`` or ``\${name}``.
        For the reasons explained in the `Using variables with keywords creating
        or accessing variables` section, using the escaped format is recommended.

        Notice that ``default`` must be given positionally like ``example`` and
        not using the named-argument syntax like ``default=example``. We hope to
        be able to remove this limitation in the future.

        Examples:
        | ${x} =    `Get Variable Value`    $a    example
        | ${y} =    `Get Variable Value`    $a    ${b}
        | ${z} =    `Get Variable Value`    $z
        =>
        - ``${x}`` gets value of ``${a}`` if ``${a}`` exists and string ``default`` otherwise
        - ``${y}`` gets value of ``${a}`` if ``${a}`` exists and value of ``${b}`` otherwise
        - ``${z}`` is set to Python ``None`` if it does not exist previously
        """
        try:
            name = self._get_var_name(name, require_assign=False)
            return self._variables.replace_scalar(name)
        except VariableError:
            return self._variables.replace_scalar(default)

    def log_variables(self, level="INFO"):
        """Logs all variables in the current scope with given log level."""
        variables = self.get_variables()
        for name in sorted(variables, key=lambda s: s[2:-1].casefold()):
            name, value = self._get_logged_variable(name, variables)
            msg = format_assign_message(name, value, cut_long=False)
            self.log(msg, level)

    def _get_logged_variable(self, name, variables):
        value = variables[name]
        try:
            if name[0] == "@":
                if isinstance(value, Sequence):
                    value = list(value)
                else:  # Don't consume iterables.
                    name = "$" + name[1:]
            if name[0] == "&":
                value = OrderedDict(value)
        except Exception:
            name = "$" + name[1:]
        return name, value

    @run_keyword_variant(resolve=0)
    def variable_should_exist(self, name, message=None):
        r"""Fails unless the given variable exists within the current scope.

        The name of the variable can be given either as a normal variable name
        like ``${name}`` or in escaped format like ``$name`` or ``\${name}``.
        For the reasons explained in the `Using variables with keywords creating
        or accessing variables` section, using the escaped format is recommended.

        The default error message can be overridden with the ``message`` argument.
        Notice that it must be given positionally like ``A message`` and not
        using the named-argument syntax like ``message=A message``. We hope to
        be able to remove this limitation in the future.

        See also `Variable Should Not Exist` and `Keyword Should Exist`.
        """
        name = self._get_var_name(name)
        try:
            self._variables.replace_scalar(name)
        except VariableError:
            raise AssertionError(
                self._variables.replace_string(message)
                if message
                else f"Variable '{name}' does not exist."
            )

    @run_keyword_variant(resolve=0)
    def variable_should_not_exist(self, name, message=None):
        r"""Fails if the given variable exists within the current scope.

        The name of the variable can be given either as a normal variable name
        like ``${name}`` or in escaped format like ``$name`` or ``\${name}``.
        For the reasons explained in the `Using variables with keywords creating
        or accessing variables` section, using the escaped format is recommended.

        The default error message can be overridden with the ``message`` argument.
        Notice that it must be given positionally like ``A message`` and not
        using the named-argument syntax like ``message=A message``. We hope to
        be able to remove this limitation in the future.

        See also `Variable Should Exist` and `Keyword Should Exist`.
        """
        name = self._get_var_name(name)
        try:
            self._variables.replace_scalar(name)
        except VariableError:
            pass
        else:
            raise AssertionError(
                self._variables.replace_string(message)
                if message
                else f"Variable '{name}' exists."
            )

    def replace_variables(self, text):
        """Replaces variables in the given text with their current values.

        If the text contains undefined variables, this keyword fails.
        If the given ``text`` contains only a single variable, its value is
        returned as-is and it can be any object. Otherwise, this keyword
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
        | ${hi} =    Set Variable    Hello, world!
        | ${hi2} =    Set Variable    I said: ${hi}
        | ${var1}    ${var2} =    Set Variable    Hello    world
        | @{list} =    Set Variable    ${list with some items}
        | ${item1}    ${item2} =    Set Variable    ${list with 2 items}

        Variables created with this keyword are available only in the
        scope where they are created. See `Set Global Variable`,
        `Set Test Variable` and `Set Suite Variable` for information on how to
        set variables so that they are available also in a larger scope.

        *NOTE:* The ``VAR`` syntax introduced in Robot Framework 7.0 is generally
        recommended over this keyword. The basic usage is shown below and the Robot
        Framework User Guide explains the syntax in detail.

        | VAR    ${hi}     Hello, world!
        | VAR    ${hi2}    I said: ${hi}
        """
        if len(values) == 0:
            return ""
        if len(values) == 1:
            return values[0]
        return list(values)

    @run_keyword_variant(resolve=0)
    def set_local_variable(self, name, *values):
        r"""Makes a variable available everywhere within the local scope.

        Variables set with this keyword are available within the
        local scope of the currently executed test case or in the local scope
        of the keyword in which they are defined. For example, if you set a
        variable in a user keyword, it is available only in that keyword. Other
        test cases or keywords will not see variables set with this keyword.

        This keyword is equivalent to a normal variable assignment based on a
        keyword return value. For example,

        | ${var} =    `Set Variable`    value
        | @{list} =    `Create List`    item1    item2    item3

        are equivalent with

        | `Set Local Variable`    @var    value
        | `Set Local Variable`    @list    item1    item2    item3

        The main use case for this keyword is creating local variables in
        libraries.

        See `Set Suite Variable` for more information and usage examples. See
        also the `Using variables with keywords creating or accessing variables`
        section for information why it is recommended to give the variable name
        in escaped format like ``$name`` or ``\${name}`` instead of the normal
        ``${name}``.

        See also `Set Global Variable` and `Set Test Variable`.

        *NOTE:* The ``VAR`` syntax introduced in Robot Framework 7.0 is recommended
        over this keyword.
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self._variables.set_local(name, value)
        self._log_set_variable(name, value)

    @run_keyword_variant(resolve=0)
    def set_test_variable(self, name, *values):
        r"""Makes a variable available everywhere within the scope of the current test.

        Variables set with this keyword are available everywhere within the
        scope of the currently executed test case. For example, if you set a
        variable in a user keyword, it is available both in the test case level
        and also in all other user keywords used in the current test. Other
        test cases will not see variables set with this keyword.

        If `Set Test Variable` is used in suite setup, the variable is available
        everywhere within that suite setup as well as in the corresponding suite
        teardown, but it is not seen by tests or possible child suites. If the
        keyword is used in a suite teardown, the variable is available only in that
        teardown.

        See `Set Suite Variable` for more information and usage examples. See
        also the `Using variables with keywords creating or accessing variables`
        section for information why it is recommended to give the variable name
        in escaped format like ``$name`` or ``\${name}`` instead of the normal
        ``${name}``.

        When creating automated tasks, not tests, it is possible to use `Set
        Task Variable`. See also `Set Global Variable` and `Set Local Variable`.

        *NOTE:* The ``VAR`` syntax introduced in Robot Framework 7.0 is recommended
        over this keyword.

        *NOTE:* Prior to Robot Framework 7.2, using `Set Test Variable` in a suite
        setup or teardown was an error.
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self._variables.set_test(name, value)
        self._log_set_variable(name, value)

    @run_keyword_variant(resolve=0)
    def set_task_variable(self, name, *values):
        """Makes a variable available everywhere within the scope of the current task.

        This is an alias for `Set Test Variable` that is more applicable when
        creating tasks, not tests.

        *NOTE:* The ``VAR`` syntax introduced in Robot Framework 7.0 is recommended
        over this keyword.
        """
        self.set_test_variable(name, *values)

    @run_keyword_variant(resolve=0)
    def set_suite_variable(self, name, *values):
        r"""Makes a variable available everywhere within the scope of the current suite.

        Variables set with this keyword are available everywhere within the
        scope of the currently executed test suite. Setting variables with this
        keyword thus has the same effect as creating them using the Variables
        section in the data file or importing them from variable files.

        Possible child test suites do not see variables set with this keyword
        by default, but that can be controlled by using ``children=<option>``
        as the last argument. If the specified ``<option>`` is given a true value
        (see `Boolean arguments`), the variable is set also to the child
        suites. Parent and sibling suites will never see variables set with
        this keyword.

        The name of the variable can be given either as a normal variable name
        like ``${NAME}`` or in escaped format as ``\${NAME}`` or ``$NAME``.
        For the reasons explained in the `Using variables with keywords creating
        or accessing variables` section, *using the escaped format is highly
        recommended*.

        Variable value can be specified using the same syntax as when variables
        are created in the Variables section. Same way as in that section,
        it is possible to create scalar values, lists and dictionaries.
        The type is got from the variable name prefix ``$``, ``@`` and ``&``,
        respectively.

        If a variable already exists within the new scope, its value will be
        overwritten. If a variable already exists within the current scope,
        the value can be left empty and the variable within the new scope gets
        the value within the current scope.

        Examples:
        | Set Suite Variable    $SCALAR    Hello, world!
        | Set Suite Variable    $SCALAR    Hello, world!    children=True
        | Set Suite Variable    @LIST      First item       Second item
        | Set Suite Variable    &DICT      key=value        foo=bar
        | ${ID} =    Get ID
        | Set Suite Variable    $ID

        To override an existing value with an empty value, use built-in
        variables ``${EMPTY}``, ``@{EMPTY}`` or ``&{EMPTY}``:

        | Set Suite Variable    $SCALAR    ${EMPTY}
        | Set Suite Variable    @LIST      @{EMPTY}
        | Set Suite Variable    &DICT      &{EMPTY}

        See also `Set Global Variable`, `Set Test Variable` and `Set Local Variable`.

        *NOTE:* The ``VAR`` syntax introduced in Robot Framework 7.0 is recommended
        over this keyword. The basic usage is shown below and the Robot Framework
        User Guide explains the syntax in detail.

        | VAR    ${SCALAR}    Hello, world!                scope=SUITE
        | VAR    @{LIST}      First item    Second item    scope=SUITE
        | VAR    &{DICT}      key=value     foo=bar        scope=SUITE
        """
        name = self._get_var_name(name)
        if (
            values
            and isinstance(values[-1], str)
            and values[-1].startswith("children=")
        ):
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
        r"""Makes a variable available globally in all tests and suites.

        Variables set with this keyword are globally available in all
        subsequent test suites, test cases and user keywords. Also variables
        created Variables sections are overridden. Variables assigned locally
        based on keyword return values or by using `Set Suite Variable`,
        `Set Test Variable` or `Set Local Variable` override these variables
        in that scope, but the global value is not changed in those cases.

        In practice setting variables with this keyword has the same effect
        as using command line options ``--variable`` and ``--variablefile``.
        Because this keyword can change variables everywhere, it should be
        used with care.

        See `Set Suite Variable` for more information and usage examples. See
        also the `Using variables with keywords creating or accessing variables`
        section for information why it is recommended to give the variable name
        in escaped format like ``$name`` or ``\${name}`` instead of the normal
        ``${name}``.

        *NOTE:* The ``VAR`` syntax introduced in Robot Framework 7.0 is recommended
        over this keyword.
        """
        name = self._get_var_name(name)
        value = self._get_var_value(name, values)
        self._variables.set_global(name, value)
        self._log_set_variable(name, value)

    # Helpers

    def _get_var_name(self, original, require_assign=True):
        try:
            replaced = self._variables.replace_string(original)
        except VariableError:
            replaced = original
        try:
            name = self._resolve_var_name(replaced)
        except ValueError:
            name = original
        match = search_variable(name, identifiers="$@&")
        match.resolve_base(self._variables)
        valid = match.is_assign() if require_assign else match.is_variable()
        if not valid:
            raise DataError(f"Invalid variable name '{name}'.")
        return str(match)

    def _resolve_var_name(self, name):
        if name.startswith("\\"):
            name = name[1:]
        if len(name) < 2 or name[0] not in "$@&":
            raise ValueError
        if name[1] != "{":
            name = f"{name[0]}{{{name[1:]}}}"
        match = search_variable(name, identifiers="$@&", ignore_errors=True)
        match.resolve_base(self._variables)
        if not match.is_assign():
            raise ValueError
        return str(match)

    def _get_var_value(self, name, values):
        if not values:
            return self._variables[name]
        if name[0] == "$":
            # We could consider catenating values similarly as when creating
            # scalar variables in the variable table, but that would require
            # handling non-string values somehow. For details see
            # https://github.com/robotframework/robotframework/issues/1919
            if len(values) != 1 or is_list_variable(values[0]):
                raise DataError(
                    f"Setting list value to scalar variable '{name}' is not supported "
                    f"anymore. Create list variable '@{name[1:]}' instead."
                )
            return self._variables.replace_scalar(values[0])
        resolver = VariableResolver.from_name_and_value(name, values)
        return resolver.resolve(self._variables)

    def _log_set_variable(self, name, value):
        if self._context.steps:
            logger.info(format_assign_message(name, value))


class _RunKeyword(_BuiltInBase):

    # If you use any of these run keyword variants from another library, you
    # should register those keywords with 'register_run_keyword' method. See
    # the documentation of that method at the end of this file. There are also
    # other run keyword variant keywords in BuiltIn which can also be seen
    # at the end of this file.

    @run_keyword_variant(resolve=0, dry_run=True)
    def run_keyword(self, name, *args):
        """Executes the given keyword with the given arguments.

        Because the name of the keyword to execute is given as an argument, it
        can be a variable and thus set dynamically, e.g. from a return value of
        another keyword or from the command line.
        """
        ctx = self._context
        name, args = self._replace_variables_in_name(name, args, ctx)
        if not isinstance(name, str):
            raise RuntimeError("Keyword name must be a string.")
        if ctx.steps:
            data, result, _ = ctx.steps[-1]
            lineno = data.lineno
        else:  # Called, typically by a listener, when no keyword started.
            data = lineno = None
            if ctx.test:
                result = ctx.test
            elif not ctx.suite.has_tests:
                result = ctx.suite.setup
            else:
                result = ctx.suite.teardown
        kw = Keyword(name, args=args, parent=data, lineno=lineno)
        with ctx.paused_timeouts:
            return kw.run(result, ctx)

    def _replace_variables_in_name(self, name, args, ctx):
        match = search_variable(name)
        if not match or ctx.dry_run:
            return unescape(name), args
        if match.is_list_variable():
            return self._replace_variables_in_name_with_list_variable(name, args, ctx)
        # If the matched runner accepts embedded arguments, use the original name
        # instead of the one where variables are already replaced and converted to
        # strings. This allows using non-string values as embedded arguments also
        # in this context. An exact match after variables have been replaced has
        # a precedence over a possible embedded match with the original name, though.
        # TODO: This functionality exists also in 'KeywordRunner.run'. Reuse that to
        # avoid duplication. We probably could pass an argument like 'dynamic_name=True'
        # to 'Keyword.run', but then it would be better if 'Run Keyword' would support
        # 'NONE' as a special value to not run anything similarly as setup/teardown.
        replaced = ctx.variables.replace_scalar(name, ignore_errors=ctx.in_teardown)
        runner = ctx.get_runner(replaced, recommend_on_failure=False)
        if hasattr(runner, "embedded_args"):
            return name, args
        return replaced, args

    def _replace_variables_in_name_with_list_variable(self, name, args, ctx):
        # TODO: This seems to be the only place where `replace_until` is used.
        # That functionality should be removed from `replace_list` and implemented
        # here. Alternatively we could disallow passing name as a list variable.
        resolved = ctx.variables.replace_list(
            [name, *args],
            replace_until=1,
            ignore_errors=ctx.in_teardown,
        )
        if not resolved:
            raise DataError(
                f"Keyword name missing: Given arguments {[name, *args]} resolved "
                f"to an empty list."
            )
        return resolved[0], resolved[1:]

    @run_keyword_variant(resolve=0, dry_run=True)
    def run_keywords(self, *keywords):
        """Executes all the given keywords in a sequence.

        This keyword is mainly useful in setups and teardowns when they need
        to take care of multiple actions and creating a new higher level user
        keyword would be an overkill.

        By default all arguments are expected to be keywords to be executed.

        Examples:
        | `Run Keywords` | `Initialize database` | `Start servers` | `Clear logs` |
        | `Run Keywords` | ${KW 1} | ${KW 2} |
        | `Run Keywords` | @{KEYWORDS} |

        Keywords can also be run with arguments using upper case ``AND`` as
        a separator between keywords. The keywords are executed so that the
        first argument is the first keyword and proceeding arguments until
        the first ``AND`` are arguments to it. First argument after the first
        ``AND`` is the second keyword and proceeding arguments until the next
        ``AND`` are its arguments. And so on.

        Examples:
        | `Run Keywords` | `Initialize database` | db1 | AND | `Start servers` | server1 | server2 |
        | `Run Keywords` | `Initialize database` | ${DB NAME} | AND | `Start servers` | @{SERVERS} | AND | `Clear logs` |
        | `Run Keywords` | ${KW} | AND | @{KW WITH ARGS} |

        Notice that the ``AND`` control argument must be used explicitly and
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
                if not err.can_continue(self._context):
                    break
        if errors:
            raise ExecutionFailures(errors)

    def _split_run_keywords(self, keywords):
        if "AND" not in keywords:
            for name in self._split_run_keywords_without_and(keywords):
                yield name, ()
        else:
            for kw_call in self._split_run_keywords_with_and(keywords):
                if not kw_call:
                    raise DataError("AND must have keyword before and after.")
                yield kw_call[0], kw_call[1:]

    def _split_run_keywords_without_and(self, keywords):
        replace_list = self._variables.replace_list
        ignore_errors = self._context.in_teardown
        # `run_keyword` resolves variables, but list variables must be expanded
        # here to pass it each keyword name separately.
        for name in keywords:
            if is_list_variable(name):
                for n in replace_list([name], ignore_errors=ignore_errors):
                    yield escape(n)
            else:
                yield name

    def _split_run_keywords_with_and(self, keywords):
        while "AND" in keywords:
            index = keywords.index("AND")
            yield keywords[:index]
            keywords = keywords[index + 1 :]
        yield keywords

    @run_keyword_variant(resolve=1, dry_run=True)
    def run_keyword_if(self, condition, name, *args):
        """Runs the given keyword with the given arguments, if ``condition`` is true.

        *NOTE:* Robot Framework 4.0 introduced built-in IF/ELSE support and using
        that is generally recommended over using this keyword.

        The given ``condition`` is evaluated in Python as explained in the
        `Evaluating expressions` section, and ``name`` and ``*args`` have same
        semantics as with `Run Keyword`.

        Example, a simple if/else construct:
        | `Run Keyword If` | '${status}' == 'OK' | Some Action    | arg |
        | `Run Keyword If` | '${status}' != 'OK' | Another Action |

        In this example, only either ``Some Action`` or ``Another Action`` is
        executed, based on the value of the ``${status}`` variable.

        Variables used like ``${variable}``, as in the examples above, are
        replaced in the expression before evaluation. Variables are also
        available in the evaluation namespace and can be accessed using special
        ``$variable`` syntax as explained in the `Evaluating expressions` section.

        Example:
        | `Run Keyword If` | $result is None or $result == 'FAIL' | Keyword |

        This keyword supports also optional ELSE and ELSE IF branches. Both
        of them are defined in ``*args`` and must use exactly format ``ELSE``
        or ``ELSE IF``, respectively. ELSE branches must contain first the
        name of the keyword to execute and then its possible arguments. ELSE
        IF branches must first contain a condition, like the first argument
        to this keyword, and then the keyword to execute and its possible
        arguments. It is possible to have ELSE branch after ELSE IF and to
        have multiple ELSE IF branches. Nested `Run Keyword If` usage is not
        supported when using ELSE and/or ELSE IF branches.

        Given previous example, if/else construct can also be created like this:
        | `Run Keyword If` | '${status}' == 'PASS' | Some Action | arg | ELSE | Another Action |

        The return value of this keyword is the return value of the actually
        executed keyword or Python ``None`` if no keyword was executed (i.e.
        if ``condition`` was false). Hence, it is recommended to use ELSE
        and/or ELSE IF branches to conditionally assign return values from
        keyword to variables (see `Set Variable If` you need to set fixed
        values conditionally). This is illustrated by the example below:

        | ${var1} =   | `Run Keyword If` | ${rc} == 0     | Some keyword returning a value |
        | ...         | ELSE IF          | 0 < ${rc} < 42 | Another keyword |
        | ...         | ELSE IF          | ${rc} < 0      | Another keyword with args | ${rc} | arg2 |
        | ...         | ELSE             | Final keyword to handle abnormal cases | ${rc} |
        | ${var2} =   | `Run Keyword If` | ${condition}  | Some keyword |

        In this example, ${var2} will be set to ``None`` if ${condition} is
        false.

        Notice that ``ELSE`` and ``ELSE IF`` control words must be used
        explicitly and thus cannot come from variables. If you need to use
        literal ``ELSE`` and ``ELSE IF`` strings as arguments, you can escape
        them with a backslash like ``\\ELSE`` and ``\\ELSE IF``.
        """
        args, branch = self._split_elif_or_else_branch(args)
        if self._is_true(condition):
            return self.run_keyword(name, *args)
        return branch()

    def _split_elif_or_else_branch(self, args):
        if "ELSE IF" in args:
            args, branch = self._split_branch(
                args, "ELSE IF", 2, "condition and keyword"
            )
            return args, lambda: self.run_keyword_if(*branch)
        if "ELSE" in args:
            args, branch = self._split_branch(args, "ELSE", 1, "keyword")
            return args, lambda: self.run_keyword(*branch)
        return args, lambda: None

    def _split_branch(self, args, control_word, required, required_error):
        index = list(args).index(control_word)
        branch = self._variables.replace_list(args[index + 1 :], required)
        if len(branch) < required:
            raise DataError(f"{control_word} requires {required_error}.")
        return args[:index], branch

    @run_keyword_variant(resolve=1, dry_run=True)
    def run_keyword_unless(self, condition, name, *args):
        """*DEPRECATED since RF 5.0. Use Native IF/ELSE or `Run Keyword If` instead.*

        Runs the given keyword with the given arguments if ``condition`` is false.

        See `Run Keyword If` for more information and an example. Notice that this
        keyword does not support ELSE or ELSE IF branches like `Run Keyword If` does.
        """
        if not self._is_true(condition):
            return self.run_keyword(name, *args)

    @run_keyword_variant(resolve=0, dry_run=True)
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

        *NOTE:* Robot Framework 5.0 introduced native TRY/EXCEPT functionality
        that is generally recommended for error handling.
        """
        try:
            return "PASS", self.run_keyword(name, *args)
        except ExecutionFailed as err:
            if err.dont_continue or err.skip:
                raise
            return "FAIL", str(err)

    @run_keyword_variant(resolve=0, dry_run=True)
    def run_keyword_and_warn_on_failure(self, name, *args):
        """Runs the specified keyword logs a warning if the keyword fails.

        This keyword is similar to `Run Keyword And Ignore Error` but if the executed
        keyword fails, the error message is logged as a warning to make it more
        visible. Returns status and possible return value or error message exactly
        like `Run Keyword And Ignore Error` does.

        Errors caused by invalid syntax, timeouts, or fatal exceptions are not
        caught by this keyword. Otherwise this keyword itself never fails.

        New in Robot Framework 4.0.
        """
        status, message = self.run_keyword_and_ignore_error(name, *args)
        if status == "FAIL":
            logger.warn(f"Executing keyword '{name}' failed:\n{message}")
        return status, message

    @run_keyword_variant(resolve=0, dry_run=True)
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
        """
        status, _ = self.run_keyword_and_ignore_error(name, *args)
        return status == "PASS"

    @run_keyword_variant(resolve=0, dry_run=True)
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

    @run_keyword_variant(resolve=1, dry_run=True)
    def run_keyword_and_expect_error(self, expected_error, name, *args):
        """Runs the keyword and checks that the expected error occurred.

        The keyword to execute and its arguments are specified using ``name``
        and ``*args`` exactly like with `Run Keyword`.

        The expected error must be given in the same format as in Robot Framework
        reports. By default it is interpreted as a glob pattern with ``*``, ``?``
        and ``[chars]`` as wildcards, but that can be changed by using various
        prefixes explained in the table below. Prefixes are case-sensitive and
        they must be separated from the actual message with a colon and an
        optional space like ``PREFIX: Message`` or ``PREFIX:Message``.

        | = Prefix = | = Explanation = |
        | ``EQUALS`` | Exact match. Especially useful if the error contains glob wildcards. |
        | ``STARTS`` | Error must start with the specified error. |
        | ``REGEXP`` | Regular expression match. |
        | ``GLOB``   | Same as the default behavior. |

        See the `Pattern matching` section for more information about glob
        patterns and regular expressions.

        If the expected error occurs, the error message is returned and it can
        be further processed or tested if needed. If there is no error, or the
        error does not match the expected error, this keyword fails.

        Examples:
        | Run Keyword And Expect Error | My error            | Keyword | arg |
        | Run Keyword And Expect Error | ValueError: *       | Some Keyword  |
        | Run Keyword And Expect Error | STARTS: ValueError: | Some Keyword  |
        | Run Keyword And Expect Error | EQUALS:No match for '//input[@type="text"]' |
        | ...                          | Find Element | //input[@type="text"] |
        | ${msg} =                     | Run Keyword And Expect Error | * |
        | ...                          | Keyword | arg1 | arg2 |
        | Log To Console | ${msg} |

        Errors caused by invalid syntax, timeouts, or fatal exceptions are not
        caught by this keyword.

        *NOTE:* Regular expression matching used to require only the beginning
        of the error to match the given pattern. That was changed in Robot
        Framework 5.0 and nowadays the pattern must match the error fully.
        To match only the beginning, add ``.*`` at the end of the pattern like
        ``REGEXP: Start.*``.

        *NOTE:* Robot Framework 5.0 introduced native TRY/EXCEPT functionality
        that is generally recommended for error handling. It supports same
        pattern matching syntax as this keyword.
        """
        try:
            self.run_keyword(name, *args)
        except ExecutionFailed as err:
            if err.dont_continue or err.skip:
                raise
            error = err.message
        else:
            raise AssertionError(f"Expected error '{expected_error}' did not occur.")
        if not self._error_is_expected(error, expected_error):
            raise AssertionError(
                f"Expected error '{expected_error}' but got '{error}'."
            )
        return error

    def _error_is_expected(self, error, expected_error):
        glob = self._matches
        matchers = {
            "GLOB": glob,
            "EQUALS": lambda s, p: s == p,
            "STARTS": lambda s, p: s.startswith(p),
            "REGEXP": lambda s, p: re.fullmatch(p, s) is not None,
        }
        prefixes = tuple(prefix + ":" for prefix in matchers)
        if not expected_error.startswith(prefixes):
            return glob(error, expected_error)
        prefix, expected_error = expected_error.split(":", 1)
        return matchers[prefix](error, expected_error.lstrip())

    @run_keyword_variant(resolve=1, dry_run=True)
    def repeat_keyword(self, repeat, name, *args):
        """Executes the specified keyword multiple times.

        ``name`` and ``args`` define the keyword that is executed similarly as
        with `Run Keyword`. ``repeat`` specifies how many times (as a count) or
        how long time (as a timeout) the keyword should be executed.

        If ``repeat`` is given as count, it specifies how many times the
        keyword should be executed. ``repeat`` can be given as an integer or
        as a string that can be converted to an integer. If it is a string,
        it can have postfix ``times`` or ``x`` (case and space insensitive)
        to make the expression more explicit.

        If ``repeat`` is given as timeout, it must be in Robot Framework's
        time format (e.g. ``1 minute``, ``2 min 3 s``). Using a number alone
        (e.g. ``1`` or ``1.5``) does not work in this context.

        If ``repeat`` is zero or negative, the keyword is not executed at
        all. This keyword fails immediately if any of the execution
        rounds fails.

        Examples:
        | Repeat Keyword | 5 times   | Go to Previous Page |
        | Repeat Keyword | ${var}    | Some Keyword | arg1 | arg2 |
        | Repeat Keyword | 2 minutes | Some Keyword | arg1 | arg2 |
        """
        try:
            count = self._get_repeat_count(repeat)
        except RuntimeError as err:
            timeout = self._get_repeat_timeout(repeat)
            if timeout is None:
                raise err
            keywords = self._keywords_repeated_by_timeout(timeout, name, args)
        else:
            keywords = self._keywords_repeated_by_count(count, name, args)
        self._run_keywords(keywords)

    def _get_repeat_count(self, times, require_postfix=False):
        times = normalize(str(times))
        if times.endswith("times"):
            times = times[:-5]
        elif times.endswith("x"):
            times = times[:-1]
        elif require_postfix:
            raise ValueError
        return self._convert_to_integer(times)

    def _get_repeat_timeout(self, timestr):
        try:
            float(timestr)
        except ValueError:
            pass
        else:
            return None
        try:
            return timestr_to_secs(timestr)
        except ValueError:
            return None

    def _keywords_repeated_by_count(self, count, name, args):
        if count <= 0:
            self.log(f"Keyword '{name}' repeated zero times.")
        for i in range(count):
            self.log(f"Repeating keyword, round {i + 1}/{count}.")
            yield name, args

    def _keywords_repeated_by_timeout(self, timeout, name, args):
        if timeout <= 0:
            self.log(f"Keyword '{name}' repeated zero times.")
        round = 0
        maxtime = time.time() + timeout
        while time.time() < maxtime:
            round += 1
            remaining = secs_to_timestr(maxtime - time.time(), compact=True)
            self.log(f"Repeating keyword, round {round}, {remaining} remaining.")
            yield name, args

    @run_keyword_variant(resolve=2, dry_run=True)
    def wait_until_keyword_succeeds(self, retry, retry_interval, name, *args):
        """Runs the specified keyword and retries if it fails.

        ``name`` and ``args`` define the keyword that is executed similarly
        as with `Run Keyword`. How long to retry running the keyword is
        defined using ``retry`` argument either as timeout or count.
        ``retry_interval`` is the time to wait between execution attempts.

        If ``retry`` is given as timeout, it must be in Robot Framework's
        time format (e.g. ``1 minute``, ``2 min 3 s``, ``4.5``) that is
        explained in an appendix of Robot Framework User Guide. If it is
        given as count, it must have ``times`` or ``x`` postfix (e.g.
        ``5 times``, ``10 x``). ``retry_interval`` must always be given in
        Robot Framework's time format.

        By default, ``retry_interval`` is the time to wait _after_ a keyword has
        failed. For example, if the first run takes 2 seconds and the retry
        interval is 3 seconds, the second run starts 5 seconds after the first
        run started. If ``retry_interval`` start with prefix ``strict:``, the
        execution time of the previous keyword is subtracted from the retry time.
        With the earlier example the second run would thus start 3 seconds after
        the first run started. A warning is logged if keyword execution time is
        longer than a strict interval.

        If the keyword does not succeed regardless of retries, this keyword
        fails. If the executed keyword passes, its return value is returned.

        Examples:
        | Wait Until Keyword Succeeds | 2 min | 5 sec | My keyword | argument |
        | ${result} = | Wait Until Keyword Succeeds | 3x | 200ms | My keyword |
        | ${result} = | Wait Until Keyword Succeeds | 3x | strict: 200ms | My keyword |

        All normal failures are caught by this keyword. Errors caused by
        invalid syntax, test or keyword timeouts, or fatal exceptions (caused
        e.g. by `Fatal Error`) are not caught.

        Running the same keyword multiple times inside this keyword can create
        lots of output and considerably increase the size of the generated
        output files. It is possible to remove unnecessary keywords from
        the outputs using the ``--remove-keywords WUKS`` command line option.

        Support for "strict" retry interval is new in Robot Framework 4.1.
        """
        maxtime = count = -1
        try:
            count = self._get_repeat_count(retry, require_postfix=True)
        except ValueError:
            timeout = timestr_to_secs(retry)
            maxtime = time.time() + timeout
            message = f"for {secs_to_timestr(timeout)}"
        else:
            if count <= 0:
                raise ValueError(f"Retry count {count} is not positive.")
            message = f"{count} time{s(count)}"
        if not (
            isinstance(retry_interval, str)
            and normalize(retry_interval).startswith("strict:")
        ):
            strict_interval = False
        else:
            retry_interval = retry_interval.split(":", 1)[1].strip()
            strict_interval = True
        retry_interval = sleep_time = timestr_to_secs(retry_interval)
        while True:
            start_time = time.time()
            try:
                return self.run_keyword(name, *args)
            except ExecutionFailed as err:
                self._reset_keyword_timeout_in_teardown(err, self._context)
                if err.dont_continue or err.skip:
                    raise
                count -= 1
                if time.time() > maxtime > 0 or count == 0:
                    name = self._variables.replace_scalar(name)
                    raise AssertionError(
                        f"Keyword '{name}' failed after retrying {message}. "
                        f"The last error was: {err}"
                    )
            finally:
                if strict_interval:
                    execution_time = time.time() - start_time
                    sleep_time = retry_interval - execution_time
                    if sleep_time < 0:
                        logger.warn(
                            f"Keyword execution time {secs_to_timestr(execution_time)} "
                            f"is longer than retry interval "
                            f"{secs_to_timestr(retry_interval)}."
                        )
            self._sleep_in_parts(sleep_time)

    def _reset_keyword_timeout_in_teardown(self, err, context):
        # Keyword timeouts in teardowns have been converted to normal failures
        # to allow execution to continue on higher level:
        # https://github.com/robotframework/robotframework/issues/3398
        # We need to reset it here to not continue unnecessarily:
        # https://github.com/robotframework/robotframework/issues/5237
        if context.in_teardown:
            timeouts = [t for t in context.timeouts if t.kind == "KEYWORD"]
            if timeouts and min(timeouts).timed_out():
                err.keyword_timeout = True

    @run_keyword_variant(resolve=1)
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
        values = list(values)
        while True:
            values = self._verify_values_for_set_variable_if(values)
            if self._is_true(condition):
                return self._variables.replace_scalar(values[0])
            if len(values) == 1:
                return None
            if len(values) == 2:
                return self._variables.replace_scalar(values[1])
            condition, *values = values[1:]
            condition = self._variables.replace_scalar(condition)

    def _verify_values_for_set_variable_if(self, values):
        if not values:
            raise RuntimeError("At least one value is required.")
        if is_list_variable(values[0]):
            values[:1] = [escape(item) for item in self._variables[values[0]]]
            return self._verify_values_for_set_variable_if(values)
        return values

    @run_keyword_variant(resolve=0, dry_run=True)
    def run_keyword_if_test_failed(self, name, *args):
        """Runs the given keyword with the given arguments, if the test failed.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        test = self._get_test_in_teardown("Run Keyword If Test Failed")
        if test.failed:
            return self.run_keyword(name, *args)

    @run_keyword_variant(resolve=0, dry_run=True)
    def run_keyword_if_test_passed(self, name, *args):
        """Runs the given keyword with the given arguments, if the test passed.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        test = self._get_test_in_teardown("Run Keyword If Test Passed")
        if test.passed:
            return self.run_keyword(name, *args)

    @run_keyword_variant(resolve=0, dry_run=True)
    def run_keyword_if_timeout_occurred(self, name, *args):
        """Runs the given keyword if either a test or a keyword timeout has occurred.

        This keyword can only be used in a test teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        self._get_test_in_teardown("Run Keyword If Timeout Occurred")
        if self._context.timeout_occurred:
            return self.run_keyword(name, *args)

    def _get_test_in_teardown(self, kwname):
        ctx = self._context
        if ctx.test and ctx.in_test_teardown:
            return ctx.test
        raise RuntimeError(f"Keyword '{kwname}' can only be used in test teardown.")

    @run_keyword_variant(resolve=0, dry_run=True)
    def run_keyword_if_all_tests_passed(self, name, *args):
        """Runs the given keyword with the given arguments, if all tests passed.

        This keyword can only be used in a suite teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        suite = self._get_suite_in_teardown("Run Keyword If All Tests Passed")
        if suite.statistics.failed == 0:
            return self.run_keyword(name, *args)

    @run_keyword_variant(resolve=0, dry_run=True)
    def run_keyword_if_any_tests_failed(self, name, *args):
        """Runs the given keyword with the given arguments, if one or more tests failed.

        This keyword can only be used in a suite teardown. Trying to use it
        anywhere else results in an error.

        Otherwise, this keyword works exactly like `Run Keyword`, see its
        documentation for more details.
        """
        suite = self._get_suite_in_teardown("Run Keyword If Any Tests Failed")
        if suite.statistics.failed > 0:
            return self.run_keyword(name, *args)

    def _get_suite_in_teardown(self, kw):
        if not self._context.in_suite_teardown:
            raise RuntimeError(f"Keyword '{kw}' can only be used in suite teardown.")
        return self._context.suite


class _Control(_BuiltInBase):

    def skip(self, msg="Skipped with Skip keyword."):
        """Skips the rest of the current test.

        Skips the remaining keywords in the current test and sets the given
        message to the test. If the test has teardown, it will be executed.
        """
        raise SkipExecution(msg)

    def skip_if(self, condition, msg=None):
        """Skips the rest of the current test if the ``condition`` is True.

        Skips the remaining keywords in the current test and sets the given
        message to the test. If ``msg`` is not given, the ``condition`` will
        be used as the message. If the test has teardown, it will be executed.

        If the ``condition`` evaluates to False, does nothing.
        """
        if self._is_true(condition):
            raise SkipExecution(msg or condition)

    def continue_for_loop(self):
        """Skips the current FOR loop iteration and continues from the next.

        ---

        *NOTE:* Robot Framework 5.0 added support for native ``CONTINUE`` statement that
        is recommended over this keyword. In the examples below, ``Continue For Loop``
        can simply be replaced with ``CONTINUE``. In addition to that, native ``IF``
        syntax (new in RF 4.0) or inline ``IF`` syntax (new in RF 5.0) can be used
        instead of ``Run Keyword If``. For example, the first example below could be
        written like this instead:

        | IF    '${var}' == 'CONTINUE'    CONTINUE

        This keyword will eventually be deprecated and removed.

        ---

        Skips the remaining keywords in the current FOR loop iteration and
        continues from the next one. Starting from Robot Framework 5.0, this
        keyword can only be used inside a loop, not in a keyword used in a loop.

        Example:
        | FOR | ${var}         | IN                     | @{VALUES}         |
        |     | Run Keyword If | '${var}' == 'CONTINUE' | Continue For Loop |
        |     | Do Something   | ${var}                 |
        | END |

        See `Continue For Loop If` to conditionally continue a FOR loop without
        using `Run Keyword If` or other wrapper keywords.
        """
        if not self._context.allow_loop_control:
            raise DataError("'Continue For Loop' can only be used inside a loop.")
        self.log("Continuing for loop from the next iteration.")
        raise ContinueLoop

    def continue_for_loop_if(self, condition):
        """Skips the current FOR loop iteration if the ``condition`` is true.

        ---

        *NOTE:* Robot Framework 5.0 added support for native ``CONTINUE`` statement
        and for inline ``IF``, and that combination should be used instead of this
        keyword. For example, ``Continue For Loop If`` usage in the example below
        could be replaced with

        | IF    '${var}' == 'CONTINUE'    CONTINUE

        This keyword will eventually be deprecated and removed.

        ---

        A wrapper for `Continue For Loop` to continue a FOR loop based on
        the given condition. The condition is evaluated using the same
        semantics as with `Should Be True` keyword.

        Example:
        | FOR | ${var}               | IN                     | @{VALUES} |
        |     | Continue For Loop If | '${var}' == 'CONTINUE' |
        |     | Do Something         | ${var}                 |
        | END |
        """
        if not self._context.allow_loop_control:
            raise DataError("'Continue For Loop If' can only be used inside a loop.")
        if self._is_true(condition):
            self.continue_for_loop()

    def exit_for_loop(self):
        """Stops executing the enclosing FOR loop.

        ---

        *NOTE:* Robot Framework 5.0 added support for native ``BREAK`` statement that
        is recommended over this keyword. In the examples below, ``Exit For Loop``
        can simply be replaced with ``BREAK``. In addition to that, native ``IF``
        syntax (new in RF 4.0) or inline ``IF`` syntax (new in RF 5.0) can be used
        instead of ``Run Keyword If``. For example, the first example below could be
        written like this instead:

        | IF    '${var}' == 'EXIT'    BREAK

        This keyword will eventually be deprecated and removed.

        ---

        Exits the enclosing FOR loop and continues execution after it. Starting
        from Robot Framework 5.0, this keyword can only be used inside a loop,
        not in a keyword used in a loop.

        Example:
        | FOR | ${var}         | IN                 | @{VALUES}     |
        |     | Run Keyword If | '${var}' == 'EXIT' | Exit For Loop |
        |     | Do Something   | ${var} |
        | END |

        See `Exit For Loop If` to conditionally exit a FOR loop without
        using `Run Keyword If` or other wrapper keywords.
        """
        if not self._context.allow_loop_control:
            raise DataError("'Exit For Loop' can only be used inside a loop.")
        self.log("Exiting for loop altogether.")
        raise BreakLoop

    def exit_for_loop_if(self, condition):
        """Stops executing the enclosing FOR loop if the ``condition`` is true.

        ---

        *NOTE:* Robot Framework 5.0 added support for native ``BREAK`` statement
        and for inline ``IF``, and that combination should be used instead of this
        keyword. For example, ``Exit For Loop If`` usage in the example below
        could be replaced with

        | IF    '${var}' == 'EXIT'    BREAK

        This keyword will eventually be deprecated and removed.

        ---

        A wrapper for `Exit For Loop` to exit a FOR loop based on
        the given condition. The condition is evaluated using the same
        semantics as with `Should Be True` keyword.

        Example:
        | FOR | ${var}           | IN                 | @{VALUES} |
        |     | Exit For Loop If | '${var}' == 'EXIT' |
        |     | Do Something     | ${var}             |
        | END |
        """
        if not self._context.allow_loop_control:
            raise DataError("'Exit For Loop If' can only be used inside a loop.")
        if self._is_true(condition):
            self.exit_for_loop()

    @run_keyword_variant(resolve=0)
    def return_from_keyword(self, *return_values):
        """Returns from the enclosing user keyword.

        ---

        *NOTE:* Robot Framework 5.0 added support for native ``RETURN`` statement that
        is recommended over this keyword. In the examples below, ``Return From Keyword``
        can simply be replaced with ``RETURN``. In addition to that, native ``IF``
        syntax (new in RF 4.0) or inline ``IF`` syntax (new in RF 5.0) can be used
        instead of ``Run Keyword If``. For example, the first example below could be
        written like this instead:

        | IF    ${rc} < 0    RETURN

        This keyword will eventually be deprecated and removed.

        ---

        This keyword can be used to return from a user keyword with PASS status
        without executing it fully. It is also possible to return values
        similarly as with the ``[Return]`` setting. For more detailed information
        about working with the return values, see the User Guide.

        This keyword is typically wrapped to some other keyword, such as
        `Run Keyword If`, to return based on a condition:

        | Run Keyword If    ${rc} < 0    Return From Keyword

        It is possible to use this keyword to return from a keyword also inside
        a for loop. That, as well as returning values, is demonstrated by the
        `Find Index` keyword in the following somewhat advanced example.
        Notice that it is often a good idea to move this kind of complicated
        logic into a library.

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
        |    FOR    ${item}    IN    @{items}
        |        Run Keyword If    '${item}' == '${element}'    Return From Keyword    ${index}
        |        ${index} =    Set Variable    ${index + 1}
        |    END
        |    Return From Keyword    ${-1}

        The most common use case, returning based on an expression, can be
        accomplished directly with `Return From Keyword If`. See also
        `Run Keyword And Return` and `Run Keyword And Return If`.
        """
        self._return_from_keyword(return_values)

    def _return_from_keyword(self, return_values=None, failures=None):
        self.log("Returning from the enclosing user keyword.")
        raise ReturnFromKeyword(return_values, failures)

    @run_keyword_variant(resolve=1)
    def return_from_keyword_if(self, condition, *return_values):
        """Returns from the enclosing user keyword if ``condition`` is true.

        ---

        *NOTE:* Robot Framework 5.0 added support for native ``RETURN`` statement
        and for inline ``IF``, and that combination should be used instead of this
        keyword. For example, `Return From Keyword If` usage in the `Find Index`
        example below could be replaced with this:

        | IF    '${item}' == '${element}'    RETURN    ${index}

        This keyword will eventually be deprecated and removed.

        ---

        A wrapper for `Return From Keyword` to return based on the given
        condition. The condition is evaluated using the same semantics as
        with `Should Be True` keyword.

        Given the same example as in `Return From Keyword`, we can rewrite the
        `Find Index` keyword as follows:

        | ***** Keywords *****
        | Find Index
        |    [Arguments]    ${element}    @{items}
        |    ${index} =    Set Variable    ${0}
        |    FOR    ${item}    IN    @{items}
        |        Return From Keyword If    '${item}' == '${element}'    ${index}
        |        ${index} =    Set Variable    ${index + 1}
        |    END
        |    Return From Keyword    ${-1}

        See also `Run Keyword And Return` and `Run Keyword And Return If`.
        """
        if self._is_true(condition):
            self._return_from_keyword(return_values)

    @run_keyword_variant(resolve=0, dry_run=True)
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
        """
        try:
            ret = self.run_keyword(name, *args)
        except ExecutionFailed as err:
            self._return_from_keyword(failures=[err])
        else:
            self._return_from_keyword(return_values=[escape(ret)])

    @run_keyword_variant(resolve=1, dry_run=True)
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
        In cases where execution cannot continue due to external factors,
        it is often safer to fail the test case and make it non-critical.
        """
        message = message.strip()
        if not message:
            raise RuntimeError("Message cannot be empty.")
        self._set_and_remove_tags(tags)
        log_message, level = self._get_logged_test_message_and_level(message)
        self.log(f"Execution passed with message:\n{log_message}", level)
        raise PassExecution(message)

    @run_keyword_variant(resolve=1)
    def pass_execution_if(self, condition, message, *tags):
        """Conditionally skips rest of the current test, setup, or teardown with PASS status.

        A wrapper for `Pass Execution` to skip rest of the current test,
        setup or teardown based the given ``condition``. The condition is
        evaluated similarly as with `Should Be True` keyword, and ``message``
        and ``*tags`` have same semantics as with `Pass Execution`.

        Example:
        | FOR | ${var}            | IN                     | @{VALUES}               |
        |     | Pass Execution If | '${var}' == 'EXPECTED' | Correct value was found |
        |     | Do Something      | ${var}                 |
        | END |
        """
        if self._is_true(condition):
            message = self._variables.replace_string(message)
            tags = self._variables.replace_list(tags)
            self.pass_execution(message, *tags)


class _Misc(_BuiltInBase):

    def no_operation(self):
        """Does absolutely nothing."""

    def sleep(self, time_, reason=None):
        """Pauses the test executed for the given time.

        ``time`` may be either a number or a time string. Time strings are in
        a format such as ``1 day 2 hours 3 minutes 4 seconds 5milliseconds`` or
        ``1d 2h 3m 4s 5ms``, and they are fully explained in an appendix of
        Robot Framework User Guide. Providing a value without specifying minutes
        or seconds, defaults to seconds.
        Optional `reason` can be used to explain why
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
        self.log(f"Slept {secs_to_timestr(seconds)}.")
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
            time.sleep(min(remaining, 0.01))

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
            return ""
        items = [str(item) for item in items]
        if items[0].startswith("SEPARATOR="):
            sep = items[0][len("SEPARATOR=") :]
            items = items[1:]
        else:
            sep = " "
        return sep.join(items)

    def log(
        self,
        message,
        level="INFO",
        html=False,
        console=False,
        repr="DEPRECATED",
        formatter="str",
    ):
        r"""Logs the given message with the given level.

        Valid levels are TRACE, DEBUG, INFO (default), WARN and ERROR.
        In addition to that, there are pseudo log levels HTML and CONSOLE that
        both log messages using INFO.

        Messages below the current active log
        level are ignored. See `Set Log Level` keyword and ``--loglevel``
        command line option for more details about setting the level.

        Messages logged with the WARN or ERROR levels are automatically
        visible also in the console and in the Test Execution Errors section
        in the log file.

        If the ``html`` argument is given a true value (see `Boolean
        arguments`) or the HTML pseudo log level is used, the message is
        considered to be HTML and special characters
        such as ``<`` are not escaped. For example, logging
        ``<img src="image.png">`` creates an image in this case, but
        otherwise the message is that exact string. When using the HTML pseudo
        level, the messages is logged using the INFO level.

        If the ``console`` argument is true or the CONSOLE pseudo level is
        used, the message is written both to the console and to the log file.
        When using the CONSOLE pseudo level, the message is logged using the
        INFO level. If the message should not be logged to the log file or there
        are special formatting needs, use the `Log To Console` keyword instead.

        The ``formatter`` argument controls how to format the string
        representation of the message. Possible values are ``str`` (default),
        ``repr``, ``ascii``, ``len``, and ``type``. They work similarly to
        Python built-in functions with same names. When using ``repr``, bigger
        lists, dictionaries and other containers are also pretty-printed so
        that there is one item per row. For more details see `String
        representations`.

        The old way to control string representation was using the ``repr``
        argument. This argument has been deprecated and ``formatter=repr``
        should be used instead.

        Examples:
        | Log | Hello, world!        |          |   | # Normal INFO message.   |
        | Log | Warning, world!      | WARN     |   | # Warning.               |
        | Log | <b>Hello</b>, world! | html=yes |   | # INFO message as HTML.  |
        | Log | <b>Hello</b>, world! | HTML     |   | # Same as above.         |
        | Log | <b>Hello</b>, world! | DEBUG    | html=true | # DEBUG as HTML. |
        | Log | Hello, console!   | console=yes | | # Log also to the console. |
        | Log | Hello, console!   | CONSOLE     | | # Log also to the console. |
        | Log | Null is \x00    | formatter=repr | | # Log ``'Null is \x00'``. |

        See `Log Many` if you want to log multiple messages in one go, and
        `Log To Console` if you only want to write to the console.

        Formatter options ``type`` and ``len`` are new in Robot Framework 5.0.
        The CONSOLE level is new in Robot Framework 6.1.
        """
        # TODO: Remove `repr` altogether in RF 8.0. It was deprecated in RF 5.0.
        if repr == "DEPRECATED":
            formatter = self._get_formatter(formatter)
        else:
            logger.warn(
                "The 'repr' argument of 'BuiltIn.Log' is deprecated. "
                "Use 'formatter=repr' instead."
            )
            formatter = prepr if is_truthy(repr) else self._get_formatter(formatter)
        message = formatter(message)
        logger.write(message, level, html)
        if console:
            logger.console(message)

    def _get_formatter(self, name):
        formatters = {
            "str": safe_str,
            "repr": prepr,
            "ascii": ascii,
            "len": len,
            "type": lambda x: type(x).__name__,
        }
        try:
            return formatters[name.lower()]
        except KeyError:
            raise ValueError(
                f"Invalid formatter '{name}'. Available {seq2str(formatters)}."
            )

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
            match = search_variable(msg)
            value = self._variables.replace_scalar(msg)
            if match.is_list_variable():
                yield from value
            elif match.is_dict_variable():
                for name, value in value.items():
                    yield f"{name}={value}"
            else:
                yield value

    def log_to_console(self, message, stream="STDOUT", no_newline=False, format=""):
        """Logs the given message to the console.

        By default uses the standard output stream. Using the standard error
        stream is possible by giving the ``stream`` argument value ``STDERR``
        (case-insensitive).

        By default appends a newline to the logged message. This can be
        disabled by giving the ``no_newline`` argument a true value (see
        `Boolean arguments`).

        By default adds no alignment formatting. The ``format`` argument allows,
        for example, alignment and customized padding of the log message. Please see the
        [https://docs.python.org/3/library/string.html#formatspec|format specification] for
        detailed alignment possibilities. This argument is new in Robot
        Framework 5.0.

        Examples:
        | Log To Console | Hello, console!             |                 |
        | Log To Console | Hello, stderr!              | STDERR          |
        | Log To Console | Message starts here and is  | no_newline=true |
        | Log To Console | continued without newline.  |                 |
        | Log To Console | center message with * pad   | format=*^60     |
        | Log To Console | 30 spaces before msg starts | format=>30      |

        This keyword does not log the message to the normal log file. Use
        `Log` keyword, possibly with argument ``console``, if that is desired.
        """
        if format:
            format = "{:" + format + "}"
            message = format.format(message)
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
        """Sets the log threshold to the specified level.

        Messages below the level will not logged. The default logging level is
        INFO, but it can be overridden with the ``--loglevel`` command line option.
        The available levels are TRACE, DEBUG, INFO (default), WARN, ERROR and NONE
        (no logging).

        The old level is returned and can be used for setting the level back
        later. An alternative way to reset the level is using the dedicated
        `Reset Log Level` keyword.
        """
        old = self._context.output.set_log_level(level)
        self._namespace.variables.set_global("${LOG_LEVEL}", level.upper())
        self.log(f"Log level changed from {old} to {level.upper()}.", level="DEBUG")
        return old

    def reset_log_level(self):
        """Resets the log level to the original value.

        The original log level is set from the command line with the ``--loglevel``
        option and is INFO by default. The active log level can be changed using
        the `Set Log Level` keyword.

        New in Robot Framework 7.0.
        """
        level = self._context.output.initial_log_level
        return self.set_log_level(level)

    def reload_library(self, name_or_instance):
        """Rechecks what keywords the specified library provides.

        Can be called explicitly in the test data or by a library itself
        when keywords it provides have changed.

        The library can be specified by its name or as the active instance of
        the library. The latter is especially useful if the library itself
        calls this keyword as a method.
        """
        lib = self._namespace.reload_library(name_or_instance)
        self.log(f"Reloaded library {lib.name} with {len(lib.keywords)} keywords.")

    @run_keyword_variant(resolve=0)
    def import_library(self, name, *args):
        """Imports a library with the given name and optional arguments.

        This functionality allows dynamic importing of libraries while tests
        are running. That may be necessary, if the library itself is dynamic
        and not yet available when test data is processed. In a normal case,
        libraries should be imported using the Library setting in the Setting
        section.

        This keyword supports importing libraries both using library
        names and physical paths. When paths are used, they must be
        given in absolute format or found from
        [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#module-search-path|
        search path]. Forward slashes can be used as path separators in all
        operating systems.

        It is possible to pass arguments to the imported library and also
        named argument syntax works if the library supports it. ``AS``
        syntax can be used to give a custom name to the imported library.

        Examples:
        | Import Library | MyLibrary |
        | Import Library | ${CURDIR}/Lib.py | arg1 | named=arg2 | AS | Custom |
        """
        args, alias = self._split_alias(args)
        try:
            self._namespace.import_library(name, args, alias)
        except DataError as err:
            raise RuntimeError(str(err))

    def _split_alias(self, args):
        if len(args) > 1 and normalize_whitespace(args[-2]) in ("WITH NAME", "AS"):
            return args[:-2], args[-1]
        return args, None

    @run_keyword_variant(resolve=0)
    def import_variables(self, path, *args):
        """Imports a variable file with the given path and optional arguments.

        Variables imported with this keyword are set into the test suite scope
        similarly when importing them in the Setting table using the Variables
        setting. These variables override possible existing variables with
        the same names. This functionality can thus be used to import new
        variables, for example, for each test in a test suite.

        The given path must be absolute or found from
        [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html##module-search-path|search path].
        Forward slashes can be used as path separator regardless
        the operating system.

        Examples:
        | Import Variables | ${CURDIR}/variables.py   |      |      |
        | Import Variables | ${CURDIR}/../vars/env.py | arg1 | arg2 |
        | Import Variables | file_from_pythonpath.py  |      |      |
        """
        try:
            self._namespace.import_variables(path, list(args), overwrite=True)
        except DataError as err:
            raise RuntimeError(str(err))

    @run_keyword_variant(resolve=0)
    def import_resource(self, path):
        """Imports a resource file with the given path.

        Resources imported with this keyword are set into the test suite scope
        similarly when importing them in the Setting table using the Resource
        setting.

        The given path must be absolute or found from
        [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#module-search-path|search path].
        Forward slashes can be used as path separator regardless
        the operating system.

        Examples:
        | Import Resource | ${CURDIR}/resource.txt |
        | Import Resource | ${CURDIR}/../resources/resource.html |
        | Import Resource | found_from_pythonpath.robot |
        """
        try:
            self._namespace.import_resource(path)
        except DataError as err:
            raise RuntimeError(str(err))

    def set_library_search_order(self, *search_order):
        """Sets the resolution order to use when a name matches multiple keywords.

        The library search order is used to resolve conflicts when a keyword name
        that is used matches multiple keyword implementations. The first library
        (or resource, see below) containing the keyword is selected and that
        keyword implementation used. If the keyword is not found from any library
        (or resource), execution fails the same way as when the search order is
        not set.

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
        - The search order is valid only in the suite where this keyword is used.
        - Keywords in resources always have higher priority than
          keywords in libraries regardless the search order.
        - The old order is returned and can be used to reset the search order later.
        - Calling this keyword without arguments removes possible search order.
        - Library and resource names in the search order are both case and space
          insensitive.
        """
        return self._namespace.set_search_order(search_order)

    def keyword_should_exist(self, name, msg=None):
        """Fails unless the given keyword exists in the current scope.

        Fails also if there is more than one keyword with the same name.
        Works both with the short name (e.g. ``Log``) and the full name
        (e.g. ``BuiltIn.Log``).

        The default error message can be overridden with the ``msg`` argument.

        See also `Variable Should Exist`.
        """
        try:
            kw = self._namespace.get_runner(name, recommend_on_failure=False).keyword
            if kw.error:
                raise DataError(kw.error)
        except DataError as err:
            raise AssertionError(msg or err.message)

    def get_time(self, format="timestamp", time_="NOW"):
        """Returns the given time in the requested format.

        *NOTE:* DateTime library contains much more flexible keywords for
        getting the current date and time and for date and time handling in
        general.

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
           time is used.

        4) If ``time`` is equal to ``UTC``, the current time in
           [http://en.wikipedia.org/wiki/Coordinated_Universal_Time|UTC]
           is used.

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
        """
        return get_time(format, parse_time(time_))

    def evaluate(self, expression, modules=None, namespace=None):
        """Evaluates the given expression in Python and returns the result.

        ``expression`` is evaluated in Python as explained in the
        `Evaluating expressions` section.

        ``modules`` argument can be used to specify a comma separated
        list of Python modules to be imported and added to the evaluation
        namespace.

        ``namespace`` argument can be used to pass a custom evaluation
        namespace as a dictionary. Possible ``modules`` are added to this
        namespace.

        Variables used like ``${variable}`` are replaced in the expression
        before evaluation. Variables are also available in the evaluation
        namespace and can be accessed using the special ``$variable`` syntax
        as explained in the `Evaluating expressions` section.

        Starting from Robot Framework 3.2, modules used in the expression are
        imported automatically. There are, however, two cases where they need to
        be explicitly specified using the ``modules`` argument:

        - When nested modules like ``rootmod.submod`` are implemented so that
          the root module does not automatically import sub modules. This is
          illustrated by the ``selenium.webdriver`` example below.

        - When using a module in the expression part of a list comprehension.
          This is illustrated by the ``json`` example below.

        Examples (expecting ``${result}`` is number 3.14):
        | ${status} =  | Evaluate | 0 < ${result} < 10 | # Would also work with string '3.14' |
        | ${status} =  | Evaluate | 0 < $result < 10   | # Using variable itself, not string representation |
        | ${random} =  | Evaluate | random.randint(0, sys.maxsize) |
        | ${options} = | Evaluate | selenium.webdriver.ChromeOptions() | modules=selenium.webdriver |
        | ${items} =   | Evaluate | [json.loads(item) for item in ('1', '"b"')] | modules=json |
        | ${ns} =      | Create Dictionary | x=${4}    | y=${2}              |
        | ${result} =  | Evaluate | x*10 + y           | namespace=${ns}     |
        =>
        | ${status} = True
        | ${random} = <random integer>
        | ${options} = ChromeOptions instance
        | ${items} = [1, 'b']
        | ${result} = 42

        *NOTE*: Prior to Robot Framework 3.2 using ``modules=rootmod.submod``
        was not enough to make the root module itself available in the
        evaluation namespace. It needed to be taken into use explicitly like
        ``modules=rootmod, rootmod.submod``.
        """
        try:
            return evaluate_expression(
                expression,
                self._variables.current,
                modules,
                namespace,
            )
        except DataError as err:
            raise RuntimeError(err.message)

    def call_method(self, object, method_name, *args, **kwargs):
        """Calls the named method of the given object with the provided arguments.

        The possible return value from the method is returned and can be
        assigned to a variable. Keyword fails both if the object does not have
        a method with the given name or if executing the method raises an
        exception.

        Possible equal signs in arguments must be escaped with a backslash
        like ``\\=``.

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
            raise RuntimeError(
                f"{type(object).__name__} object does not have method '{method_name}'."
            )
        try:
            return method(*args, **kwargs)
        except Exception as err:
            msg = get_error_message()
            raise RuntimeError(f"Calling method '{method_name}' failed: {msg}") from err

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
            return ""
        if len(patterns) == 1:
            return re.escape(patterns[0])
        return [re.escape(p) for p in patterns]

    def set_test_message(self, message, append=False, separator=" "):
        """Sets message for the current test case.

        If the optional ``append`` argument is given a true value (see `Boolean
        arguments`), the given ``message`` is added after the possible earlier
        message.

        An optional ``separator`` argument can be used to provide custom separator
        string when appending to the old text. A single space is used as separator
        by default.

        In test teardown this keyword can alter the possible failure message,
        but otherwise failures override messages set by this keyword. Notice
        that in teardown the message is available as a built-in variable
        ``${TEST MESSAGE}``.

        It is possible to use HTML format in the message by starting the message
        with ``*HTML*``.

        Examples:
        | Set Test Message | My message           |                          |
        | Set Test Message | is continued.        | append=yes               |
        | Should Be Equal  | ${TEST MESSAGE}      | My message is continued. |
        | Set Test Message | `*`HTML`*` <b>Hello!</b> |                      |

        This keyword can not be used in suite setup or suite teardown.

        The ``separator`` argument is new in Robot Framework 7.2.
        """
        test = self._context.test
        if not test:
            raise RuntimeError(
                "'Set Test Message' keyword cannot be used in suite setup or teardown."
            )
        test.message = self._get_new_text(
            test.message, message, append, handle_html=True, separator=separator
        )
        if self._context.in_test_teardown:
            self._variables.set_test("${TEST_MESSAGE}", test.message)
        message, level = self._get_logged_test_message_and_level(test.message)
        self.log(f"Set test message to:\n{message}", level)

    def _get_new_text(self, old, new, append, handle_html=False, separator=" "):
        if not isinstance(new, str):
            new = str(new)
        if not (is_truthy(append) and old):
            return new
        if handle_html:
            if new.startswith("*HTML*"):
                new = new[6:].lstrip()
                if not old.startswith("*HTML*"):
                    old = f"*HTML* {html_escape(old)}"
                separator = html_escape(separator)
            elif old.startswith("*HTML*"):
                new = html_escape(new)
                separator = html_escape(separator)
        return f"{old}{separator}{new}"

    def _get_logged_test_message_and_level(self, message):
        if message.startswith("*HTML*"):
            return message[6:].lstrip(), "HTML"
        return message, "INFO"

    def set_test_documentation(self, doc, append=False, separator=" "):
        """Sets documentation for the current test case.

        The possible existing documentation is overwritten by default, but
        this can be changed using the optional ``append`` argument similarly
        as with `Set Test Message` keyword.

        An optional ``separator`` argument can be used to provide custom separator
        string when appending to the old text. A single space is used as separator
        by default.

        The current test documentation is available as a built-in variable
        ``${TEST DOCUMENTATION}``. This keyword can not be used in suite
        setup or suite teardown.

        The ``separator`` argument is new in Robot Framework 7.2.
        """
        test = self._context.test
        if not test:
            raise RuntimeError(
                "'Set Test Documentation' keyword cannot be used in "
                "suite setup or teardown."
            )
        test.doc = self._get_new_text(test.doc, doc, append, separator=separator)
        self._variables.set_test("${TEST_DOCUMENTATION}", test.doc)
        self.log(f"Set test documentation to:\n{test.doc}")

    def set_suite_documentation(self, doc, append=False, top=False, separator=" "):
        """Sets documentation for the current test suite.

        By default, the possible existing documentation is overwritten, but
        this can be changed using the optional ``append`` argument similarly
        as with `Set Test Message` keyword.

        This keyword sets the documentation of the current suite by default.
        If the optional ``top`` argument is given a true value (see `Boolean
        arguments`), the documentation of the top level suite is altered
        instead.

        An optional ``separator`` argument can be used to provide custom separator
        string when appending to the old text. A single space is used as separator
        by default.

        The documentation of the current suite is available as a built-in
        variable ``${SUITE DOCUMENTATION}``.

        The ``separator`` argument is new in Robot Framework 7.2.
        """
        suite = self._get_context(top).suite
        suite.doc = self._get_new_text(suite.doc, doc, append, separator=separator)
        self._variables.set_suite("${SUITE_DOCUMENTATION}", suite.doc, top)
        self.log(f"Set suite documentation to:\n{suite.doc}")

    def set_suite_metadata(self, name, value, append=False, top=False, separator=" "):
        """Sets metadata for the current test suite.

        By default, possible existing metadata values are overwritten, but
        this can be changed using the optional ``append`` argument similarly
        as with `Set Test Message` keyword.

        This keyword sets the metadata of the current suite by default.
        If the optional ``top`` argument is given a true value (see `Boolean
        arguments`), the metadata of the top level suite is altered instead.

        An optional ``separator`` argument can be used to provide custom separator
        string when appending to the old text. A single space is used as separator
        by default.

        The metadata of the current suite is available as a built-in variable
        ``${SUITE METADATA}`` in a Python dictionary. Notice that modifying this
        variable directly has no effect on the actual metadata the suite has.

        The ``separator`` argument is new in Robot Framework 7.2.
        """
        if not isinstance(name, str):
            name = str(name)
        metadata = self._get_context(top).suite.metadata
        original = metadata.get(name, "")
        metadata[name] = self._get_new_text(
            original, value, append, separator=separator
        )
        self._variables.set_suite("${SUITE_METADATA}", metadata.copy(), top)
        self.log(f"Set suite metadata '{name}' to value '{metadata[name]}'.")

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
            ctx.variables.set_test("@{TEST_TAGS}", list(ctx.test.tags))
        elif not ctx.in_suite_teardown:
            ctx.suite.set_tags(tags, persist=True)
        else:
            raise RuntimeError("'Set Tags' cannot be used in suite teardown.")
        self.log(f"Set tag{s(tags)} {seq2str(tags)}.")

    def remove_tags(self, *tags):
        """Removes given ``tags`` from the current test or all tests in a suite.

        Tags can be given exactly or using a pattern with ``*``, ``?`` and
        ``[chars]`` acting as wildcards. See the `Glob patterns` section
        for more information.

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
            ctx.variables.set_test("@{TEST_TAGS}", list(ctx.test.tags))
        elif not ctx.in_suite_teardown:
            ctx.suite.set_tags(remove=tags, persist=True)
        else:
            raise RuntimeError("'Remove Tags' cannot be used in suite teardown.")
        self.log(f"Removed tag{s(tags)} {seq2str(tags)}.")

    def get_library_instance(self, name=None, all=False):
        """Returns the currently active instance of the specified library.

        This keyword makes it easy for libraries to interact with
        other libraries that have state. This is illustrated by
        the Python example below:

        | from robot.libraries.BuiltIn import BuiltIn
        |
        | def title_should_start_with(expected):
        |     seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
        |     title = seleniumlib.get_title()
        |     if not title.startswith(expected):
        |         raise AssertionError(f"Title '{title}' did not start with '{expected}'.")

        It is also possible to use this keyword in the test data and
        pass the returned library instance to another keyword. If a
        library is imported with a custom name, the ``name`` used to get
        the instance must be that name and not the original library name.

        If the optional argument ``all`` is given a true value, then a
        dictionary mapping all library names to instances will be returned.

        Example:
        | &{all libs} = | Get library instance | all=True |
        """
        if all:
            return self._namespace.get_library_instances()
        try:
            return self._namespace.get_library_instance(name)
        except DataError as err:
            raise RuntimeError(str(err))


class BuiltIn(_Verify, _Converter, _Variables, _RunKeyword, _Control, _Misc):
    r"""An always available standard library with often needed keywords.

    ``BuiltIn`` is Robot Framework's standard library that provides a set
    of generic keywords needed often. It is imported automatically and
    thus always available. The provided keywords can be used, for example,
    for verifications (e.g. `Should Be Equal`, `Should Contain`),
    conversions (e.g. `Convert To Integer`) and for various other purposes
    (e.g. `Log`, `Sleep`, `Run Keyword If`, `Set Global Variable`).

    == Table of contents ==

    %TOC%

    = HTML error messages =

    Many of the keywords accept an optional error message to use if the keyword
    fails, and it is possible to use HTML in these messages by prefixing them
    with ``*HTML*``. See `Fail` keyword for a usage example. Notice that using
    HTML in messages is not limited to BuiltIn library but works with any
    error message.

    = Evaluating expressions =

    Many keywords, such as `Evaluate`, `Run Keyword If` and `Should Be True`,
    accept an expression that is evaluated in Python.

    == Evaluation namespace ==

    Expressions are evaluated using Python's
    [http://docs.python.org/library/functions.html#eval|eval] function so
    that all Python built-ins like ``len()`` and ``int()`` are available.
    In addition to that, all unrecognized variables are considered to be
    modules that are automatically imported. It is possible to use all
    available Python modules, including the standard modules and the installed
    third party modules.

    Examples:
    | `Should Be True`    len('${result}') > 3
    | `Run Keyword If`    os.sep == '/'    Non-Windows Keyword
    | ${version} =    `Evaluate`    robot.__version__

    `Evaluate` also allows configuring the execution namespace with a custom
    namespace and with custom modules to be imported. The latter functionality
    is useful in special cases where the automatic module import does not work
    such as when using nested modules like ``rootmod.submod`` or list
    comprehensions. See the documentation of the `Evaluate` keyword for mode
    details.

    == Variables in expressions ==

    When a variable is used in the expressing using the normal ``${variable}``
    syntax, its value is replaced before the expression is evaluated. This
    means that the value used in the expression will be the string
    representation of the variable value, not the variable value itself.
    This is not a problem with numbers and other objects that have a string
    representation that can be evaluated directly, but with other objects
    the behavior depends on the string representation. Most importantly,
    strings must always be quoted, and if they can contain newlines, they must
    be triple quoted.

    Examples:
    | `Should Be True`    ${rc} < 10                   Return code greater than 10
    | `Run Keyword If`    '${status}' == 'PASS'        Log    Passed
    | `Run Keyword If`    'FAIL' in '''${output}'''    Log    Output contains FAIL

    Actual variables values are also available in the evaluation namespace.
    They can be accessed using special variable syntax without the curly
    braces like ``$variable``. These variables should never be quoted.

    Examples:
    | `Should Be True`    $rc < 10             Return code greater than 10
    | `Run Keyword If`    $status == 'PASS'    `Log`    Passed
    | `Run Keyword If`    'FAIL' in $output    `Log`    Output contains FAIL
    | `Should Be True`    len($result) > 1 and $result[1] == 'OK'
    | `Should Be True`    $result is not None

    Using the ``$variable`` syntax slows down expression evaluation a little.
    This should not typically matter, but should be taken into account if
    complex expressions are evaluated often and there are strict time
    constrains.

    Notice that instead of creating complicated expressions, it is often better
    to move the logic into a library. That eases maintenance and can also
    enhance execution speed.

    = Using variables with keywords creating or accessing variables =

    This library has special keywords `Set Global Variable`, `Set Suite Variable`,
    `Set Test Variable` and `Set Local Variable` for creating variables in
    different scopes. These keywords take the variable name and its value as
    arguments. The name can be given using the normal ``${variable}`` syntax or
    in escaped format either like ``$variable`` or ``\${variable}``. For example,
    these are typically equivalent and create new suite level variable
    ``${name}`` with value ``value``:

    | Set Suite Variable    ${name}     value
    | Set Suite Variable    $name       value
    | Set Suite Variable    \${name}    value

    A problem with using the normal ``${variable}`` syntax is that these
    keywords cannot easily know is the idea to create a variable with exactly
    that name or does that variable actually contain the name of the variable
    to create. If the variable does not initially exist, it will always be
    created. If it exists and its value is a variable name either in the normal
    or in the escaped syntax, variable with _that_ name is created instead.
    For example, if ``${name}`` variable would exist and contain value
    ``$example``, these examples would create different variables:

    | Set Suite Variable    ${name}     value    # Creates ${example}.
    | Set Suite Variable    $name       value    # Creates ${name}.
    | Set Suite Variable    \${name}    value    # Creates ${name}.

    Because the behavior when using the normal ``${variable}`` syntax depends
    on the possible existing value of the variable, it is *highly recommended
    to use the escaped ``$variable`` or ``\${variable}`` format instead*.

    This same problem occurs also with special keywords for accessing variables
    `Get Variable Value`, `Variable Should Exist` and `Variable Should Not Exist`.

    *NOTE:* It is recommended to use the ``VAR`` syntax introduced in Robot
    Framework 7.0 for creating variables in different scopes instead of the
    `Set Global/Suite/Test/Local Variable` keywords. It makes creating variables
    uniform and avoids all the problems discussed above.

    = Boolean arguments =

    Some keywords accept arguments that are handled as Boolean values true or
    false. If such an argument is given as a string, it is considered false if
    it is an empty string or equal to ``FALSE``, ``NONE``, ``NO``, ``OFF`` or
    ``0``, case-insensitively. Keywords verifying something that allow dropping
    actual and expected values from the possible error message also consider
    string ``no values`` to be false. Other strings are considered true unless
    the keyword documentation explicitly states otherwise, and other argument
    types are tested using the same
    [http://docs.python.org/library/stdtypes.html#truth|rules as in Python].

    True examples:
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=True         # Strings are generally true.
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=yes          # Same as the above.
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=${TRUE}      # Python ``True`` is true.
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=${42}        # Numbers other than 0 are true.

    False examples:
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=False        # String ``false`` is false.
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=no           # Also string ``no`` is false.
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=${EMPTY}     # Empty string is false.
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=${FALSE}     # Python ``False`` is false.
    | `Should Be Equal`    ${x}    ${y}    Custom error    values=no values    # ``no values`` works with ``values`` argument

    = Pattern matching =

    Many keywords accept arguments as either glob or regular expression patterns.

    == Glob patterns ==

    Some keywords, for example `Should Match`, support so called
    [http://en.wikipedia.org/wiki/Glob_(programming)|glob patterns] where:

    | ``*``        | matches any string, even an empty string                |
    | ``?``        | matches any single character                            |
    | ``[chars]``  | matches one character in the bracket                    |
    | ``[!chars]`` | matches one character not in the bracket                |
    | ``[a-z]``    | matches one character from the range in the bracket     |
    | ``[!a-z]``   | matches one character not from the range in the bracket |

    Unlike with glob patterns normally, path separator characters ``/`` and
    ``\`` and the newline character ``\n`` are matches by the above
    wildcards.

    == Regular expressions ==

    Some keywords, for example `Should Match Regexp`, support
    [http://en.wikipedia.org/wiki/Regular_expression|regular expressions]
    that are more powerful but also more complicated that glob patterns.
    The regular expression support is implemented using Python's
    [http://docs.python.org/library/re.html|re module] and its documentation
    should be consulted for more information about the syntax.

    Because the backslash character (``\``) is an escape character in
    Robot Framework test data, possible backslash characters in regular
    expressions need to be escaped with another backslash like ``\\d\\w+``.
    Strings that may contain special characters but should be handled
    as literal strings, can be escaped with the `Regexp Escape` keyword.

    = Multiline string comparison =

    `Should Be Equal` and `Should Be Equal As Strings` report the failures using
    [http://en.wikipedia.org/wiki/Diff_utility#Unified_format|unified diff
    format] if both strings have more than two lines.

    Example:
    | ${first} =     `Catenate`    SEPARATOR=\n    Not in second    Same    Differs    Same
    | ${second} =    `Catenate`    SEPARATOR=\n    Same    Differs2    Same    Not in first
    | `Should Be Equal`    ${first}    ${second}

    Results in the following error message:

    | Multiline strings are different:
    | --- first
    | +++ second
    | @@ -1,4 +1,4 @@
    | -Not in second
    |  Same
    | -Differs
    | +Differs2
    |  Same
    | +Not in first

    = String representations =

    Several keywords log values explicitly (e.g. `Log`) or implicitly (e.g.
    `Should Be Equal` when there are failures). By default, keywords log values
    using human-readable string representation, which means that strings
    like ``Hello`` and numbers like ``42`` are logged as-is. Most of the time
    this is the desired behavior, but there are some problems as well:

    - It is not possible to see difference between different objects that
      have the same string representation like string ``42`` and integer ``42``.
      `Should Be Equal` and some other keywords add the type information to
      the error message in these cases, though.

    - Non-printable characters such as the null byte are not visible.

    - Trailing whitespace is not visible.

    - Different newlines (``\r\n`` on Windows, ``\n`` elsewhere) cannot
      be separated from each others.

    - There are several Unicode characters that are different but look the
      same. One example is the Latin ``a`` (``\u0061``) and the Cyrillic
      ``а`` (``\u0430``). Error messages like ``a != а`` are not very helpful.

    - Some Unicode characters can be represented using
      [https://en.wikipedia.org/wiki/Unicode_equivalence|different forms].
      For example, ``ä`` can be represented either as a single code point
      ``\u00e4`` or using two combined code points ``\u0061`` and ``\u0308``.
      Such forms are considered canonically equivalent, but strings
      containing them are not considered equal when compared in Python. Error
      messages like ``ä != ä`` are not that helpful either.

    - Containers such as lists and dictionaries are formatted into a single
      line making it hard to see individual items they contain.

    To overcome the above problems, some keywords such as `Log` and
    `Should Be Equal` have an optional ``formatter`` argument that can be
    used to configure the string representation. The supported values are
    ``str`` (default), ``repr``, and ``ascii`` that work similarly as
    [https://docs.python.org/library/functions.html|Python built-in functions]
    with same names. More detailed semantics are explained below.

    == str ==

    Use the human-readable string representation. Equivalent to using ``str()``
    in Python. This is the default.

    == repr ==

    Use the machine-readable string representation. Similar to using ``repr()``
    in Python, which means that strings like ``Hello`` are logged like
    ``'Hello'``, newlines and non-printable characters are escaped like ``\n``
    and ``\x00``, and so on. Non-ASCII characters are shown as-is like ``ä``.

    In this mode bigger lists, dictionaries and other containers are
    pretty-printed so that there is one item per row.

    == ascii ==

    Same as using ``ascii()`` in Python. Similar to using ``repr`` explained above
    but with the following differences:

    - Non-ASCII characters are escaped like ``\xe4`` instead of
      showing them as-is like ``ä``. This makes it easier to see differences
      between Unicode characters that look the same but are not equal.
    - Containers are not pretty-printed.
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = get_version()


class RobotNotRunningError(AttributeError):
    """Used when something cannot be done because Robot is not running.

    Based on AttributeError to be backwards compatible with RF < 2.8.5.
    May later be based directly on Exception, so new code should except
    this exception explicitly.
    """


def register_run_keyword(library, keyword, args_to_process=0, deprecation_warning=True):
    """Tell Robot Framework that this keyword runs other keywords internally.

    *NOTE:* This API will change in the future. For more information see
    https://github.com/robotframework/robotframework/issues/2190.

    :param library: Name of the library the keyword belongs to.
    :param keyword: Name of the keyword itself.
    :param args_to_process: How many arguments to process normally before
        passing them to the keyword. Other arguments are not touched at all.
    :param deprecation_warning: Set to ``False```to avoid the warning.

    Registered keywords are handled specially by Robot so that:

    - Their arguments are not resolved normally (use ``args_to_process``
      to control that). This basically means not replacing variables or
      handling escapes.
    - They are not stopped by timeouts. Prior to Robot Framework 7.3, timeouts
      occurring when these keywords were executing other keywords could corrupt
      output files. That bug has been fixed, so this use case why to register
      keywords as run keyword variants is not relevant anymore.
    - If there are conflicts with keyword names, these keywords have
      *lower* precedence than other keywords.

    Main use cases are:

    - Library keyword is using `BuiltIn.run_keyword` internally to execute other
      keywords. Registering the caller as a "run keyword variant" avoids variables
      and escapes in arguments being resolved multiple times. All arguments passed
      to `run_keyword` can and should be left unresolved.
    - Keyword has some need to not resolve variables in arguments. This way
      variable values are not logged anywhere by Robot automatically.

    As mentioned above, this API will likely be reimplemented in the future
    or there could be new API for library keywords to execute other keywords.
    External libraries can nevertheless use this API if they really need it and
    are aware of the possible breaking changes in the future.

    Examples::

        from robot.libraries.BuiltIn import BuiltIn, register_run_keyword

        def my_run_keyword(name, *args):
            # do something
            return BuiltIn().run_keyword(name, *args)

        register_run_keyword(__name__, 'My Run Keyword')

        -------------

        from robot.libraries.BuiltIn import BuiltIn, register_run_keyword

        class MyLibrary:
            def my_run_keyword_if(self, expression, name, *args):
                # Do something
                if self._is_true(expression):
                    return BuiltIn().run_keyword(name, *args)

        # Process one argument normally to get `expression` resolved.
        register_run_keyword('MyLibrary', 'my_run_keyword_if', args_to_process=1)
    """
    RUN_KW_REGISTER.register_run_keyword(
        library, keyword, args_to_process, deprecation_warning
    )
