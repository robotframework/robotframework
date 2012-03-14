#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from itertools import chain

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

    def __init__(self, source='', name='', doc='', metadata=None,
                 message='', starttime=None, endtime=None):
        """Results of a single test suite.

        :ivar parent: Parent :class:`TestSuite` or `None`.
        :ivar source: Path to the source file.
        :ivar name: Test suite name.
        :ivar doc: Test suite documentation.
        :ivar metadata: Test suite metadata as a dictionary.
        :ivar suites: Child suite results.
        :ivar tests: Test case results. a list of :class:`~.testcase.TestCase`
            instances.
        :ivar keywords: A list containing setup and teardown results.
        :ivar message: Possible failure message.
        :ivar starttime: Test suite execution start time as a timestamp.
        :ivar endtime: Test suite execution end time as a timestamp.
        """
        model.TestSuite.__init__(self, source, name, doc, metadata)
        self.message = message
        self.starttime = starttime
        self.endtime = endtime

    @property
    def status(self):
        return 'FAIL' if self.statistics.critical.failed else 'PASS'

    @property
    def statistics(self):
        return TotalStatisticsBuilder(self).stats

    @property
    def full_message(self):
        if not self.message:
            return self.statistics.message
        return '%s\n\n%s' % (self.message, self.statistics.message)

    @property
    def elapsedtime(self):
        if self.starttime and self.endtime:
            return utils.get_elapsed_time(self.starttime, self.endtime)
        return sum(child.elapsedtime for child in
                   chain(self.suites, self.tests, self.keywords))

    def remove_keywords(self, how):
        self.visit(KeywordRemover(how))

    def filter_messages(self, log_level='TRACE'):
        self.visit(MessageFilter(log_level))
