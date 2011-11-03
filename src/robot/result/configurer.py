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
                 include_tests=None, remove_keywords=None, log_level=None,
                 critical=None, noncritical=None):
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.set_tags = set_tags or []
        self.critical_tags = critical
        self.non_critical_tags = noncritical
        self.include_tags = include_tags
        self.exclude_tags = exclude_tags
        self.include_suites = include_suites
        self.include_tests = include_tests
        self.remove_keywords = remove_keywords
        self.log_level = log_level

    @property
    def add_tags(self):
        return [t for t in self.set_tags if not t.startswith('-')]

    @property
    def remove_tags(self):
        return [t[1:] for t in self.set_tags if t.startswith('-')]

    def configure(self, suite):
        self._set_suite_attributes(suite)
        suite.filter(self.include_suites, self.include_tests,
                     self.include_tags, self.exclude_tags)
        suite.set_tags(self.add_tags, self.remove_tags)
        suite.remove_keywords(self.remove_keywords)
        suite.filter_messages(self.log_level)
        suite.set_criticality(self.critical_tags, self.non_critical_tags)

    def _set_suite_attributes(self, suite):
        if self.name:
            suite.name = self.name
        if self.doc:
            suite.doc = self.doc
        if self.metadata:
            suite.metadata.update(self.metadata)

