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
import warnings
from typing import Mapping, Sequence

from robot.errors import DataError
from robot.utils import get_error_message
from robot.variables import VariableMatches

from ..context import EXECUTION_CONTEXTS
from .typeinfo import TypeInfo

VARIABLE_PLACEHOLDER = "robot-834d5d70-239e-43f6-97fb-902acf41625b"


class EmbeddedArguments:

    def __init__(
        self,
        name: re.Pattern,
        args: Sequence[str] = (),
        custom_patterns: "Mapping[str, str]|None" = None,
        types: "Sequence[TypeInfo|None]" = (),
    ):
        self.name = name
        self.args = tuple(args)
        self.custom_patterns = custom_patterns or None
        self.types = types

    @classmethod
    def from_name(cls, name: str) -> "EmbeddedArguments|None":
        return EmbeddedArgumentParser().parse(name) if "${" in name else None

    def match(self, name: str) -> "re.Match|None":
        """Deprecated since Robot Framework 7.3."""
        warnings.warn(
            "'EmbeddedArguments.match()' is deprecated since Robot Framework 7.3. Use "
            "new 'EmbeddedArguments.matches()' or 'EmbeddedArguments.parse_args()' "
            "instead. Alternatively, use 'EmbeddedArguments.name.fullmatch()' to "
            "preserve the old behavior and to be compatible with earlier Robot "
            "Framework versions."
        )
        return self.name.fullmatch(name)

    def matches(self, name: str) -> bool:
        """Return ``True`` if ``name`` matches these embedded arguments."""
        args, _ = self._parse_args(name)
        return bool(args)

    def parse_args(self, name: str) -> "tuple[str, ...]":
        """Parse arguments matching these embedded arguments from ``name``."""
        args, placeholders = self._parse_args(name)
        if not placeholders:
            return args
        return tuple([self._replace_placeholders(a, placeholders) for a in args])

    def _parse_args(self, name: str) -> "tuple[tuple[str, ...], dict[str, str]]":
        parts = []
        placeholders = {}
        for match in VariableMatches(name):
            ph = f"={VARIABLE_PLACEHOLDER}-{len(placeholders) + 1}="
            placeholders[ph] = match.match
            parts[-1:] = [match.before, ph, match.after]
        name = "".join(parts) if parts else name
        match = self.name.fullmatch(name)
        args = match.groups() if match else ()
        return args, placeholders

    def _replace_placeholders(self, arg: str, placeholders: "dict[str, str]") -> str:
        for ph in placeholders:
            if ph in arg:
                arg = arg.replace(ph, placeholders[ph])
        return arg

    def map(self, args: Sequence[object]) -> "list[tuple[str, object]]":
        args = [
            info.convert(value, name) if info else value
            for info, name, value in zip(self.types, self.args, args)
        ]
        self.validate(args)
        return list(zip(self.args, args))

    def validate(self, args: Sequence[object]):
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
                    context.warn(
                        f"Embedded argument '{name}' got value {value!r} "
                        f"that does not match custom pattern {pattern!r}. "
                        f"The argument is still accepted, but this behavior "
                        f"will change in Robot Framework 8.0."
                    )


class EmbeddedArgumentParser:
    _inline_flag = re.compile(r"\(\?[aiLmsux]+(-[imsx]+)?\)")
    _regexp_group_start = re.compile(r"(?<!\\)\((.*?)\)")
    _escaped_curly = re.compile(r"(\\+)([{}])")
    _regexp_group_escape = r"(?:\1)"
    _default_pattern = ".*?"

    def parse(self, string: str) -> "EmbeddedArguments|None":
        name_parts = []
        args = []
        custom_patterns = {}
        after = string = " ".join(string.split())
        types = []
        for match in VariableMatches(string, identifiers="$"):
            arg, typ, pattern = self._parse_arg(match.base)
            args.append(arg)
            types.append(None if typ is None else self._get_type_info(arg, typ))
            if pattern is None:
                pattern = self._default_pattern
            else:
                custom_patterns[arg] = pattern
                pattern = self._format_custom_regexp(pattern)
            name_parts.extend([re.escape(match.before), "(", pattern, ")"])
            after = match.after
        if not args:
            return None
        name_parts.append(re.escape(after))
        name = self._compile_regexp("".join(name_parts))
        return EmbeddedArguments(name, args, custom_patterns, types)

    def _parse_arg(self, arg: str) -> "tuple[str, str|None, str|None]":
        if ":" not in arg:
            return arg, None, None
        match = re.fullmatch("([^:]+): ([^:]+)(:(.*))?", arg)
        if match:
            arg, typ, _, pattern = match.groups()
            return arg, typ, pattern
        arg, pattern = arg.split(":", 1)
        return arg, None, pattern

    def _format_custom_regexp(self, pattern: str) -> str:
        for formatter in (
            self._remove_inline_flags,
            self._make_groups_non_capturing,
            self._unescape_curly_braces,
            self._escape_escapes,
            self._add_variable_placeholder_pattern,
        ):
            pattern = formatter(pattern)
        return pattern

    def _remove_inline_flags(self, pattern: str) -> str:
        # Inline flags are included in custom regexp stored separately, but they
        # must be removed from the full pattern.
        match = self._inline_flag.match(pattern)
        return pattern if match is None else pattern[match.end() :]

    def _make_groups_non_capturing(self, pattern: str) -> str:
        return self._regexp_group_start.sub(self._regexp_group_escape, pattern)

    def _unescape_curly_braces(self, pattern: str) -> str:
        # Users must escape possible lone curly braces in patters (e.g. `${x:\{}`)
        # or otherwise the variable syntax is invalid.
        def unescape(match):
            backslashes = len(match.group(1))
            return "\\" * (backslashes // 2 * 2) + match.group(2)

        return self._escaped_curly.sub(unescape, pattern)

    def _escape_escapes(self, pattern: str) -> str:
        # When keywords are matched, embedded arguments have not yet been
        # resolved which means possible escapes are still doubled. We thus
        # need to double them in the pattern as well.
        return pattern.replace(r"\\", r"\\\\")

    def _add_variable_placeholder_pattern(self, pattern: str) -> str:
        return rf"{pattern}|={VARIABLE_PLACEHOLDER}-\d+="

    def _get_type_info(self, name: str, typ: str) -> "TypeInfo|None":
        var = f"${{{name}: {typ}}}"
        try:
            return TypeInfo.from_variable(var)
        except DataError as err:
            raise DataError(f"Invalid embedded argument '{var}': {err}")

    def _compile_regexp(self, pattern: str) -> re.Pattern:
        try:
            return re.compile(pattern.replace(r"\ ", r"\s"), re.IGNORECASE)
        except Exception:
            raise DataError(
                f"Compiling embedded arguments regexp failed: {get_error_message()}"
            )
