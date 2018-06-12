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

from robot.model import TotalStatisticsBuilder, Criticality
from robot import model, utils

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
    __slots__ = ['kwname', 'libname', 'status', 'starttime', 'endtime', 'message']
    message_class = Message

    def __init__(self, kwname='', libname='', doc='', args=(), assign=(),
                 tags=(), timeout=None, type='kw',  status='FAIL',
                 starttime=None, endtime=None):
        model.Keyword.__init__(self, '', doc, args, assign, tags, timeout, type)
        #: Name of the keyword without library or resource name.
        self.kwname = kwname or ''
        #: Name of the library or resource containing this keyword.
        self.libname = libname or ''
        #: Execution status as a string. Typically ``PASS`` or ``FAIL``, but
        #: library keywords have status ``NOT_RUN`` in the dry-ryn mode.
        #: See also :attr:`passed`.
        self.status = status
        #: Keyword execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.starttime = starttime
        #: Keyword execution end time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime
        #: Keyword status message. Used only if suite teardowns fails.
        self.message = ''

    @property
    def elapsedtime(self):
        """Total execution time in milliseconds."""
        return utils.get_elapsed_time(self.starttime, self.endtime)

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
        """``True`` or ``False`` depending on the :attr:`status`."""
        return self.status == 'PASS'

    @passed.setter
    def passed(self, passed):
        self.status = 'PASS' if passed else 'FAIL'


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
        return utils.get_elapsed_time(self.starttime, self.endtime)

    @property
    def passed(self):
        """``True/False`` depending on the :attr:`status`."""
        return self.status == 'PASS'

    @passed.setter
    def passed(self, passed):
        self.status = 'PASS' if passed else 'FAIL'

    @property
    def critical(self):
        """``True/False`` depending on is the test considered critical.

        Criticality is determined based on test's :attr:`tags` and
        :attr:`~TestSuite.criticality` of the :attr:`parent` suite.
        """
        if not self.parent:
            return True
        return self.parent.criticality.test_is_critical(self)


class TestSuite(model.TestSuite):
    """Represents results of a single test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['message', 'starttime', 'endtime', '_criticality']
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
        self._criticality = None

    @property
    def passed(self):
        """``True`` if no critical test has failed, ``False`` otherwise."""
        return not self.statistics.critical.failed

    @property
    def status(self):
        """``'PASS'`` if no critical test has failed, ``'FAIL'`` otherwise."""
        return 'PASS' if self.passed else 'FAIL'

    @property
    def statistics(self):
        """Suite statistics as a :class:`~robot.model.totalstatistics.TotalStatistics` object.

        Recreated every time this property is accessed, so saving the results
        to a variable and inspecting it is often a good idea::

            stats = suite.statistics
            print(stats.critical.failed)
            print(stats.all.total)
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
            return utils.get_elapsed_time(self.starttime, self.endtime)
        return sum(child.elapsedtime for child in
                   chain(self.suites, self.tests, self.keywords))

    @property
    def criticality(self):
        """Used by tests to determine are they considered critical or not.

        Normally configured using ``--critical`` and ``--noncritical``
        command line options. Can be set programmatically using
        :meth:`set_criticality` of the root test suite.
        """
        if self.parent:
            return self.parent.criticality
        if self._criticality is None:
            self.set_criticality()
        return self._criticality

    def set_criticality(self, critical_tags=None, non_critical_tags=None):
        """Sets which tags are considered critical and which non-critical.

        :param critical_tags: Tags or patterns considered critical. See
            the documentation of the ``--critical`` option for more details.
        :param non_critical_tags: Tags or patterns considered non-critical. See
            the documentation of the ``--noncritical`` option for more details.

        Tags can be given as lists of strings or, when giving only one,
        as single strings. This information is used by tests to determine
        are they considered critical or not.

        Criticality can be set only to the root test suite.
        """
        if self.parent is not None:
            raise ValueError('Criticality can only be set to the root suite.')
        self._criticality = Criticality(critical_tags, non_critical_tags)

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

    def configure(self, **options):
        """A shortcut to configure a suite using one method call.

        Can only be used with the root test suite.

        :param options: Passed to
            :class:`~robot.result.configurer.SuiteConfigurer` that will then
            set suite attributes, call :meth:`filter`, etc. as needed.

        Example::

            suite.configure(remove_keywords='PASSED',
                            critical_tags='smoke',
                            doc='Smoke test results.')
        """
        model.TestSuite.configure(self)    # Parent validates call is allowed.
        self.visit(SuiteConfigurer(**options))

    def handle_suite_teardown_failures(self):
        """Internal usage only."""
        self.visit(SuiteTeardownFailureHandler())

    def suite_teardown_failed(self, message):
        """Internal usage only."""
        self.visit(SuiteTeardownFailed(message))
