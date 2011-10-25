#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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


class SuiteConfigurer(object):

    def __init__(self, name=None, doc=None, metadata=None, set_tags=None,
                 include_tags=None, exclude_tags=None, include_suites=None,
                 include_tests=None, remove_keywords=False):
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.set_tags = set_tags
        self.include_tags = include_tags
        self.exclude_tags = exclude_tags
        self.include_suites = include_suites
        self.include_tests = include_tests
        self.remove_keywords = remove_keywords

    def configure(self, suite):
        if self.name:
            suite.name = self.name
        if self.doc:
            suite.doc = self.doc
        if self.metadata:
            suite.metadata.update(self.metadata)
        if self.set_tags:
            self._set_tags(suite)

    def _set_tags(self, suite):
        for test in suite.tests:
            test.tags.add(self.set_tags)
        for sub in suite.suites:
            self._set_tags(sub)
