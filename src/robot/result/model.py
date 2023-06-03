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
At that time they can be inspected and modified by listeners__.

When results are parsed from XML output files after execution to be able to
create logs and reports, these objects are created by the
:func:`~.resultbuilder.ExecutionResult` factory method.
At that point they can be inspected and modified by `pre-Rebot modifiers`__.

The :func:`~.resultbuilder.ExecutionResult` factory method can also be used
by custom scripts and tools. In such usage it is often easiest to inspect and
modify these objects using the :mod:`visitor interface <robot.model.visitor>`.

If classes defined here are needed, for example, as type hints, they can
be imported via the :mod:`robot.running` module.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#programmatic-modification-of-results

"""

import sys
import warnings
from collections import OrderedDict
from datetime import datetime, timedelta
from itertools import chain
from pathlib import Path
from typing import Generic, Mapping, Sequence, Type, Union, TypeVar

if sys.version_info >= (3, 8):
    from typing import Literal

from robot import model
from robot.model import (BodyItem, create_fixture, DataDict, Keywords, Tags,
                         SuiteVisitor, TotalStatistics, TotalStatisticsBuilder,
                         TestCases, TestSuites)
from robot.utils import copy_signature, get_elapsed_time, KnownAtRuntime, setter

from .configurer import SuiteConfigurer
from .messagefilter import MessageFilter
from .modeldeprecation import deprecated, DeprecatedAttributesMixin
from .keywordremover import KeywordRemover
from .suiteteardownfailed import SuiteTeardownFailed, SuiteTeardownFailureHandler

IT = TypeVar('IT', bound='IfBranch|TryBranch')
FW = TypeVar('FW', bound='ForIteration|WhileIteration')

BodyItemParent = Union['TestSuite', 'TestCase', 'For', 'ForIteration', 'If', 'IfBranch',
                       'Try', 'TryBranch', 'While', 'WhileIteration', None]


class Body(model.BaseBody['Keyword', 'For', 'While', 'If', 'Try', 'Return', 'Continue',
                          'Break', 'Message', 'Error']):
    __slots__ = []


class Branches(model.BaseBranches['Keyword', 'For', 'While', 'If', 'Try', 'Return',
                                  'Continue', 'Break', 'Message', 'Error', IT]):
    __slots__ = []


class IterationType(Generic[FW]):
    """Class that wrapps `Generic` as python doesn't allow multple generic inheritance"""
    pass


class Iterations(model.BaseBody['Keyword', 'For', 'While', 'If', 'Try', 'Return',
                                'Continue', 'Break', 'Message', 'Error'], IterationType[FW]):
    __slots__ = ['iteration_class']
    iteration_type: Type[FW] = KnownAtRuntime

    def __init__(self, iteration_class: Type[FW],
                 parent: BodyItemParent = None,
                 items: 'Sequence[FW|DataDict]' = ()):
        self.iteration_class = iteration_class
        super().__init__(parent, items)

    @copy_signature(iteration_type)
    def create_iteration(self, *args, **kwargs) -> FW:
        return self._create(self.iteration_class, 'iteration_class', args, kwargs)


@Body.register
@Branches.register
@Iterations.register
class Message(model.Message):
    __slots__ = ()


class StatusMixin:
    PASS = 'PASS'
    FAIL = 'FAIL'
    SKIP = 'SKIP'
    NOT_RUN = 'NOT RUN'
    NOT_SET = 'NOT SET'
    starttime: 'str|None'
    endtime: 'str|None'
    __slots__ = ()

    @property
    def elapsedtime(self) -> int:
        """Total execution time in milliseconds.

        This attribute will be replaced by :attr:`elapsed_time` in the future.
        """
        return get_elapsed_time(self.starttime, self.endtime)

    @property
    def elapsed_time(self) -> timedelta:
        """Total execution time as a ``timedelta``.

        This attribute will replace :attr:`elapsedtime` in the future.

        New in Robot Framework 6.1.
        """
        return timedelta(milliseconds=self.elapsedtime)

    @property
    def start_time(self) -> 'datetime|None':
        """Execution start time as a ``datetime`` or as ``None`` if not set.

        This attribute will replace :attr:`starttime` in the future.

        New in Robot Framework 6.1.
        """
        return self._timestr_to_datetime(self.starttime) if self.starttime else None

    @start_time.setter
    def start_time(self, start_time: 'datetime|None'):
        self.starttime = self._datetime_to_timestr(start_time) if start_time else None

    @property
    def end_time(self) -> 'datetime|None':
        """Execution end time as a ``datetime`` or as ``None`` if not set.

        This attribute will replace :attr:`endtime` in the future.

        New in Robot Framework 6.1.
        """
        return self._timestr_to_datetime(self.endtime) if self.endtime else None

    @end_time.setter
    def end_time(self, end_time: 'datetime|None'):
        self.endtime = self._datetime_to_timestr(end_time) if end_time else None

    def _timestr_to_datetime(self, ts: str) -> datetime:
        micro = int(ts[18:]) * 1000
        return datetime(int(ts[:4]), int(ts[4:6]), int(ts[6:8]),
                        int(ts[9:11]), int(ts[12:14]), int(ts[15:17]), micro)

    def _datetime_to_timestr(self, dt: datetime) -> str:
        millis = int(round(dt.microsecond, -3) / 1000)
        return (f'{dt.year}{dt.month:02}{dt.day:02} '
                f'{dt.hour:02}:{dt.minute:02}.{dt.second:02}.{millis}')

    @property
    def passed(self) -> bool:
        """``True`` when :attr:`status` is 'PASS', ``False`` otherwise."""
        return self.status == self.PASS

    @passed.setter
    def passed(self, passed: bool):
        self.status = self.PASS if passed else self.FAIL

    @property
    def failed(self) -> bool:
        """``True`` when :attr:`status` is 'FAIL', ``False`` otherwise."""
        return self.status == self.FAIL

    @failed.setter
    def failed(self, failed: bool):
        self.status = self.FAIL if failed else self.PASS

    @property
    def skipped(self) -> bool:
        """``True`` when :attr:`status` is 'SKIP', ``False`` otherwise.

        Setting to ``False`` value is ambiguous and raises an exception.
        """
        return self.status == self.SKIP

    @skipped.setter
    def skipped(self, skipped: 'Literal[True]'):
        if not skipped:
            raise ValueError(f"`skipped` value must be truthy, got '{skipped}'.")
        self.status = self.SKIP

    @property
    def not_run(self) -> bool:
        """``True`` when :attr:`status` is 'NOT RUN', ``False`` otherwise.

        Setting to ``False`` value is ambiguous and raises an exception.
        """
        return self.status == self.NOT_RUN

    @not_run.setter
    def not_run(self, not_run: 'Literal[True]'):
        if not not_run:
            raise ValueError(f"`not_run` value must be truthy, got '{not_run}'.")
        self.status = self.NOT_RUN


class ForIteration(BodyItem, StatusMixin, DeprecatedAttributesMixin):
    """Represents one FOR loop iteration."""
    type = BodyItem.ITERATION
    body_class = Body
    repr_args = ('variables',)
    __slots__ = ['variables', 'status', 'starttime', 'endtime', 'doc']

    def __init__(self, variables: 'Mapping[str, str]|None' = None,
                 status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 doc: str = '',
                 parent: BodyItemParent = None):
        self.variables = OrderedDict(variables or ())
        self.parent = parent
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc
        self.body = []

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        return self.body_class(self, body)

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_for_iteration(self)

    @property
    @deprecated
    def name(self) -> str:
        return ', '.join('%s = %s' % item for item in self.variables.items())


@Body.register
class For(model.For, StatusMixin, DeprecatedAttributesMixin):
    iteration_class = ForIteration
    iterations_class = Iterations[iteration_class]
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, variables: Sequence[str] = (),
                 flavor: "Literal['IN', 'IN RANGE', 'IN ENUMERATE', 'IN ZIP']" = 'IN',
                 values: Sequence[str] = (),
                 start: 'str|None' = None,
                 mode: 'str|None' = None,
                 fill: 'str|None' = None,
                 status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 doc: str = '',
                 parent: BodyItemParent = None):
        super().__init__(variables, flavor, values, start, mode, fill, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc

    @setter
    def body(self, iterations: 'Sequence[ForIteration|DataDict]') -> iterations_class:
        return self.iterations_class(self.iteration_class, self, iterations)

    @property
    @deprecated
    def name(self) -> str:
        variables = ' | '.join(self.variables)
        values = ' | '.join(self.values)
        for name, value in [('start', self.start),
                            ('mode', self.mode),
                            ('fill', self.fill)]:
            if value is not None:
                values += f' | {name}={value}'
        return f'{variables} {self.flavor} [ {values} ]'


class WhileIteration(BodyItem, StatusMixin, DeprecatedAttributesMixin):
    """Represents one WHILE loop iteration."""
    type = BodyItem.ITERATION
    body_class = Body
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 doc: str = '',
                 parent: BodyItemParent = None):
        self.parent = parent
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        return self.body_class(self, body)

    def visit(self, visitor: SuiteVisitor):
        visitor.visit_while_iteration(self)

    @property
    @deprecated
    def name(self) -> str:
        return ''


@Body.register
class While(model.While, StatusMixin, DeprecatedAttributesMixin):
    iteration_class = WhileIteration
    iterations_class = Iterations[iteration_class]
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, condition: 'str|None' = None,
                 limit: 'str|None' = None,
                 on_limit: 'str|None' = None,
                 on_limit_message: 'str|None' = None,
                 status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 doc: str = '',
                 parent: BodyItemParent = None):
        super().__init__(condition, limit, on_limit, on_limit_message, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc

    @setter
    def body(self, iterations: 'Sequence[WhileIteration|DataDict]') -> iterations_class:
        return self.iterations_class(self.iteration_class, self, iterations)

    @property
    @deprecated
    def name(self) -> str:
        parts = []
        if self.condition:
            parts.append(self.condition)
        if self.limit:
            parts.append(f'limit={self.limit}')
        if self.on_limit:
            parts.append(f'on_limit={self.on_limit}')
        if self.on_limit_message:
            parts.append(f'on_limit_message={self.on_limit_message}')
        return ' | '.join(parts)


class IfBranch(model.IfBranch, StatusMixin, DeprecatedAttributesMixin):
    body_class = Body
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, type: str = BodyItem.IF,
                 condition: 'str|None' = None,
                 status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 doc: str = '',
                 parent: BodyItemParent = None):
        super().__init__(type, condition, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc

    @property
    @deprecated
    def name(self) -> str:
        return self.condition or ''


@Body.register
class If(model.If, StatusMixin, DeprecatedAttributesMixin):
    branch_class = IfBranch
    branches_class = Branches[branch_class]
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 doc: str = '',
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc


class TryBranch(model.TryBranch, StatusMixin, DeprecatedAttributesMixin):
    body_class = Body
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, type: str = BodyItem.TRY,
                 patterns: Sequence[str] = (),
                 pattern_type: 'str|None' = None,
                 variable: 'str|None' = None,
                 status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 doc: str = '',
                 parent: BodyItemParent = None):
        super().__init__(type, patterns, pattern_type, variable, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc

    @property
    @deprecated
    def name(self) -> str:
        patterns = list(self.patterns)
        if self.pattern_type:
            patterns.append(f'type={self.pattern_type}')
        parts = []
        if patterns:
            parts.append(' | '.join(patterns))
        if self.variable:
            parts.append(f'AS {self.variable}')
        return ' '.join(parts)


@Body.register
class Try(model.Try, StatusMixin, DeprecatedAttributesMixin):
    branch_class = TryBranch
    branches_class = Branches[branch_class]
    __slots__ = ['status', 'starttime', 'endtime', 'doc']

    def __init__(self, status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 doc: str = '',
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.doc = doc


@Body.register
class Return(model.Return, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'starttime', 'endtime']
    body_class = Body

    def __init__(self, values: Sequence[str] = (),
                 status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(values, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Child keywords and messages as a :class:`~.Body` object.

        Typically empty. Only contains something if running RETURN has failed
        due to a syntax error or listeners have logged messages or executed
        keywords.
        """
        return self.body_class(self, body)

    @property
    @deprecated
    def args(self) -> 'tuple[str, ...]':
        return self.values

    @property
    @deprecated
    def doc(self) -> str:
        return ''


@Body.register
class Continue(model.Continue, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'starttime', 'endtime']
    body_class = Body

    def __init__(self, status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Child keywords and messages as a :class:`~.Body` object.

        Typically empty. Only contains something if running CONTINUE has failed
        due to a syntax error or listeners have logged messages or executed
        keywords.
        """
        return self.body_class(self, body)

    @property
    @deprecated
    def args(self) -> 'tuple[str, ...]':
        return ()

    @property
    @deprecated
    def doc(self) -> str:
        return ''


@Body.register
class Break(model.Break, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'starttime', 'endtime']
    body_class = Body

    def __init__(self, status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Child keywords and messages as a :class:`~.Body` object.

        Typically empty. Only contains something if running BREAK has failed
        due to a syntax error or listeners have logged messages or executed
        keywords.
        """
        return self.body_class(self, body)

    @property
    @deprecated
    def args(self) -> 'tuple[str, ...]':
        return ()

    @property
    @deprecated
    def doc(self) -> str:
        return ''


@Body.register
class Error(model.Error, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'starttime', 'endtime']
    body_class = Body

    def __init__(self, values: Sequence[str] = (),
                 status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(values, parent)
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Messages as a :class:`~.Body` object.

        Typically contains the message that caused the error.
        """
        return self.body_class(self, body)

    @property
    @deprecated
    def kwname(self) -> str:
        return self.values[0]

    @property
    @deprecated
    def args(self) -> 'tuple[str, ...]':
        return self.values[1:]

    @property
    @deprecated
    def doc(self) -> 'str':
        return ''


@Body.register
@Branches.register
@Iterations.register
class Keyword(model.Keyword, StatusMixin):
    """Represents an executed library or user keyword."""
    body_class = Body
    __slots__ = ['kwname', 'libname', 'doc', 'timeout', 'status', '_teardown',
                 'starttime', 'endtime', 'message', 'sourcename']

    def __init__(self, kwname: str = '',
                 libname: str = '',
                 doc: str = '',
                 args: Sequence[str] = (),
                 assign: Sequence[str] = (),
                 tags: Sequence[str] = (),
                 timeout: 'str|None' = None,
                 type: str = BodyItem.KEYWORD,
                 status: str = 'FAIL',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 sourcename: 'str|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(None, args, assign, type, parent)
        #: Name of the keyword without library or resource name.
        self.kwname = kwname
        #: Name of the library or resource containing this keyword.
        self.libname = libname
        self.doc = doc
        self.tags = tags
        self.timeout = timeout
        self.status = status
        self.starttime = starttime
        self.endtime = endtime
        #: Keyword status message. Used only if suite teardowns fails.
        self.message = ''
        #: Original name of keyword with embedded arguments.
        self.sourcename = sourcename
        self._teardown = None
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Possible keyword body as a :class:`~.Body` object.

        Body can consist of child keywords, messages, and control structures
        such as IF/ELSE. Library keywords typically have an empty body.
        """
        return self.body_class(self, body)

    @property
    def keywords(self) -> Keywords:
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
    def messages(self) -> 'list[Message]':
        """Keyword's messages.

        Starting from Robot Framework 4.0 this is a list generated from messages
        in :attr:`body`.
        """
        return self.body.filter(messages=True)    # type: ignore

    @property
    def children(self) -> 'list[BodyItem]':
        """List of child keywords and messages in creation order.

        Deprecated since Robot Framework 4.0. Use :attr:`body` instead.
        """
        warnings.warn("'Keyword.children' is deprecated. Use 'Keyword.body' instead.")
        return list(self.body)

    @property
    def name(self) -> 'str|None':
        """Keyword name in format ``libname.kwname``.

        Just ``kwname`` if :attr:`libname` is empty. In practice that is the
        case only with user keywords in the same file as the executed test case
        or test suite.

        Cannot be set directly. Set :attr:`libname` and :attr:`kwname`
        separately instead.
        """
        if not self.libname:
            return self.kwname
        return f'{self.libname}.{self.kwname}'

    @name.setter
    def name(self, name):
        if name is not None:
            raise AttributeError("Cannot set 'name' attribute directly. "
                                 "Set 'kwname' and 'libname' separately instead.")
        self.kwname = None
        self.libname = None

    @property    # Cannot use @setter because it would create teardowns recursively.
    def teardown(self) -> 'Keyword':
        """Keyword teardown as a :class:`Keyword` object.

        Teardown can be modified by setting attributes directly::

            keyword.teardown.name = 'Example'
            keyword.teardown.args = ('First', 'Second')

        Alternatively the :meth:`config` method can be used to set multiple
        attributes in one call::

            keyword.teardown.config(name='Example', args=('First', 'Second'))

        The easiest way to reset the whole teardown is setting it to ``None``.
        It will automatically recreate the underlying ``Keyword`` object::

            keyword.teardown = None

        This attribute is a ``Keyword`` object also when a keyword has no teardown
        but in that case its truth value is ``False``. If there is a need to just
        check does a keyword have a teardown, using the :attr:`has_teardown`
        attribute avoids creating the ``Keyword`` object and is thus more memory
        efficient.

        New in Robot Framework 4.0. Earlier teardown was accessed like
        ``keyword.keywords.teardown``. :attr:`has_teardown` is new in Robot
        Framework 4.1.2.
        """
        if self._teardown is None:
            self._teardown = create_fixture(self.__class__, None, self, self.TEARDOWN)
        return self._teardown

    @teardown.setter
    def teardown(self, teardown: 'Keyword|DataDict|None'):
        self._teardown = create_fixture(self.__class__, teardown, self, self.TEARDOWN)

    @property
    def has_teardown(self) -> bool:
        """Check does a keyword have a teardown without creating a teardown object.

        A difference between using ``if kw.has_teardown:`` and ``if kw.teardown:``
        is that accessing the :attr:`teardown` attribute creates a :class:`Keyword`
        object representing a teardown even when the keyword actually does not
        have one. This typically does not matter, but with bigger suite structures
        having lots of keywords it can have a considerable effect on memory usage.

        New in Robot Framework 4.1.2.
        """
        return bool(self._teardown)

    @setter
    def tags(self, tags: Sequence[str]) -> model.Tags:
        """Keyword tags as a :class:`~.model.tags.Tags` object."""
        return Tags(tags)


class TestCase(model.TestCase[Keyword], StatusMixin):
    """Represents results of a single test case.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['status', 'message', 'starttime', 'endtime']
    body_class = Body
    fixture_class = Keyword

    def __init__(self, name: str = '',
                 doc: str = '',
                 tags: Sequence[str] = (),
                 timeout: 'str|None' = None,
                 lineno: 'int|None' = None,
                 status: str = 'FAIL',
                 message: str = '',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 parent: 'TestSuite|None' = None):
        super().__init__(name, doc, tags, timeout, lineno, parent)
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
    def not_run(self) -> bool:
        return False

    @property
    def critical(self) -> bool:
        warnings.warn("'TestCase.critical' is deprecated and always returns 'True'.")
        return True

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Test body as a :class:`~robot.result.Body` object."""
        return self.body_class(self, body)


class TestSuite(model.TestSuite[Keyword, TestCase], StatusMixin):
    """Represents results of a single test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['message', 'starttime', 'endtime']
    test_class = TestCase
    fixture_class = Keyword

    def __init__(self, name: str = '',
                 doc: str = '',
                 metadata: 'Mapping[str, str]|None' = None,
                 source: 'Path|str|None' = None,
                 rpa: bool = False,
                 message: str = '',
                 starttime: 'str|None' = None,
                 endtime: 'str|None' = None,
                 parent: 'TestSuite|None' = None):
        super().__init__(name, doc, metadata, source, rpa, parent)
        #: Possible suite setup or teardown error message.
        self.message = message
        #: Suite execution start time in format ``%Y%m%d %H:%M:%S.%f``.
        self.starttime = starttime
        #: Suite execution end time in format ``%Y%m%d %H:%M:%S.%f``.
        self.endtime = endtime

    @property
    def passed(self) -> bool:
        """``True`` if no test has failed but some have passed, ``False`` otherwise."""
        return self.status == self.PASS

    @property
    def failed(self) -> bool:
        """``True`` if any test has failed, ``False`` otherwise."""
        return self.status == self.FAIL

    @property
    def skipped(self) -> bool:
        """``True`` if there are no passed or failed tests, ``False`` otherwise."""
        return self.status == self.SKIP

    @property
    def not_run(self) -> bool:
        return False

    @property
    def status(self) -> "Literal['PASS', 'SKIP', 'FAIL']":
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
    def statistics(self) -> TotalStatistics:
        """Suite statistics as a :class:`~robot.model.totalstatistics.TotalStatistics` object.

        Recreated every time this property is accessed, so saving the results
        to a variable and inspecting it is often a good idea::

            stats = suite.statistics
            print(stats.failed)
            print(stats.total)
            print(stats.message)
        """
        return TotalStatisticsBuilder(self, bool(self.rpa)).stats

    @property
    def full_message(self) -> str:
        """Combination of :attr:`message` and :attr:`stat_message`."""
        if not self.message:
            return self.stat_message
        return f'{self.message}\n\n{self.stat_message}'

    @property
    def stat_message(self) -> str:
        """String representation of the :attr:`statistics`."""
        return self.statistics.message

    @property
    def elapsedtime(self) -> int:
        """Total execution time in milliseconds."""
        if self.starttime and self.endtime:
            return get_elapsed_time(self.starttime, self.endtime)
        return sum(child.elapsedtime for child in
                   chain(self.suites, self.tests, (self.setup, self.teardown)))

    @setter
    def suites(self, suites: 'Sequence[TestSuite|DataDict]') -> TestSuites['TestSuite']:
        return TestSuites['TestSuite'](self.__class__, self, suites)

    def remove_keywords(self, how: str):
        """Remove keywords based on the given condition.

        :param how: What approach to use when removing keywords. Either
            ``ALL``, ``PASSED``, ``FOR``, ``WUKS``, or ``NAME:<pattern>``.

        For more information about the possible values see the documentation
        of the ``--removekeywords`` command line option.
        """
        self.visit(KeywordRemover(how))

    def filter_messages(self, log_level: str = 'TRACE'):
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

        Not to be confused with :meth:`config` method that suites, tests,
        and keywords have to make it possible to set multiple attributes in
        one call.
        """
        super().configure()    # Parent validates is call allowed.
        self.visit(SuiteConfigurer(**options))

    def handle_suite_teardown_failures(self):
        """Internal usage only."""
        self.visit(SuiteTeardownFailureHandler())

    def suite_teardown_failed(self, message: str):
        """Internal usage only."""
        self.visit(SuiteTeardownFailed(message))

    def suite_teardown_skipped(self, message: str):
        """Internal usage only."""
        self.visit(SuiteTeardownFailed(message, skipped=True))
