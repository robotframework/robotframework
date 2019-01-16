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

from .settings import (KeywordSettings, TestCaseFileSettings,
                       TestCaseSettings, ResourceFileSettings)


class LexingContext(object):

    def __init__(self, settings):
        self.settings = settings

    def lex_setting(self, statement):
        self.settings.lex(statement)

    def keyword_context(self):
        return KeywordContext(KeywordSettings())


class TestCaseFileContext(LexingContext):

    def __init__(self):
        LexingContext.__init__(self, TestCaseFileSettings())

    def test_case_context(self):
        return TestCaseContext(TestCaseSettings(self.settings))


class ResourceFileContext(LexingContext):

    def __init__(self):
        LexingContext.__init__(self, ResourceFileSettings())

    def test_case_context(self):
        # Lex test cases for resource/init files.
        # The error will be reported when the model is built
        return KeywordContext(TestCaseSettings(self.settings))


class TestCaseContext(LexingContext):

    @property
    def template_set(self):
        return self.settings.template_set


class KeywordContext(LexingContext):

    @property
    def template_set(self):
        return False
