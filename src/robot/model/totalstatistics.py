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

from .stats import TotalStat
from .visitor import SuiteVisitor


class TotalStatistics(object):
    """Container for total statistics."""

    def __init__(self, rpa=False):
        #: Instance of :class:`~robot.model.stats.TotalStat` for critical tests.
        test_or_task = 'Tests' if not rpa else 'Tasks'
        self.critical = TotalStat('Critical ' + test_or_task)
        #: Instance of :class:`~robot.model.stats.TotalStat` for all the tests.
        self.all = TotalStat('All ' + test_or_task)
        self._rpa = rpa

    def visit(self, visitor):
        visitor.visit_total_statistics(self)

    def __iter__(self):
        return iter([self.critical, self.all])

    @property
    def message(self):
        """String representation of the statistics.

        For example::

            2 critical tests, 1 passed, 1 failed
            2 tests total, 1 passed, 1 failed
        """
        test_or_task = 'test' if not self._rpa else 'task'
        ctotal, cend, cpass, cfail = self._get_counts(self.critical)
        atotal, aend, apass, afail = self._get_counts(self.all)
        return ('%d critical %s%s, %d passed, %d failed\n'
                '%d %s%s total, %d passed, %d failed'
                % (ctotal, test_or_task, cend, cpass, cfail,
                   atotal, test_or_task, aend, apass, afail))

    def _get_counts(self, stat):
        ending = 's' if stat.total != 1 else ''
        return stat.total, ending, stat.passed, stat.failed


class TotalStatisticsBuilder(SuiteVisitor):

    def __init__(self, suite=None, rpa=False):
        self.stats = TotalStatistics(rpa)
        if suite:
            suite.visit(self)

    def add_test(self, test):
        self.stats.all.add_test(test)
        if test.critical:
            self.stats.critical.add_test(test)

    def visit_test(self, test):
        self.add_test(test)

    def visit_keyword(self, kw):
        pass
