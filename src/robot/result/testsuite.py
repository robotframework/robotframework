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

from robot.model import TotalStatisticsBuilder
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
    def statistics(self):
        return TotalStatisticsBuilder(self).stats

    # TODO:
    # 1) Remove critical_stats and all_stats in favor of new self.statistics.xxx
    # 2) Consider removing stat_message in favor of unicode(self.statistics)

    @property
    def stat_message(self):
        return unicode(self.statistics)

    @property
    def full_message(self):
        stat_msg = unicode(self.statistics)
        if not self.message:
            return stat_msg
        return '%s\n\n%s' % (self.message, stat_msg)

    @property
    def critical_stats(self):
        return self.statistics.critical

    @property
    def all_stats(self):
        return self.statistics.all

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
