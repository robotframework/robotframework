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

from collections.abc import Iterator

from robot.utils import plural_or_not, test_or_task

from .stats import TotalStat
from .visitor import SuiteVisitor


class TotalStatistics:
    """Container for total statistics."""

    def __init__(self, rpa: bool = False):
        #: Instance of :class:`~robot.model.stats.TotalStat` for all the tests.
        self.stat = TotalStat(test_or_task('All {Test}s', rpa))
        self._rpa = rpa

    def visit(self, visitor):
        visitor.visit_total_statistics(self.stat)

    def __iter__(self) -> 'Iterator[TotalStat]':
        yield self.stat

    @property
    def total(self) -> int:
        return self.stat.total

    @property
    def passed(self) -> int:
        return self.stat.passed

    @property
    def skipped(self) -> int:
        return self.stat.skipped

    @property
    def failed(self) -> int:
        return self.stat.failed

    def add_test(self, test):
        self.stat.add_test(test)

    @property
    def message(self) -> str:
        """String representation of the statistics.

        For example::
            2 tests, 1 passed, 1 failed
        """
        kind = test_or_task('test', self._rpa) + plural_or_not(self.total)
        msg = f'{self.total} {kind}, {self.passed} passed, {self.failed} failed'
        if self.skipped:
            msg += f', {self.skipped} skipped'
        return msg


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
