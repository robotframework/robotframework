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

from typing import Sequence, TYPE_CHECKING

from robot.utils import setter

from .tags import TagPatterns
from .namepatterns import SuiteNamePatterns, TestNamePatterns
from .visitor import SuiteVisitor

if TYPE_CHECKING:
    from .keyword import Keyword
    from .testcase import TestCase
    from .testsuite import TestSuite


class EmptySuiteRemover(SuiteVisitor):

    def __init__(self, preserve_direct_children: bool = False):
        self.preserve_direct_children = preserve_direct_children

    def end_suite(self, suite: 'TestSuite'):
        if suite.parent or not self.preserve_direct_children:
            suite.suites = [s for s in suite.suites if s.test_count]

    def visit_test(self, test: 'TestCase'):
        pass

    def visit_keyword(self, keyword: 'Keyword'):
        pass


class Filter(EmptySuiteRemover):

    def __init__(self,
                 include_suites: 'SuiteNamePatterns|Sequence[str]|None' = None,
                 include_tests: 'TestNamePatterns|Sequence[str]|None' = None,
                 include_tags: 'TagPatterns|Sequence[str]|None' = None,
                 exclude_tags: 'TagPatterns|Sequence[str]|None' = None):
        super().__init__()
        self.include_suites = include_suites
        self.include_tests = include_tests
        self.include_tags = include_tags
        self.exclude_tags = exclude_tags

    @setter
    def include_suites(self, suites) -> 'SuiteNamePatterns|None':
        return self._patterns_or_none(suites, SuiteNamePatterns)

    @setter
    def include_tests(self, tests) -> 'TestNamePatterns|None':
        return self._patterns_or_none(tests, TestNamePatterns)

    @setter
    def include_tags(self, tags) -> 'TagPatterns|None':
        return self._patterns_or_none(tags, TagPatterns)

    @setter
    def exclude_tags(self, tags) -> 'TagPatterns|None':
        return self._patterns_or_none(tags, TagPatterns)

    def _patterns_or_none(self, items, pattern_class):
        if items is None or isinstance(items, pattern_class):
            return items
        return pattern_class(items)

    def start_suite(self, suite: 'TestSuite'):
        if not self:
            return False
        if hasattr(suite, 'starttime'):
            suite.starttime = suite.endtime = None
        if self.include_suites is not None:
            if self.include_suites.match(suite.name, suite.longname):
                suite.visit(Filter(include_tests=self.include_tests,
                                   include_tags=self.include_tags,
                                   exclude_tags=self.exclude_tags))
                return False
            suite.tests = []
            return True
        if self.include_tests is not None:
            suite.tests = [t for t in suite.tests
                           if self.include_tests.match(t.name, t.longname)]
        if self.include_tags is not None:
            suite.tests = [t for t in suite.tests
                           if self.include_tags.match(t.tags)]
        if self.exclude_tags is not None:
            suite.tests = [t for t in suite.tests
                           if not self.exclude_tags.match(t.tags)]
        return bool(suite.suites)

    def __bool__(self) -> bool:
        return bool(self.include_suites is not None or
                    self.include_tests is not None or
                    self.include_tags is not None or
                    self.exclude_tags is not None)
