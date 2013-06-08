#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

from robot.model import TotalStatisticsBuilder, Criticality
from robot import model, utils

from .configurer import SuiteConfigurer
from .messagefilter import MessageFilter
from .keywordremover import KeywordRemover
from .keyword import Keyword
from .suiteteardownfailed import (SuiteTeardownFailureHandler,
                                  SuiteTeardownFailed)
from .testcase import TestCase


class TestSuite(model.TestSuite):
    __slots__ = ['message', 'starttime', 'endtime', '_criticality']
    test_class = TestCase
    keyword_class = Keyword

    def __init__(self, name='', doc='', metadata=None, source=None,
                 message='', starttime=None, endtime=None):
        """Result of a single test suite.

        :ivar parent: Parent :class:`TestSuite` or `None`.
        :ivar name: Test suite name.
        :ivar doc: Test suite documentation.
        :ivar metadata: Test suite metadata as a dictionary.
        :ivar source: Path to the source file.
        :ivar suites: A list of child :class:`~.testsuite.TestSuite` instances.
        :ivar tests: A list of :class:`~.testcase.TestCase` instances.
        :ivar keywords: A list containing setup and teardown
            :class:`~.keyword.Keyword` instances.
        :ivar starttime: Test suite execution start time as a timestamp.
        :ivar endtime: Test suite execution end time as a timestamp.
        """
        model.TestSuite.__init__(self, name, doc, metadata, source)
        self.message = message
        self.starttime = starttime
        self.endtime = endtime
        self._criticality = None

    @property
    def passed(self):
        """Returns boolean based on if any critical test cases failed in the
        suite."""
        return not self.statistics.critical.failed

    @property
    def status(self):
        """Returns string `'PASS'` or `'FAIL'` if the test suite failed."""
        return 'PASS' if self.passed else 'FAIL'

    @property
    def statistics(self):
        """Builds a new :class:`~robot.model.totalstatistics.TotalStatistics`
        object based from itself and returns it."""
        return TotalStatisticsBuilder(self).stats

    @property
    def full_message(self):
        """Returns a possible failure message."""
        if not self.message:
            return self.stat_message
        return '%s\n\n%s' % (self.message, self.stat_message)

    @property
    def stat_message(self):
        """Returns a string with passed and failed information of critical as
        well as all test cases."""
        return self.statistics.message

    @property
    def elapsedtime(self):
        """Returns total execution time of the suite in milliseconds."""
        if self.starttime and self.endtime:
            return utils.get_elapsed_time(self.starttime, self.endtime)
        return sum(child.elapsedtime for child in
                   chain(self.suites, self.tests, self.keywords))

    @property
    def criticality(self):
        """Returns if the test suite is critical or not."""
        if self.parent:
            return self.parent.criticality
        if self._criticality is None:
            self.set_criticality()
        return self._criticality

    def set_criticality(self, critical_tags=None, non_critical_tags=None):
        """Set which tags are considered critical for the test suite and which
        are not."""
        if self.parent:
            raise TypeError('Criticality can only be set to top level suite')
        self._criticality = Criticality(critical_tags, non_critical_tags)

    def remove_keywords(self, how):
        """Remove keywords based on
        :func:`given criteria<robot.result.keywordremover.KeywordRemover>`."""
        self.visit(KeywordRemover(how))

    def filter_messages(self, log_level='TRACE'):
        """Visitor to filter :class:`~.keyword.Keyword` messages of a given
        log level.

        :attr log_level: Optional log level. If no log level is given, messages
            are filtered on the `TRACE` log level.
        """
        self.visit(MessageFilter(log_level))

    def configure(self, **options):
        """Configure suite with
        :class:`set of options <.configurer.SuiteConfigurer>`."""
        self.visit(SuiteConfigurer(**options))

    def handle_suite_teardown_failures(self):
        self.visit(SuiteTeardownFailureHandler())

    def suite_teardown_failed(self, message):
        self.visit(SuiteTeardownFailed(message))
