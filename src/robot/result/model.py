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

"""Module implementing result related model objects.

During test execution these objects are created internally by various runners.
At that time they can inspected and modified by listeners__.

When results are parsed from XML output files after execution to be able to
create logs and reports, these objects are created by the
:func:`~.resultbuilder.ExecutionResult` factory method.
At that point they can be inspected and modified by `pre-Rebot modifiers`__.

The :func:`~.resultbuilder.ExecutionResult` factory method can also be used
by custom scripts and tools. In such usage it is often easiest to inspect and
modify these objects using the :mod:`visitor interface <robot.model.visitor>`.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#programmatic-modification-of-results

"""

from itertools import chain
from operator import attrgetter
import warnings

from robot import model
from robot.model import TotalStatisticsBuilder, Messages, Keywords
from robot.utils import get_elapsed_time, setter

from .configurer import SuiteConfigurer
from .messagefilter import MessageFilter
from .keywordremover import KeywordRemover
from .suiteteardownfailed import (SuiteTeardownFailureHandler,
                                  SuiteTeardownFailed)


# TODO: Should remove model.Message altogether and just implement the whole
# thing here. Additionally model.Keyword should not have `message_class` at
# all or it should be None.

class Message(model.Message):
    """Represents a single log message.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = []


class Keyword(model.Keyword):
    """Represents results of a single keyword.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['kwname', 'libname', 'status', 'starttime', 'endtime', 'message',
                 'lineno', 'source']
    keyword_class = None        #: Internal usage only.
    message_class = Message     #: Internal usage only.

    def __init__(self, kwname='', libname='', doc='', args=(), assign=(), tags=(),
                 timeout=None, type='kw', status='FAIL', starttime=None, endtime=None,
                 parent=None, lineno=None, source=None):
        model.Keyword.__init__(self, '', doc, args, assign, tags, timeout, type, parent)
        self.messages = None
        self.keywords = None
        #: Name of the keyword without library or resource name.
        self.kwname = kwname or ''
        #: Name of the library or resource containing this keyword.
        self.libname = libname or ''
        #: Execution status as a string. Typically ``PASS``, ``FAIL`` or ``SKIP``,
        #: but library keywords have status ``NOT_RUN`` in the dry-ryn mode.
        self.status = status
        #: Keyword execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.starttime = starttime
        #: Keyword execution end time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime
        #: Keyword status message. Used only if suite teardowns fails.
        self.message = ''
        self.lineno = lineno
        self.source = source

    @setter
    def keywords(self, keywords):
        """Child keywords as a :class:`~.Keywords` object."""
        return Keywords(self.keyword_class or self.__class__, self, keywords)

    @setter
    def messages(self, messages):
        """Messages as a :class:`~.model.message.Messages` object."""
        return Messages(self.message_class, self, messages)

    @property
    def children(self):
        """Child :attr:`keywords` and :attr:`messages` in creation order."""
        # It would be cleaner to store keywords/messages in same `children`
        # list and turn `keywords` and `messages` to properties that pick items
        # from it. That would require bigger changes to the model, though.
        return sorted(chain(self.keywords, self.messages),
                      key=attrgetter('_sort_key'))

    @property
    def elapsedtime(self):
        """Total execution time in milliseconds."""
        return get_elapsed_time(self.starttime, self.endtime)

    @property
    def name(self):
        """Keyword name in format ``libname.kwname``.

        Just ``kwname`` if :attr:`libname` is empty. In practice that is the
        case only with user keywords in the same file as the executed test case
        or test suite.

        Cannot be set directly. Set :attr:`libname` and :attr:`kwname`
        separately instead.
        """
        if not self.libname:
            return self.kwname
        return '%s.%s' % (self.libname, self.kwname)

    @property
    def passed(self):
        """``True`` when :attr:`status` is 'PASS', ``False`` otherwise."""
        return self.status == 'PASS'

    @passed.setter
    def passed(self, passed):
        self.status = 'PASS' if passed else 'FAIL'

    @property
    def failed(self):
        """``True`` when :attr:`status` is 'FAIL', ``False`` otherwise."""
        return self.status == 'FAIL'

    @failed.setter
    def failed(self, failed):
        self.status = 'FAIL' if failed else 'PASS'

    @property
    def skipped(self):
        """``True`` when :attr:`status` is 'SKIP', ``False`` otherwise.

        Setting to ``False`` value is ambiguous and raises an exception.
        """
        return self.status == 'SKIP'

    @skipped.setter
    def skipped(self, skipped):
        if not skipped:
            raise ValueError("`skipped` value must be truthy, got '%s'."
                             % skipped)
        self.status = 'SKIP'


class TestCase(model.TestCase):
    """Represents results of a single test case.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['status', 'message', 'starttime', 'endtime']
    keyword_class = Keyword

    def __init__(self, name='', doc='', tags=None, timeout=None, status='FAIL',
                 message='', starttime=None, endtime=None):
        model.TestCase.__init__(self, name, doc, tags, timeout)
        #: Status as a string ``PASS`` or ``FAIL``. See also :attr:`passed`.
        self.status = status
        #: Test message. Typically a failure message but can be set also when
        #: test passes.
        self.message = message
        #: Test case execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.starttime = starttime
        #: Test case execution end time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime

    @property
    def elapsedtime(self):
        """Total execution time in milliseconds."""
        return get_elapsed_time(self.starttime, self.endtime)

    @property
    def passed(self):
        """``True`` when :attr:`status` is 'PASS', ``False`` otherwise."""
        return self.status == 'PASS'

    @passed.setter
    def passed(self, passed):
        self.status = 'PASS' if passed else 'FAIL'

    @property
    def failed(self):
        """``True`` when :attr:`status` is 'FAIL', ``False`` otherwise."""
        return self.status == 'FAIL'

    @failed.setter
    def failed(self, failed):
        self.status = 'FAIL' if failed else 'PASS'

    @property
    def skipped(self):
        """``True`` when :attr:`status` is 'SKIP', ``False`` otherwise.

        Setting to ``False`` value is ambiguous and raises an exception.
        """
        return self.status == 'SKIP'

    @skipped.setter
    def skipped(self, skipped):
        if not skipped:
            raise ValueError("`skipped` value must be truthy, got '%s'."
                             % skipped)
        self.status = 'SKIP'

    @property
    def critical(self):
        warnings.warn("'TestCase.criticality' has been deprecated and always "
                      " returns 'True'.",
                      UserWarning)
        return True


class TestSuite(model.TestSuite):
    """Represents results of a single test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['message', 'starttime', 'endtime']
    test_class = TestCase
    keyword_class = Keyword

    def __init__(self, name='', doc='', metadata=None, source=None,
                 message='', starttime=None, endtime=None, rpa=False):
        model.TestSuite.__init__(self, name, doc, metadata, source, rpa)
        #: Possible suite setup or teardown error message.
        self.message = message
        #: Suite execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.starttime = starttime
        #: Suite execution end time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime

    @property
    def passed(self):
        """``True`` if no test has failed but some have passed, ``False`` otherwise."""
        return self.status == 'PASS'

    @property
    def failed(self):
        """``True`` if any test has failed, ``False`` otherwise."""
        return self.status == 'FAIL'

    @property
    def skipped(self):
        """``True`` if there are no passed or failed tests, ``False`` otherwise."""
        return self.status == 'SKIP'

    @property
    def status(self):
        """'PASS', 'FAIL' or 'SKIP' depending on test statuses.

        - If any test has failed, status is 'FAIL'.
        - If no test has failed but at least some test has passed, status is 'PASS'.
        - If there are no failed or passed tests, status is 'SKIP'. This covers both
          the case when all tests have been skipped and when there are no tests.
        """
        stats = self.statistics  # Local variable avoids recreating stats.
        if stats.failed:
            return 'FAIL'
        if stats.passed:
            return 'PASS'
        return 'SKIP'

    @property
    def statistics(self):
        """Suite statistics as a :class:`~robot.model.totalstatistics.TotalStatistics` object.

        Recreated every time this property is accessed, so saving the results
        to a variable and inspecting it is often a good idea::

            stats = suite.statistics
            print(stats.failed)
            print(stats.total)
            print(stats.message)
        """
        return TotalStatisticsBuilder(self, self.rpa).stats

    @property
    def full_message(self):
        """Combination of :attr:`message` and :attr:`stat_message`."""
        if not self.message:
            return self.stat_message
        return '%s\n\n%s' % (self.message, self.stat_message)

    @property
    def stat_message(self):
        """String representation of the :attr:`statistics`."""
        return self.statistics.message

    @property
    def elapsedtime(self):
        """Total execution time in milliseconds."""
        if self.starttime and self.endtime:
            return get_elapsed_time(self.starttime, self.endtime)
        return sum(child.elapsedtime for child in
                   chain(self.suites, self.tests, (self.setup, self.teardown)))

    def remove_keywords(self, how):
        """Remove keywords based on the given condition.

        :param how: What approach to use when removing keywords. Either
            ``ALL``, ``PASSED``, ``FOR``, ``WUKS``, or ``NAME:<pattern>``.

        For more information about the possible values see the documentation
        of the ``--removekeywords`` command line option.
        """
        self.visit(KeywordRemover(how))

    def filter_messages(self, log_level='TRACE'):
        """Remove log messages below the specified ``log_level``."""
        self.visit(MessageFilter(log_level))

    def clear(self):
        """Remove subsuites, tests, setup and teardown from this suite."""
        self.suites.clear()
        self.tests.clear()
        self.setup = None
        self.teardown = None

    def configure(self, **options):
        """A shortcut to configure a suite using one method call.

        Can only be used with the root test suite.

        :param options: Passed to
            :class:`~robot.result.configurer.SuiteConfigurer` that will then
            set suite attributes, call :meth:`filter`, etc. as needed.

        Example::

            suite.configure(remove_keywords='PASSED',
                            doc='Smoke test results.')
        """
        model.TestSuite.configure(self)    # Parent validates call is allowed.
        self.visit(SuiteConfigurer(**options))

    def handle_suite_teardown_failures(self):
        """Internal usage only."""
        self.visit(SuiteTeardownFailureHandler())

    def suite_teardown_failed(self, error):
        """Internal usage only."""
        self.visit(SuiteTeardownFailed(error))

    def suite_teardown_skipped(self, message):
        """Internal usage only."""
        self.visit(SuiteTeardownFailed(message, skipped=True))
