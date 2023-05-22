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

from robot.conf import Languages, LanguageLike, LanguagesLike
from robot.utils import normalize_whitespace

from .settings import (InitFileSettings, FileSettings, Settings, SuiteFileSettings,
                       ResourceFileSettings, TestCaseSettings, KeywordSettings)
from .tokens import StatementTokens, Token


class LexingContext:

    def __init__(self, settings: Settings, languages: Languages):
        self.settings = settings
        self.languages = languages

    def lex_setting(self, statement: StatementTokens):
        self.settings.lex(statement)


class FileContext(LexingContext):
    settings: FileSettings

    def __init__(self, lang: LanguagesLike = None):
        languages = lang if isinstance(lang, Languages) else Languages(lang)
        settings_class: 'type[FileSettings]' = type(self).__annotations__['settings']
        settings = settings_class(languages)
        super().__init__(settings, languages)

    def add_language(self, lang: LanguageLike):
        self.languages.add_language(lang)

    def keyword_context(self) -> 'KeywordContext':
        return KeywordContext(KeywordSettings(self.settings))

    def setting_section(self, statement: StatementTokens) -> bool:
        return self._handles_section(statement, 'Settings')

    def variable_section(self, statement: StatementTokens) -> bool:
        return self._handles_section(statement, 'Variables')

    def test_case_section(self, statement: StatementTokens) -> bool:
        return False

    def task_section(self, statement: StatementTokens) -> bool:
        return False

    def keyword_section(self, statement: StatementTokens) -> bool:
        return self._handles_section(statement, 'Keywords')

    def comment_section(self, statement: StatementTokens) -> bool:
        return self._handles_section(statement, 'Comments')

    def lex_invalid_section(self, statement: StatementTokens):
        header = statement[0]
        header.type = Token.INVALID_HEADER
        header.error = self._get_invalid_section_error(header.value)
        for token in statement[1:]:
            token.type = Token.COMMENT

    def _get_invalid_section_error(self, header: str) -> str:
        raise NotImplementedError

    def _handles_section(self, statement: StatementTokens, header: str) -> bool:
        marker = statement[0].value
        return bool(marker and marker[0] == '*' and
                    self.languages.headers.get(self._normalize(marker)) == header)

    def _normalize(self, marker: str) -> str:
        return normalize_whitespace(marker).strip('* ').title()


class SuiteFileContext(FileContext):
    settings: SuiteFileSettings

    def test_case_context(self) -> 'TestCaseContext':
        return TestCaseContext(TestCaseSettings(self.settings))

    def test_case_section(self, statement: StatementTokens) -> bool:
        return self._handles_section(statement, 'Test Cases')

    def task_section(self, statement: StatementTokens) -> bool:
        return self._handles_section(statement, 'Tasks')

    def _get_invalid_section_error(self, header: str) -> str:
        return (f"Unrecognized section header '{header}'. Valid sections: "
                f"'Settings', 'Variables', 'Test Cases', 'Tasks', 'Keywords' "
                f"and 'Comments'.")


class ResourceFileContext(FileContext):
    settings: ResourceFileSettings

    def _get_invalid_section_error(self, header: str) -> str:
        name = self._normalize(header)
        if self.languages.headers.get(name) in ('Test Cases', 'Tasks'):
            return f"Resource file with '{name}' section is invalid."
        return (f"Unrecognized section header '{header}'. Valid sections: "
                f"'Settings', 'Variables', 'Keywords' and 'Comments'.")


class InitFileContext(FileContext):
    settings: InitFileSettings

    def _get_invalid_section_error(self, header: str) -> str:
        name = self._normalize(header)
        if self.languages.headers.get(name) in ('Test Cases', 'Tasks'):
            return f"'{name}' section is not allowed in suite initialization file."
        return (f"Unrecognized section header '{header}'. Valid sections: "
                f"'Settings', 'Variables', 'Keywords' and 'Comments'.")


class TestCaseContext(LexingContext):
    settings: TestCaseSettings

    def __init__(self, settings: TestCaseSettings):
        super().__init__(settings, settings.languages)

    @property
    def template_set(self) -> bool:
        return self.settings.template_set


class KeywordContext(LexingContext):
    settings: KeywordSettings

    def __init__(self, settings: KeywordSettings):
        super().__init__(settings, settings.languages)

    @property
    def template_set(self) -> bool:
        return False
