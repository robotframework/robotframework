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


class Markers:
    # FIXME: should this be merged with conf.Languages

    def __init__(self, languages):
        if not isinstance(languages, Languages):
            # FIXME: add unit test
            languages = Languages(languages)
        self.setting_headers = set()
        self.variable_headers = set()
        self.test_case_headers = set()
        self.task_headers = set()
        self.keyword_headers = set()
        self.comment_headers = set()
        self.settings = {}
        for lang in languages:
            self.setting_headers |= lang.setting_headers
            self.variable_headers |= lang.variable_headers
            self.test_case_headers |= lang.test_case_headers
            self.task_headers |= lang.task_headers
            self.keyword_headers |= lang.keyword_headers
            self.comment_headers |= lang.comment_headers
            self.settings.update(lang.settings)

    def setting_section(self, marker):
        return marker in self.setting_headers

    def variable_section(self, marker):
        return marker in self.variable_headers

    def test_case_section(self, marker):
        return marker in self.test_case_headers

    def task_section(self, marker):
        return marker in self.task_headers

    def keyword_section(self, marker):
        return marker in self.keyword_headers

    def comment_section(self, marker):
        return marker in self.comment_headers

    def translate(self, value):
        if value in self.settings:
            return self.settings[value]
        return value
