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

from .sections import (InitFileSections, TestCaseFileSections,
                       ResourceFileSections)
from .settings import (InitFileSettings, TestCaseFileSettings,
                       ResourceFileSettings, TestCaseSettings, KeywordSettings)


class LexingContext:
    settings_class = None

    def __init__(self, settings=None):
        self.settings = settings or self.settings_class()

    def lex_setting(self, statement):
        self.settings.lex(statement)


class FileContext(LexingContext):
    sections_class = None

    def __init__(self, settings=None):
        LexingContext.__init__(self, settings)
        self.sections = self.sections_class()

    def setting_section(self, statement):
        return self.sections.setting(statement)

    def variable_section(self, statement):
        return self.sections.variable(statement)

    def test_case_section(self, statement):
        return self.sections.test_case(statement)

    def keyword_section(self, statement):
        return self.sections.keyword(statement)

    def comment_section(self, statement):
        return self.sections.comment(statement)

    def keyword_context(self):
        return KeywordContext(settings=KeywordSettings())

    def lex_invalid_section(self, statement):
        self.sections.lex_invalid(statement)


class TestCaseFileContext(FileContext):
    sections_class = TestCaseFileSections
    settings_class = TestCaseFileSettings

    def test_case_context(self):
        return TestCaseContext(settings=TestCaseSettings(self.settings))


class ResourceFileContext(FileContext):
    sections_class = ResourceFileSections
    settings_class = ResourceFileSettings


class InitFileContext(FileContext):
    sections_class = InitFileSections
    settings_class = InitFileSettings


class TestCaseContext(LexingContext):

    @property
    def template_set(self):
        return self.settings.template_set


class KeywordContext(LexingContext):

    @property
    def template_set(self):
        return False
