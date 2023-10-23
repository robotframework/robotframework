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

import re

from robot.errors import DataError
from robot.utils import get_error_message, is_string
from robot.variables import VariableMatches

from ..context import EXECUTION_CONTEXTS


class EmbeddedArguments:

    def __init__(self, name=None, args=(), custom_patterns=None):
        self.name = name
        self.args = args
        self.custom_patterns = custom_patterns

    @classmethod
    def from_name(cls, name):
        return EmbeddedArgumentParser().parse(name) if '${' in name else cls()

    def match(self, name):
        return self.name.match(name)

    def map(self, values):
        self.validate(values)
        return list(zip(self.args, values))

    def validate(self, values):
        """Validate that embedded args match custom regexps.

        Initial validation is done already when matching keywords, but this
        validation makes sure arguments match also if they are given as variables.

        Currently, argument not matching only causes a deprecation warning, but
        that will be changed to an actual failure in RF 8.0:
        https://github.com/robotframework/robotframework/issues/4069
        """
        if not self.custom_patterns:
            return
        for arg, value in zip(self.args, values):
            if arg in self.custom_patterns and is_string(value):
                pattern = self.custom_patterns[arg]
                if not re.fullmatch(pattern, value):
                    # TODO: Change to `raise ValueError(...)` in RF 8.0.
                    context = EXECUTION_CONTEXTS.current
                    context.warn(f"Embedded argument '{arg}' got value {value!r} "
                                 f"that does not match custom pattern {pattern!r}. "
                                 f"The argument is still accepted, but this behavior "
                                 f"will change in Robot Framework 8.0.")

    def __bool__(self):
        return self.name is not None


class EmbeddedArgumentParser:
    _regexp_extension = re.compile(r'(?<!\\)\(\?.+\)')
    _regexp_group_start = re.compile(r'(?<!\\)\((.*?)\)')
    _escaped_curly = re.compile(r'(\\+)([{}])')
    _regexp_group_escape = r'(?:\1)'
    _default_pattern = '.*?'
    _variable_pattern = r'\$\{[^\}]+\}'

    def parse(self, string):
        args = []
        custom_patterns = {}
        name_regexp = ['^']
        after = string
        for match in VariableMatches(string, identifiers='$'):
            name, pattern, custom = self._get_name_and_pattern(match.base)
            args.append(name)
            if custom:
                custom_patterns[name] = pattern
                pattern = self._format_custom_regexp(pattern)
            name_regexp.extend([re.escape(match.before), f'({pattern})'])
            after = match.after
        name_regexp.extend([re.escape(after), '$'])
        name = self._compile_regexp(name_regexp) if args else None
        return EmbeddedArguments(name, args, custom_patterns or None)

    def _get_name_and_pattern(self, name):
        if ':' in name:
            name, pattern = name.split(':', 1)
            custom = True
        else:
            pattern = self._default_pattern
            custom = False
        return name, pattern, custom

    def _format_custom_regexp(self, pattern):
        for formatter in (self._regexp_extensions_are_not_allowed,
                          self._make_groups_non_capturing,
                          self._unescape_curly_braces,
                          self._escape_escapes,
                          self._add_automatic_variable_pattern):
            pattern = formatter(pattern)
        return pattern

    def _regexp_extensions_are_not_allowed(self, pattern):
        if self._regexp_extension.search(pattern):
            raise DataError('Regexp extensions are not allowed in embedded arguments.')
        return pattern

    def _make_groups_non_capturing(self, pattern):
        return self._regexp_group_start.sub(self._regexp_group_escape, pattern)

    def _unescape_curly_braces(self, pattern):
        # Users must escape possible lone curly braces in patters (e.g. `${x:\{}`)
        # or otherwise the variable syntax is invalid.
        def unescape(match):
            backslashes = len(match.group(1))
            return '\\' * (backslashes // 2 * 2) + match.group(2)
        return self._escaped_curly.sub(unescape, pattern)

    def _escape_escapes(self, pattern):
        # When keywords are matched, embedded arguments have not yet been
        # resolved which means possible escapes are still doubled. We thus
        # need to double them in the pattern as well.
        return pattern.replace(r'\\', r'\\\\')

    def _add_automatic_variable_pattern(self, pattern):
        return f'{pattern}|{self._variable_pattern}'

    def _compile_regexp(self, pattern):
        try:
            return re.compile(''.join(pattern), re.IGNORECASE)
        except Exception:
            raise DataError("Compiling embedded arguments regexp failed: %s"
                            % get_error_message())
