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

    def start_test(self, test):
        test.tags.add(self.add)
        test.tags.remove(self.remove)
        return False

    def start_keyword(self, keyword):
        return False


class Filter(Visitor):

    def __init__(self, include_tags=None, exclude_tags=None,
                 include_tests=None, include_suites=None):
        # TODO: What to do if these are passed as strings? Convert to list? Fail?
        self.include_tags = TagPatterns(include_tags)
        self.exclude_tags = TagPatterns(exclude_tags)
        self.include_tests = include_tests
        self.include_suites = include_suites

    def start_suite(self, suite):
        if self.include_tests:
            suite.tests = list(self._filter(suite, self._test_included_by_name))
        if self.include_tags:
            suite.tests = list(self._filter(suite, self._test_included_by_tags))
        return bool(suite.suites)

    def _filter(self, suite, filter):
        for test in suite.tests:
            if filter(test):
                yield test

    def _test_included_by_name(self, test):
        return any(utils.matches_any(name, self.include_tests, ignore=['_'])
                   for name in (test.name, test.longname))

    def _test_included_by_tags(self, test):
        return self.include_tags.match_any(test.tags)

    def start_test(self, test):
        return False

    def start_keyword(self, keyword):
        return False
