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

from robot import utils
from robot.errors import DataError

from .visitor import SuiteVisitor


class SuiteConfigurer(SuiteVisitor):

    def __init__(self, name=None, doc=None, metadata=None, set_tags=None,
                 include_tags=None, exclude_tags=None, include_suites=None,
                 include_tests=None, empty_suite_ok=False):
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.set_tags = set_tags or []
        self.include_tags = include_tags
        self.exclude_tags = exclude_tags
        self.include_suites = include_suites
        self.include_tests = include_tests
        self.empty_suite_ok = empty_suite_ok

    @property
    def add_tags(self):
        return [t for t in self.set_tags if not t.startswith('-')]

    @property
    def remove_tags(self):
        return [t[1:] for t in self.set_tags if t.startswith('-')]

    def visit_suite(self, suite):
        self._set_suite_attributes(suite)
        self._filter(suite)
        suite.set_tags(self.add_tags, self.remove_tags)

    def _set_suite_attributes(self, suite):
        if self.name:
            suite.name = self.name
        if self.doc:
            suite.doc = self.doc
        if self.metadata:
            suite.metadata.update(self.metadata)

    def _filter(self, suite):
        name = suite.name
        suite.filter(self.include_suites, self.include_tests,
                     self.include_tags, self.exclude_tags)
        if not (suite.test_count or self.empty_suite_ok):
            self._raise_no_tests_error(name)

    def _raise_no_tests_error(self, suite):
        selectors = '%s %s' % (self._get_test_selector_msgs(),
                               self._get_suite_selector_msg())
        msg = "Suite '%s' contains no tests %s" % (suite, selectors.strip())
        raise DataError(msg.strip() + '.')

    def _get_test_selector_msgs(self):
        parts = []
        for explanation, selector in [('with tags', self.include_tags),
                                      ('without tags', self.exclude_tags),
                                      ('named', self.include_tests)]:
            if selector:
                parts.append(self._format_selector_msg(explanation, selector))
        return utils.seq2str(parts, quote='')

    def _format_selector_msg(self, explanation, selector):
        if len(selector) == 1 and explanation[-1] == 's':
            explanation = explanation[:-1]
        return '%s %s' % (explanation, utils.seq2str(selector, lastsep=' or '))

    def _get_suite_selector_msg(self):
        if not self.include_suites:
            return ''
        return self._format_selector_msg('in suites', self.include_suites)
