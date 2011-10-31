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

from robot import utils

from visitor import Visitor
from tags import TagPatterns


class Filter(Visitor):

    def __init__(self, include_suites=None, include_tests=None,
                 include_tags=None, exclude_tags=None):
        self.include_suites = include_suites
        self.include_tests = include_tests
        self.include_tags = include_tags
        self.exclude_tags = exclude_tags

    @utils.setter
    def include_suites(self, suites):
        return _SuiteNameFilter(suites) \
            if not isinstance(suites, _SuiteNameFilter) else suites

    @utils.setter
    def include_tests(self, tests):
        return _TestNameFilter(tests) \
            if not isinstance(tests, _TestNameFilter) else tests

    @utils.setter
    def include_tags(self, tags):
        return TagPatterns(tags) if not isinstance(tags, TagPatterns) else tags

    @utils.setter
    def exclude_tags(self, tags):
        return TagPatterns(tags) if not isinstance(tags, TagPatterns) else tags

    def start_suite(self, suite):
        if not self:
            return False
        if self.include_suites:
            return self._filter_by_suite_name(suite)
        if self.include_tests:
            suite.tests = list(self._filter(suite, self._included_by_test_name))
        if self.include_tags:
            suite.tests = list(self._filter(suite, self._included_by_tags))
        if self.exclude_tags:
            suite.tests = list(self._filter(suite, self._not_excluded_by_tags))
        return bool(suite.suites)

    def _filter_by_suite_name(self, suite):
        if self.include_suites.match(suite):
            suite.visit(Filter(include_suites=[],
                               include_tests=self.include_tests,
                               include_tags=self.include_tags,
                               exclude_tags=self.exclude_tags))
            return False
        suite.tests = []
        return True

    def _filter(self, suite, filter):
        for test in suite.tests:
            if filter(test):
                yield test

    def _included_by_test_name(self, test):
        return self.include_tests.match(test)

    def _included_by_tags(self, test):
        return self.include_tags.match(test.tags)

    def _not_excluded_by_tags(self, test):
        return not self.exclude_tags.match(test.tags)

    def end_suite(self, suite):
        suite.suites = [s for s in suite.suites if s.test_count]

    def visit_test(self, test):
        pass

    def visit_keyword(self, keyword):
        pass

    def __nonzero__(self):
        return bool(self.include_suites or self.include_tests or
                    self.include_tags or self.exclude_tags)


class _NameFilter(object):

    def __init__(self, patterns):
        if isinstance(patterns, basestring):
            patterns = [patterns]
        self._patterns = patterns

    def match(self, item):
        return self._match(item.name) or self._match_longname(item.longname)

    def _match(self, name):
        return utils.matches_any(name, self._patterns, ignore=['_'])

    def __nonzero__(self):
        return bool(self._patterns)


class _SuiteNameFilter(_NameFilter):

    def _match_longname(self, name):
        while '.' in name:
            if self._match(name):
                return True
            name = name.split('.', 1)[1]
        return False


class _TestNameFilter(_NameFilter):

    def _match_longname(self, name):
        return self._match(name)
