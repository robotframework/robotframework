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

from abc import ABC, abstractmethod

from robot.conf import Languages
from robot.utils import normalize, normalize_whitespace, RecommendationFinder

from .tokens import StatementTokens, Token


class Settings(ABC):
    names: 'tuple[str, ...]' = ()
    aliases: 'dict[str, str]' = {}
    multi_use = (
        'Metadata',
        'Library',
        'Resource',
        'Variables'
    )
    single_value = (
        'Resource',
        'Test Timeout',
        'Test Template',
        'Timeout',
        'Template',
        'Name'
    )
    name_and_arguments = (
        'Metadata',
        'Suite Setup',
        'Suite Teardown',
        'Test Setup',
        'Test Teardown',
        'Test Template',
        'Setup',
        'Teardown',
        'Template',
        'Resource',
        'Variables'
    )
    name_arguments_and_with_name = (
        'Library',
    )

    def __init__(self, languages: Languages):
        self.settings: 'dict[str, list[Token]|None]' = {n: None for n in self.names}
        self.languages = languages

    def lex(self, statement: StatementTokens):
        orig = self._format_name(statement[0].value)
        name = normalize_whitespace(orig).title()
        name = self.languages.settings.get(name, name)
        if name in self.aliases:
            name = self.aliases[name]
        try:
            self._validate(orig, name, statement)
        except ValueError as err:
            self._lex_error(statement, err.args[0])
        else:
            self._lex_setting(statement, name)

    def _format_name(self, name: str) -> str:
        return name

    def _validate(self, orig: str, name: str, statement: StatementTokens):
        if name not in self.settings:
            message = self._get_non_existing_setting_message(orig, name)
            raise ValueError(message)
        if self.settings[name] is not None and name not in self.multi_use:
            raise ValueError(f"Setting '{orig}' is allowed only once. "
                             f"Only the first value is used.")
        if name in self.single_value and len(statement) > 2:
            raise ValueError(f"Setting '{orig}' accepts only one value, "
                             f"got {len(statement)-1}.")

    def _get_non_existing_setting_message(self, name: str, normalized: str) -> str:
        if self._is_valid_somewhere(normalized, Settings.__subclasses__()):
            return self._not_valid_here(name)
        return RecommendationFinder(normalize).find_and_format(
            name=normalized,
            candidates=tuple(self.settings) + tuple(self.aliases),
            message=f"Non-existing setting '{name}'."
        )

    def _is_valid_somewhere(self, name: str, classes: 'list[type[Settings]]') -> bool:
        for cls in classes:
            if (name in cls.names or name in cls.aliases
                    or self._is_valid_somewhere(name, cls.__subclasses__())):
                return True
        return False

    @abstractmethod
    def _not_valid_here(self, name: str) -> str:
        raise NotImplementedError

    def _lex_error(self, statement: StatementTokens, error: str):
        statement[0].set_error(error)
        for token in statement[1:]:
            token.type = Token.COMMENT

    def _lex_setting(self, statement: StatementTokens, name: str):
        statement[0].type = {'Test Tags': Token.TEST_TAGS,
                             'Name': Token.SUITE_NAME}.get(name, name.upper())
        self.settings[name] = values = statement[1:]
        if name in self.name_and_arguments:
            self._lex_name_and_arguments(values)
        elif name in self.name_arguments_and_with_name:
            self._lex_name_arguments_and_with_name(values)
        else:
            self._lex_arguments(values)
        if name == 'Return':
            statement[0].error = ("The '[Return]' setting is deprecated. "
                                  "Use the 'RETURN' statement instead.")

    def _lex_name_and_arguments(self, tokens: StatementTokens):
        if tokens:
            tokens[0].type = Token.NAME
            self._lex_arguments(tokens[1:])

    def _lex_name_arguments_and_with_name(self, tokens: StatementTokens):
        self._lex_name_and_arguments(tokens)
        if len(tokens) > 1 and \
                normalize_whitespace(tokens[-2].value) in ('WITH NAME', 'AS'):
            tokens[-2].type = Token.AS
            tokens[-1].type = Token.NAME

    def _lex_arguments(self, tokens: StatementTokens):
        for token in tokens:
            token.type = Token.ARGUMENT


class FileSettings(Settings, ABC):
    pass


class SuiteFileSettings(FileSettings):
    names = (
        'Documentation',
        'Metadata',
        'Name',
        'Suite Setup',
        'Suite Teardown',
        'Test Setup',
        'Test Teardown',
        'Test Template',
        'Test Timeout',
        'Test Tags',
        'Default Tags',
        'Keyword Tags',
        'Library',
        'Resource',
        'Variables'
    )
    aliases = {
        'Force Tags': 'Test Tags',
        'Task Tags': 'Test Tags',
        'Task Setup': 'Test Setup',
        'Task Teardown': 'Test Teardown',
        'Task Template': 'Test Template',
        'Task Timeout': 'Test Timeout',
    }

    def _not_valid_here(self, name: str) -> str:
        return f"Setting '{name}' is not allowed in suite file."


class InitFileSettings(FileSettings):
    names = (
        'Documentation',
        'Metadata',
        'Name',
        'Suite Setup',
        'Suite Teardown',
        'Test Setup',
        'Test Teardown',
        'Test Timeout',
        'Test Tags',
        'Keyword Tags',
        'Library',
        'Resource',
        'Variables'
    )
    aliases = {
        'Force Tags': 'Test Tags',
        'Task Tags': 'Test Tags',
        'Task Setup': 'Test Setup',
        'Task Teardown': 'Test Teardown',
        'Task Timeout': 'Test Timeout',
    }

    def _not_valid_here(self, name: str) -> str:
        return f"Setting '{name}' is not allowed in suite initialization file."


class ResourceFileSettings(FileSettings):
    names = (
        'Documentation',
        'Keyword Tags',
        'Library',
        'Resource',
        'Variables'
    )

    def _not_valid_here(self, name: str) -> str:
        return f"Setting '{name}' is not allowed in resource file."


class TestCaseSettings(Settings):
    names = (
        'Documentation',
        'Tags',
        'Setup',
        'Teardown',
        'Template',
        'Timeout'
    )

    def __init__(self, parent: SuiteFileSettings):
        super().__init__(parent.languages)
        self.parent = parent

    def _format_name(self, name: str) -> str:
        return name[1:-1].strip()

    @property
    def template_set(self) -> bool:
        template = self.settings['Template']
        if self._has_disabling_value(template):
            return False
        parent_template = self.parent.settings['Test Template']
        return self._has_value(template) or self._has_value(parent_template)

    def _has_disabling_value(self, setting: 'StatementTokens|None') -> bool:
        if setting is None:
            return False
        return setting == [] or setting[0].value.upper() == 'NONE'

    def _has_value(self, setting: 'StatementTokens|None') -> bool:
        return bool(setting and setting[0].value)

    def _not_valid_here(self, name: str) -> str:
        return f"Setting '{name}' is not allowed with tests or tasks."


class KeywordSettings(Settings):
    names = (
        'Documentation',
        'Arguments',
        'Setup',
        'Teardown',
        'Timeout',
        'Tags',
        'Return'
    )

    def __init__(self, parent: FileSettings):
        super().__init__(parent.languages)
        self.parent = parent

    def _format_name(self, name: str) -> str:
        return name[1:-1].strip()

    def _not_valid_here(self, name: str) -> str:
        return f"Setting '{name}' is not allowed with user keywords."
