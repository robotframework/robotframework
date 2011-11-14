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

from .tagstatistics import TagStatistics
from .suitestatistics import SuiteStatistics
from .totalstatistics import TotalStatistics
from .visitor import SuiteVisitor


class Statistics(object):

    def __init__(self, suite, suite_stat_level=-1, tag_stat_include=None,
                 tag_stat_exclude=None, tag_stat_combine=None, tag_doc=None,
                 tag_stat_link=None):
        self.tags = TagStatistics(suite.criticality, tag_stat_include,
                                  tag_stat_exclude, tag_stat_combine,
                                  tag_doc, tag_stat_link)
        self.suite = StatisticsBuilder(self.tags, suite_stat_level).build(suite)
        self.total = TotalStatistics(self.suite)

    def visit(self, visitor):
        visitor.visit_statistics(self)


class StatisticsBuilder(SuiteVisitor):

    def __init__(self, tag_stats, suite_stat_level):
        self._tag_stats = tag_stats
        self._parents = []
        self._suite_stat_level = suite_stat_level

    def start_suite(self, suite):
        new  = SuiteStatistics(suite)
        if self._suite_stat_level == -1 or len(self._parents) < self._suite_stat_level:
            self._current_suite_stat.suites.append(new)
        self._parents.append(self._current_suite_stat)
        self._current_suite_stat = new
        self._current_suite = suite

    def build(self, suite):
        self._current_suite_stat = SuiteStatistics(suite)
        self.visit_suite(suite)
        return self._current_suite_stat.suites[0]

    def end_suite(self, suite):
        if self._parents:
            self._parents[-1].all.add_stat(self._current_suite_stat.all)
            self._parents[-1].critical.add_stat(self._current_suite_stat.critical)
            self._current_suite_stat = self._parents.pop(-1)

    def visit_test(self, test):
        self._current_suite_stat.add_test(test)
        self._tag_stats.add_test(test)
