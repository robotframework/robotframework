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

from robot.utils import test_or_task

from .stats import TotalStat
from .visitor import SuiteVisitor


class TotalStatistics:
    """Container for total statistics."""

    def __init__(self, rpa=False):
        #: Instance of :class:`~robot.model.stats.TotalStat` for all the tests.
        self._stat = TotalStat(test_or_task('All {Test}s', rpa))
        self._rpa = rpa

    def visit(self, visitor):
        visitor.visit_total_statistics(self._stat)

    def __iter__(self):
        yield self._stat

    @property
    def total(self):
        return self._stat.total

    @property
    def passed(self):
        return self._stat.passed

    @property
    def skipped(self):
        return self._stat.skipped

    @property
    def failed(self):
        return self._stat.failed

    def add_test(self, test):
        self._stat.add_test(test)

    @property
    def message(self):
        """String representation of the statistics.

        For example::
            2 tests, 1 passed, 1 failed
        """
        # TODO: should this message be highlighted in console
        test_or_task = 'test' if not self._rpa else 'task'
        total, end, passed, failed, skipped = self._get_counts()
        template = '%d %s%s, %d passed, %d failed'
        if skipped:
            return ((template + ', %d skipped')
                    % (total, test_or_task, end, passed, failed, skipped))
        return template % (total, test_or_task, end, passed, failed)

    def _get_counts(self):
        ending = 's' if self.total != 1 else ''
        return self.total, ending, self.passed, self.failed, self.skipped


class TotalStatisticsBuilder(SuiteVisitor):

    def __init__(self, suite=None, rpa=False):
        self.stats = TotalStatistics(rpa)
        if suite:
            suite.visit(self)

    def add_test(self, test):
        self.stats.add_test(test)

    def visit_test(self, test):
        self.add_test(test)

    def visit_keyword(self, kw):
        pass
