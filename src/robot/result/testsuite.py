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
    """Result of a single test suite."""
    __slots__ = ['message', 'starttime', 'endtime', '_criticality']
    test_class = TestCase
    keyword_class = Keyword

    def __init__(self, name='', doc='', metadata=None, source=None,
                 message='', starttime=None, endtime=None):
        model.TestSuite.__init__(self, name, doc, metadata, source)
        #: Suite setup/teardown error message.
        self.message = message
        #: Suite execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.starttime = starttime
        #: Suite execution end time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime
        self._criticality = None

    @property
    def passed(self):
        """``True`` if all critical tests succeeded, ``False`` otherwise."""
        return not self.statistics.critical.failed

    @property
    def status(self):
        """``'PASS'`` if all critical tests succeeded, ``'FAIL'`` otherwise."""
        return 'PASS' if self.passed else 'FAIL'

    @property
    def statistics(self):
        """Suite statistics as a :class:`~robot.model.totalstatistics.TotalStatistics` object.

        Recreated every time this property is accessed, so saving the results
        to a variable and inspecting it is often a good idea::

            stats = suite.statistics
            print stats.critical.failed
            print stats.all.total
            print stats.message
        """
        return TotalStatisticsBuilder(self).stats

    @property
    def full_message(self):
        """Combination of :attr:`message` and :attr:`stat_message`."""
        if not self.message:
            return self.stat_message
        return '%s\n\n%s' % (self.message, self.stat_message)

    @property
    def stat_message(self):
        """String representation of the suite's :attr:`statistics`."""
        return self.statistics.message

    @property
    def elapsedtime(self):
        """Total execution time of the suite in milliseconds."""
        if self.starttime and self.endtime:
            return utils.get_elapsed_time(self.starttime, self.endtime)
        return sum(child.elapsedtime for child in
                   chain(self.suites, self.tests, self.keywords))

    @property
    def criticality(self):
        """Used by tests to determine are they considered critical or not.

        Set using :meth:`set_criticality`.
        """
        if self.parent:
            return self.parent.criticality
        if self._criticality is None:
            self.set_criticality()
        return self._criticality

    def set_criticality(self, critical_tags=None, non_critical_tags=None):
        """Sets which tags are considered critical and which non-critical.

        Tags can be given as lists of strings or, when giving only one,
        as single strings. This information is used by tests to determine
        are they considered critical or not.

        Criticality can be set only to the top level test suite.
        """
        if self.parent:
            raise TypeError('Criticality can only be set to top level suite')
        self._criticality = Criticality(critical_tags, non_critical_tags)

    def remove_keywords(self, how):
        """Remove keywords based on the given condition.

        :param how: Is either ``ALL``, ``PASSED``, ``FOR``, ``WUKS``, or
                    ``NAME:<pattern>``.

                    These values have exact same semantics as values accepted by
                    ``--removekeywords`` command line option.
        """
        self.visit(KeywordRemover(how))

    def filter_messages(self, log_level='TRACE'):
        """Remove log messages below the specified ``log_level``."""
        self.visit(MessageFilter(log_level))

    def configure(self, **options):
        """A shortcut to configure a suite using one method call.

        :param options: Passed to
                        :class:`~robot.result.configurer.SuiteConfigurer` that will then call
                        :meth:`filter`, :meth:`remove_keywords`, etc. based on them.

        Example::

            suite.configure(remove_keywords='PASSED',
                            critical_tags='smoke',
                            doc='Smoke test results.')
        """
        self.visit(SuiteConfigurer(**options))

    def handle_suite_teardown_failures(self):
        """Internal usage only."""
        self.visit(SuiteTeardownFailureHandler())

    def suite_teardown_failed(self, message):
        """Internal usage only."""
        self.visit(SuiteTeardownFailed(message))
