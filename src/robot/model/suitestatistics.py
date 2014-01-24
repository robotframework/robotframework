#  Copyright 2008-2014 Nokia Solutions and Networks
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

from .stats import SuiteStat


class SuiteStatistics(object):
    """Container for suite statistics."""

    def __init__(self, suite):
        #: Instance of :class:`~robot.model.stats.SuiteStat`.
        self.stat = SuiteStat(suite)
        #: List of :class:`~robot.model.testsuite.TestSuite` objects.
        self.suites = []

    def visit(self, visitor):
        visitor.visit_suite_statistics(self)

    def __iter__(self):
        yield self.stat
        for child in self.suites:
            for stat in child:
                yield stat


class SuiteStatisticsBuilder(object):

    def __init__(self, suite_stat_level):
        self._suite_stat_level = suite_stat_level
        self._stats_stack = []
        self.stats = None

    @property
    def current(self):
        return self._stats_stack[-1] if self._stats_stack else None

    def start_suite(self, suite):
        self._stats_stack.append(SuiteStatistics(suite))
        if self.stats is None:
            self.stats = self.current

    def add_test(self, test):
        self.current.stat.add_test(test)

    def end_suite(self):
        stats = self._stats_stack.pop()
        if self.current:
            self.current.stat.add_stat(stats.stat)
            if self._is_child_included():
                self.current.suites.append(stats)

    def _is_child_included(self):
        return self._include_all_levels() or self._below_threshold()

    def _include_all_levels(self):
        return self._suite_stat_level == -1

    def _below_threshold(self):
        return len(self._stats_stack) < self._suite_stat_level
