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
from typing import Any, Mapping, Sequence

from robot.errors import DataError
from robot.utils import get_error_message
from robot.variables import VariableMatches

from ..context import EXECUTION_CONTEXTS


class EmbeddedArguments:

    def __init__(self, name: re.Pattern,
                 args: Sequence[str] = (),
                 custom_patterns: 'Mapping[str, str]|None' = None):
        self.name = name
        self.args = tuple(args)
        self.custom_patterns = custom_patterns or None

    @classmethod
    def from_name(cls, name: str) -> 'EmbeddedArguments|None':
        return EmbeddedArgumentParser().parse(name) if '${' in name else None

    def match(self, name: str) -> 're.Match|None':
        return self.name.fullmatch(name)

    def map(self, args: Sequence[Any]) -> 'list[tuple[str, Any]]':
        self.validate(args)
        return list(zip(self.args, args))

    def validate(self, args: Sequence[Any]):
        """Validate that embedded args match custom regexps.

        Initial validation is done already when matching keywords, but this
        validation makes sure arguments match also if they are given as variables.

        Currently, argument not matching only causes a deprecation warning, but
        that will be changed to ``ValueError`` in RF 8.0:
        https://github.com/robotframework/robotframework/issues/4069
        """
        if not self.custom_patterns:
            return
        for name, value in zip(self.args, args):
            if name in self.custom_patterns and isinstance(value, str):
                pattern = self.custom_patterns[name]
                if not re.fullmatch(pattern, value):
                    # TODO: Change to `raise ValueError(...)` in RF 8.0.
                    context = EXECUTION_CONTEXTS.current
                    context.warn(f"Embedded argument '{name}' got value {value!r} "
                                 f"that does not match custom pattern {pattern!r}. "
                                 f"The argument is still accepted, but this behavior "
                                 f"will change in Robot Framework 8.0.")


class EmbeddedArgumentParser:
    _regexp_extension = re.compile(r'(?<!\\)\(\?.+\)')
    _regexp_group_start = re.compile(r'(?<!\\)\((.*?)\)')
    _escaped_curly = re.compile(r'(\\+)([{}])')
    _regexp_group_escape = r'(?:\1)'
    _default_pattern = '.*?'
    _variable_pattern = r'\$\{[^\}]+\}'

    def parse(self, string: str) -> 'EmbeddedArguments|None':
        name_parts = ['^']
        args = []
        custom_patterns = {}
        after = string
        for match in VariableMatches(' '.join(string.split()), identifiers='$'):
            arg, pattern, is_custom = self._get_name_and_pattern(match.base)
            args.append(arg)
            if is_custom:
                custom_patterns[arg] = pattern
                pattern = self._format_custom_regexp(pattern)
            name_parts.extend([re.escape(match.before), f'({pattern})'])
            after = match.after
        if not args:
            return None
        name_parts.extend([re.escape(after), '$'])
        name = self._compile_regexp(''.join(name_parts))
        return EmbeddedArguments(name, args, custom_patterns)

    def _get_name_and_pattern(self, name: str) -> 'tuple[str, str, bool]':
        if ':' in name:
            name, pattern = name.split(':', 1)
            custom = True
        else:
            pattern = self._default_pattern
            custom = False
        return name, pattern, custom

    def _format_custom_regexp(self, pattern: str) -> str:
        for formatter in (self._regexp_extensions_are_not_allowed,
                          self._make_groups_non_capturing,
                          self._unescape_curly_braces,
                          self._escape_escapes,
                          self._add_automatic_variable_pattern):
            pattern = formatter(pattern)
        return pattern

    def _regexp_extensions_are_not_allowed(self, pattern: str) -> str:
        if self._regexp_extension.search(pattern):
            raise DataError('Regexp extensions are not allowed in embedded arguments.')
        return pattern

    def _make_groups_non_capturing(self, pattern: str) -> str:
        return self._regexp_group_start.sub(self._regexp_group_escape, pattern)

    def _unescape_curly_braces(self, pattern: str) -> str:
        # Users must escape possible lone curly braces in patters (e.g. `${x:\{}`)
        # or otherwise the variable syntax is invalid.
        def unescape(match):
            backslashes = len(match.group(1))
            return '\\' * (backslashes // 2 * 2) + match.group(2)
        return self._escaped_curly.sub(unescape, pattern)

    def _escape_escapes(self, pattern: str) -> str:
        # When keywords are matched, embedded arguments have not yet been
        # resolved which means possible escapes are still doubled. We thus
        # need to double them in the pattern as well.
        return pattern.replace(r'\\', r'\\\\')

    def _add_automatic_variable_pattern(self, pattern: str) -> str:
        return f'{pattern}|{self._variable_pattern}'

    def _compile_regexp(self, pattern: str) -> re.Pattern:
        try:
            return re.compile(pattern.replace(r'\ ', r'\s'), re.IGNORECASE)
        except Exception:
            raise DataError(f"Compiling embedded arguments regexp failed: "
                            f"{get_error_message()}")
