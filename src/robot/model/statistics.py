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

from .totalstatistics import TotalStatisticsBuilder
from .suitestatistics import SuiteStatisticsBuilder
from .tagstatistics import TagStatisticsBuilder
from .visitor import SuiteVisitor


class Statistics(object):
    """Container for total, suite and tag statistics.

    Accepted parameters have the same semantics as the matching command line
    options.
    """
    def __init__(self, suite, suite_stat_level=-1, tag_stat_include=None,
                 tag_stat_exclude=None, tag_stat_combine=None, tag_doc=None,
                 tag_stat_link=None):
        total_builder = TotalStatisticsBuilder()
        suite_builder = SuiteStatisticsBuilder(suite_stat_level)
        tag_builder = TagStatisticsBuilder(suite.criticality, tag_stat_include,
                                           tag_stat_exclude, tag_stat_combine,
                                           tag_doc, tag_stat_link)
        suite.visit(StatisticsBuilder(total_builder, suite_builder, tag_builder))
        #: Instance of :class:`~robot.model.totalstatistics.TotalStatistics`.
        self.total = total_builder.stats
        #: Instance of :class:`~robot.model.suitestatistics.SuiteStatistics`.
        self.suite = suite_builder.stats
        #: Instance of :class:`~robot.model.tagstatistics.TagStatistics`.
        self.tags = tag_builder.stats

    def visit(self, visitor):
        visitor.visit_statistics(self)


class StatisticsBuilder(SuiteVisitor):

    def __init__(self, total_builder, suite_builder, tag_builder):
        self._total_builder = total_builder
        self._suite_builder = suite_builder
        self._tag_builder = tag_builder

    def start_suite(self, suite):
        self._suite_builder.start_suite(suite)

    def end_suite(self, suite):
        self._suite_builder.end_suite()

    def visit_test(self, test):
        self._total_builder.add_test(test)
        self._suite_builder.add_test(test)
        self._tag_builder.add_test(test)

    def visit_keyword(self, kw):
        pass
