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

from collections import OrderedDict
from itertools import chain
import warnings

from robot import model
from robot.model import BodyItem, Keywords, TotalStatisticsBuilder
from robot.utils import get_elapsed_time, setter

from .configurer import SuiteConfigurer
from .messagefilter import MessageFilter
from .modeldeprecation import deprecated, DeprecatedAttributesMixin
from .keywordremover import KeywordRemover
from .suiteteardownfailed import SuiteTeardownFailed, SuiteTeardownFailureHandler


class Body(model.Body):
    message_class = None
    __slots__ = []

    def create_message(self, *args, **kwargs):
        return self.append(self.message_class(*args, **kwargs))

    def filter(self, keywords=None, fors=None, ifs=None, messages=None, predicate=None):
        return self._filter([(self.keyword_class, keywords),
                             (self.for_class, fors),
                             (self.if_class, ifs),
                             (self.message_class, messages)], predicate)


class ForIterations(Body):
    for_iteration_class = None
    keyword_class = None
    if_class = None
    for_class = None
    __slots__ = []

    def create_iteration(self, *args, **kwargs):
        return self.append(self.for_iteration_class(*args, **kwargs))


class IfBranches(Body, model.IfBranches):
    __slots__ = []


@Body.register
class Message(model.Message):
    __slots__ = []


class StatusMixin(object):
    __slots__ = []
    PASS = 'PASS'
    FAIL = 'FAIL'
    SKIP = 'SKIP'
    NOT_RUN = 'NOT RUN'
    NOT_SET = 'NOT SET'

    @property
    def elapsedtime(self):
        """Total execution time in milliseconds."""
        return get_elapsed_time(self.starttime, self.endtime)

    @property
    def passed(self):
        """``True`` when :attr:`status` is 'PASS', ``False`` otherwise."""
        return self.status == self.PASS

    @passed.setter
    def passed(self, passed):
        self.status = self.PASS if passed else self.FAIL

    @property
    def failed(self):
        """``True`` when :attr:`status` is 'FAIL', ``False`` otherwise."""
        return self.status == self.FAIL

    @failed.setter
    def failed(self, failed):
        self.status = self.FAIL if failed else self.PASS

    @property
    def skipped(self):
        """``True`` when :attr:`status` is 'SKIP', ``False`` otherwise.

        Setting to ``False`` value is ambiguous and raises an exception.
        """
        return self.status == self.SKIP

    @skipped.setter
    def skipped(self, skipped):
        if not skipped:
            raise ValueError("`skipped` value must be truthy, got '%s'." % skipped)
        self.status = self.SKIP

    @property
    def not_run(self):
        """``True`` when :attr:`status` is 'NOT RUN', ``False`` otherwise.

        Setting to ``False`` value is ambiguous and raises an exception.
        """
        return self.status == self.NOT_RUN

    @not_run.setter
    def not_run(self, not_run):
        if not not_run:
            raise ValueError("`not_run` value must be truthy, got '%s'." % not_run)
        self.status = self.NOT_RUN


@ForIterations.register
class ForIteration(BodyItem, StatusMixin, DeprecatedAttributesMixin):
    type = BodyItem.FOR_ITERATION
    body_class = Body
    repr_args = ('variables',)
    __slots__ = ['variables', 'status', 'starttime', 'endtime', 'doc']

    def __init__(self, variables=None, status='FAIL', starttime=None, endtime=None,
                 doc='', parent=None):
        self.variables = variables or OrderedDict()
        self.parent = parent
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc
        self.body = None

    @setter
    def body(self, body):
        return self.body_class(self, body)

    def visit(self, visitor):
        visitor.visit_for_iteration(self)

    @property
    @deprecated
    def name(self):
        return ', '.join('%s = %s' % item for item in self.variables.items())


@Body.register
class For(model.For, StatusMixin, DeprecatedAttributesMixin):
    body_class = ForIterations
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, variables=(),  flavor='IN', values=(), status='FAIL',
                 starttime=None, endtime=None, doc='', parent=None):
        model.For.__init__(self, variables, flavor, values, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc

    @property
    @deprecated
    def name(self):
        return '%s %s [ %s ]' % (' | '.join(self.variables), self.flavor,
                                 ' | '.join(self.values))


@Body.register
class If(model.If, StatusMixin, DeprecatedAttributesMixin):
    body_class = IfBranches
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, parent=None, status='FAIL', starttime=None, endtime=None, doc=''):
        model.If.__init__(self, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc


@IfBranches.register
class IfBranch(model.IfBranch, StatusMixin, DeprecatedAttributesMixin):
    body_class = Body
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, type=BodyItem.IF, condition=None, status='FAIL',
                 starttime=None, endtime=None, doc='', parent=None):
        model.IfBranch.__init__(self, type, condition, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc

    @property
    @deprecated
    def name(self):
        return self.condition


@Body.register
class Keyword(model.Keyword, StatusMixin):
    """Represents results of a single keyword.

    See the base class for documentation of attributes not documented here.
    """
    body_class = Body
    __slots__ = ['kwname', 'libname', 'status', 'starttime', 'endtime', 'message',
                 'sourcename']

    def __init__(self, kwname='', libname='', doc='', args=(), assign=(), tags=(),
                 timeout=None, type=BodyItem.KEYWORD, status='FAIL', starttime=None,
                 endtime=None, parent=None, sourcename=None):
        model.Keyword.__init__(self, None, doc, args, assign, tags, timeout, type, parent)
        #: Name of the keyword without library or resource name.
        self.kwname = kwname
        #: Name of the library or resource containing this keyword.
        self.libname = libname
        #: Execution status as a string. ``PASS``, ``FAIL``, ``SKIP`` or ``NOT RUN``.
        self.status = status
        #: Keyword execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.starttime = starttime
        #: Keyword execution end time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime
        #: Keyword status message. Used only if suite teardowns fails.
        self.message = ''
        #: Original name of keyword with embedded arguments.
        self.sourcename = sourcename
        self.body = None

    @setter
    def body(self, body):
        """Child keywords and messages as a :class:`~.Body` object."""
        return self.body_class(self, body)

    @property
    def keywords(self):
        """Deprecated since Robot Framework 4.0.

        Use :attr:`body` or :attr:`teardown` instead.
        """
        keywords = self.body.filter(messages=False)
        if self.teardown:
            keywords.append(self.teardown)
        return Keywords(self, keywords)

    @keywords.setter
    def keywords(self, keywords):
        Keywords.raise_deprecation_error()

    @property
    def messages(self):
        """Keyword's messages.

        Starting from Robot Framework 4.0 this is a list generated from messages
        in :attr:`body`.
        """
        return self.body.filter(messages=True)

    @property
    def children(self):
        """List of child keywords and messages in creation order.

        Deprecated since Robot Framework 4.0. Use :att:`body` instead.
        """
        warnings.warn("'Keyword.children' is deprecated. Use 'Keyword.body' instead.")
        return list(self.body)

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

    @name.setter
    def name(self, name):
        if name is not None:
            raise AttributeError("Cannot set 'name' attribute directly. "
                                 "Set 'kwname' and 'libname' separately instead.")
        self.kwname = None
        self.libname = None


class TestCase(model.TestCase, StatusMixin):
    """Represents results of a single test case.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['status', 'message', 'starttime', 'endtime']
    body_class = Body
    fixture_class = Keyword

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
    def not_run(self):
        return False

    @property
    def critical(self):
        warnings.warn("'TestCase.critical' is deprecated and always returns 'True'.")
        return True


class TestSuite(model.TestSuite, StatusMixin):
    """Represents results of a single test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['message', 'starttime', 'endtime']
    test_class = TestCase
    fixture_class = Keyword

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
        return self.status == self.PASS

    @property
    def failed(self):
        """``True`` if any test has failed, ``False`` otherwise."""
        return self.status == self.FAIL

    @property
    def skipped(self):
        """``True`` if there are no passed or failed tests, ``False`` otherwise."""
        return self.status == self.SKIP

    @property
    def not_run(self):
        return False

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
            return self.FAIL
        if stats.passed:
            return self.PASS
        return self.SKIP

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
