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

from robot.conf import Languages
from robot.utils import normalize_whitespace

from .settings import (InitFileSettings, TestCaseFileSettings, ResourceFileSettings,
                       TestCaseSettings, KeywordSettings)
from .tokens import Token


class LexingContext:
    settings_class = None

    def __init__(self, settings=None, lang=None):
        if not settings:
            self.languages = lang if isinstance(lang, Languages) else Languages(lang)
            self.settings = self.settings_class(self.languages)
        else:
            self.languages = settings.languages
            self.settings = settings

    def lex_setting(self, statement):
        self.settings.lex(statement)


class FileContext(LexingContext):

    def __init__(self, settings=None, lang=None):
        super().__init__(settings, lang)

    def add_language(self, lang):
        self.languages.add_language(lang)

    def keyword_context(self):
        return KeywordContext(settings=KeywordSettings(self.languages))

    def setting_section(self, statement):
        return self._handles_section(statement, 'Settings')

    def variable_section(self, statement):
        return self._handles_section(statement, 'Variables')

    def test_case_section(self, statement):
        return False

    def task_section(self, statement):
        return False

    def keyword_section(self, statement):
        return self._handles_section(statement, 'Keywords')

    def comment_section(self, statement):
        return self._handles_section(statement, 'Comments')

    def lex_invalid_section(self, statement):
        message, fatal = self._get_invalid_section_error(statement[0].value)
        statement[0].set_error(message, fatal)
        for token in statement[1:]:
            token.type = Token.COMMENT

    def _get_invalid_section_error(self, header):
        raise NotImplementedError

    def _handles_section(self, statement, header):
        marker = statement[0].value
        return (marker[:1] == '*' and
                self.languages.headers.get(self._normalize(marker)) == header)

    def _normalize(self, marker):
        return normalize_whitespace(marker).strip('* ').title()


class TestCaseFileContext(FileContext):
    settings_class = TestCaseFileSettings

    def test_case_context(self):
        return TestCaseContext(settings=TestCaseSettings(self.settings, self.languages))

    def test_case_section(self, statement):
        return self._handles_section(statement, 'Test Cases')

    def task_section(self, statement):
        return self._handles_section(statement, 'Tasks')

    def _get_invalid_section_error(self, header):
        return (f"Unrecognized section header '{header}'. Valid sections: "
                f"'Settings', 'Variables', 'Test Cases', 'Tasks', 'Keywords' "
                f"and 'Comments'."), False


class ResourceFileContext(FileContext):
    settings_class = ResourceFileSettings

    def _get_invalid_section_error(self, header):
        name = self._normalize(header)
        if self.languages.headers.get(name) in ('Test Cases', 'Tasks'):
            message = f"Resource file with '{name}' section is invalid."
            fatal = True
        else:
            message = (f"Unrecognized section header '{header}'. Valid sections: "
                       f"'Settings', 'Variables', 'Keywords' and 'Comments'.")
            fatal = False
        return message, fatal


class InitFileContext(FileContext):
    settings_class = InitFileSettings

    def _get_invalid_section_error(self, header):
        name = self._normalize(header)
        if self.languages.headers.get(name) in ('Test Cases', 'Tasks'):
            message = f"'{name}' section is not allowed in suite initialization file."
        else:
            message = (f"Unrecognized section header '{header}'. Valid sections: "
                       f"'Settings', 'Variables', 'Keywords' and 'Comments'.")
        return message, False


class TestCaseContext(LexingContext):

    @property
    def template_set(self):
        return self.settings.template_set


class KeywordContext(LexingContext):

    @property
    def template_set(self):
        return False
