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

from .suitestatistics import SuiteStatistics, SuiteStatisticsBuilder
from .tagstatistics import TagStatistics, TagStatisticsBuilder
from .totalstatistics import TotalStatistics, TotalStatisticsBuilder
from .visitor import SuiteVisitor


class Statistics:
    """Container for total, suite and tag statistics.

    Accepted parameters have the same semantics as the matching command line
    options.
    """

    def __init__(
        self,
        suite,
        suite_stat_level=-1,
        tag_stat_include=None,
        tag_stat_exclude=None,
        tag_stat_combine=None,
        tag_doc=None,
        tag_stat_link=None,
        rpa=False,
    ):
        total_builder = TotalStatisticsBuilder(rpa=rpa)
        suite_builder = SuiteStatisticsBuilder(suite_stat_level)
        tag_builder = TagStatisticsBuilder(
            tag_stat_include,
            tag_stat_exclude,
            tag_stat_combine,
            tag_doc,
            tag_stat_link,
        )
        suite.visit(StatisticsBuilder(total_builder, suite_builder, tag_builder))
        self.total: TotalStatistics = total_builder.stats
        self.suite: SuiteStatistics = suite_builder.stats
        self.tags: TagStatistics = tag_builder.stats

    def to_dict(self):
        return {
            "total": self.total.stat.get_attributes(include_label=True),
            "suites": [s.get_attributes(include_label=True) for s in self.suite],
            "tags": [t.get_attributes(include_label=True) for t in self.tags],
        }

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
