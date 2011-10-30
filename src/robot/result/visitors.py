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

from tags import TagPatterns


class Visitor(object):

    def start_suite(self, suite):
        pass

    def end_suite(self, suite):
        pass

    # TODO: Should start_test and start_keyword return False by default?
    def start_test(self, test):
        pass

    def end_test(self, test):
        pass

    def start_keyword(self, keyword):
        pass

    def end_keyword(self, keyword):
        pass

    # TODO: Shouldn't we just have message method?
    def log_message(self, msg):
        pass

    # TODO: Stats and errors related methods missing.
    # But do we actually need stat methods?


class TagSetter(Visitor):

    def __init__(self, add=None, remove=None):
        self.add = add
        self.remove = remove

    def start_suite(self, suite):
        return bool(self)

    def start_test(self, test):
        test.tags.add(self.add)
        test.tags.remove(self.remove)
        return False

    def start_keyword(self, keyword):
        return False

    def __nonzero__(self):
        return bool(self.add or self.remove)


class Filter(Visitor):

    def __init__(self, include_suites=None, include_tests=None,
                 include_tags=None, exclude_tags=None):
        self.include_suites = include_suites
        self.include_tests = include_tests
        self.include_tags = include_tags
        self.exclude_tags = exclude_tags

    # TODO:
    # - include_suites and include_tests should be objects

    @utils.setter
    def include_suites(self, suites):
        return suites if not isinstance(suites, basestring) else [suites]

    @utils.setter
    def include_tests(self, tests):
        return tests if not isinstance(tests, basestring) else [tests]

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
        if not self._included_by_suite_name(suite):
            suite.tests = []
            return True
        suite.visit(Filter(include_suites=[],
                           include_tests=self.include_tests,
                           include_tags=self.include_tags,
                           exclude_tags=self.exclude_tags))
        return False

    def _included_by_suite_name(self, suite):
        if self._matches_any(suite.name, self.include_suites):
            return True
        return self._included_by_suite_longname(suite.longname)

    def _matches_any(self, string, patterns):
        return utils.matches_any(string, patterns, ignore=['_'])

    def _included_by_suite_longname(self, name):
        while '.' in name:
            if self._matches_any(name, self.include_suites):
                return True
            name = name.split('.', 1)[1]

    def _filter(self, suite, filter):
        for test in suite.tests:
            if filter(test):
                yield test

    def _included_by_test_name(self, test):
        return any(self._matches_any(name, self.include_tests)
                   for name in (test.name, test.longname))

    def _included_by_tags(self, test):
        return self.include_tags.match(test.tags)

    def _not_excluded_by_tags(self, test):
        return not self.exclude_tags.match(test.tags)

    def end_suite(self, suite):
        suite.suites = [s for s in suite.suites if s.test_count]

    def start_test(self, test):
        return False

    def start_keyword(self, keyword):
        return False

    def __nonzero__(self):
        return bool(self.include_suites or self.include_tests or
                    self.include_tags or self.exclude_tags)
