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

from robot.model.stats import SuiteStat


class SuiteStatistics(object):

    def __init__(self, suite):
        self.all = SuiteStat(suite)
        self.critical = SuiteStat(suite)
        self.suites = []

    def add_test(self, test):
        self.all.add_test(test)
        if test.critical == 'yes':
            self.critical.add_test(test)

    def add_child_stats(self, stats, add_to_suites=True):
        self.all.add_stat(stats.all)
        self.critical.add_stat(stats.critical)
        if add_to_suites:
            self.suites.append(stats)

    def visit(self, visitor):
        visitor.visit_suite_statistics(self)

    def __iter__(self):
        yield self.all
        for s in self.suites:
            for stat in s:
                yield stat


class SuiteStatisticsBuilder(object):

    def __init__(self, suite_stat_level):
        self._suite_stat_level = suite_stat_level
        self._stats_stack = []
        self.root = None

    @property
    def current(self):
        return self._stats_stack[-1] if self._stats_stack else None

    def start_suite(self, suite):
        self._stats_stack.append(SuiteStatistics(suite))
        if self.root is None:
            self.root = self.current

    def add_test(self, test):
        self.current.add_test(test)

    def end_suite(self):
        stats = self._stats_stack.pop()
        if self.current:
            self.current.add_child_stats(stats, self._is_child_included())

    def _is_child_included(self):
        return self._include_all_levels() or self._below_threshold()

    def _include_all_levels(self):
        return self._suite_stat_level == -1

    def _below_threshold(self):
        return len(self._stats_stack) < self._suite_stat_level
