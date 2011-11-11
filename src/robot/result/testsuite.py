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

from robot.model.statistics import Statistics
from robot import model, utils

from messagefilter import MessageFilter
from keywordremover import KeywordRemover
from testcase import TestCase
from keyword import Keyword


class TestSuite(model.TestSuite):
    __slots__ = ['message', 'starttime', 'endtime']
    test_class = TestCase
    keyword_class = Keyword

    def __init__(self, source='', name='', doc='', metadata=None):
        model.TestSuite.__init__(self, source, name, doc, metadata)
        self.message = ''
        self.starttime = 'N/A'
        self.endtime = 'N/A'

    @property
    def status(self):
        return 'PASS' if not self.critical_stats.failed else 'FAIL'

    @property
    def stat_message(self):
        return self._stat_message()

    @property
    def full_message(self):
        stat_msg = self._stat_message()
        if not self.message:
            return stat_msg
        return '%s\n\n%s' % (self.message, stat_msg)

    def _stat_message(self):
        # TODO: Should create self.statistics and move this there.
        ctotal, cend, cpass, cfail = self._get_counts(self.critical_stats)
        atotal, aend, apass, afail = self._get_counts(self.all_stats)
        return ('%d critical test%s, %d passed, %d failed\n'
                '%d test%s total, %d passed, %d failed'
                % (ctotal, cend, cpass, cfail, atotal, aend, apass, afail))

    def _get_counts(self, stat):
        ending = utils.plural_or_not(stat.total)
        return stat.total, ending, stat.passed, stat.failed

    @property
    def critical_stats(self):
        return Statistics(self).suite.critical

    @property
    def all_stats(self):
        return Statistics(self).suite.all

    @property
    def elapsedtime(self):
        if self.starttime == 'N/A' or self.endtime == 'N/A':
            children = list(self.suites) + list(self.tests) + list(self.keywords)
            return sum(item.elapsedtime for item in children)
        return utils.get_elapsed_time(self.starttime, self.endtime)

    def remove_keywords(self, how):
        self.visit(KeywordRemover(how))

    def filter_messages(self, log_level):
        self.visit(MessageFilter(log_level))
