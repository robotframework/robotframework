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
from robot.utils import get_error_message
from robot.variables import VariableIterator


class EmbeddedArguments:

    def __init__(self, name):
        if '${' in name:
            self.name, self.args = EmbeddedArgumentParser().parse(name)
        else:
            self.name, self.args = None, []

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
        name_regexp = ['^']
        for before, variable, string in VariableIterator(string, identifiers='$'):
            name, pattern = self._get_name_and_pattern(variable[2:-1])
            args.append(name)
            name_regexp.extend([re.escape(before), '(%s)' % pattern])
        name_regexp.extend([re.escape(string), '$'])
        name = self._compile_regexp(name_regexp) if args else None
        return name, args

    def _get_name_and_pattern(self, name):
        if ':' not in name:
            return name, self._default_pattern
        name, pattern = name.split(':', 1)
        return name, self._format_custom_regexp(pattern)

    def _format_custom_regexp(self, pattern):
        for formatter in (self._regexp_extensions_are_not_allowed,
                          self._make_groups_non_capturing,
                          self._unescape_curly_braces,
                          self._add_automatic_variable_pattern):
            pattern = formatter(pattern)
        return pattern

    def _regexp_extensions_are_not_allowed(self, pattern):
        if not self._regexp_extension.search(pattern):
            return pattern
        raise DataError('Regexp extensions are not allowed in embedded '
                        'arguments.')

    def _make_groups_non_capturing(self, pattern):
        return self._regexp_group_start.sub(self._regexp_group_escape, pattern)

    def _unescape_curly_braces(self, pattern):
        def unescaper(match):
            backslashes = len(match.group(1))
            return '\\' * (backslashes // 2 * 2) + match.group(2)
        return self._escaped_curly.sub(unescaper, pattern)

    def _add_automatic_variable_pattern(self, pattern):
        return '%s|%s' % (pattern, self._variable_pattern)

    def _compile_regexp(self, pattern):
        try:
            return re.compile(''.join(pattern), re.IGNORECASE)
        except Exception:
            raise DataError("Compiling embedded arguments regexp failed: %s"
                            % get_error_message())
