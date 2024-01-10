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

from datetime import datetime, timedelta
from io import StringIO
from itertools import chain
from pathlib import Path
from typing import Literal, Mapping, overload, Sequence, Union, TextIO, TypeVar

from robot import model
from robot.model import (BodyItem, create_fixture, DataDict, Tags, TestSuites,
                         TotalStatistics, TotalStatisticsBuilder)
from robot.utils import is_dict_like, is_list_like, setter

from .configurer import SuiteConfigurer
from .messagefilter import MessageFilter
from .modeldeprecation import DeprecatedAttributesMixin
from .keywordremover import KeywordRemover
from .suiteteardownfailed import SuiteTeardownFailed, SuiteTeardownFailureHandler


IT = TypeVar('IT', bound='IfBranch|TryBranch')
FW = TypeVar('FW', bound='ForIteration|WhileIteration')
BodyItemParent = Union['TestSuite', 'TestCase', 'Keyword', 'For', 'ForIteration', 'If',
                       'IfBranch', 'Try', 'TryBranch', 'While', 'WhileIteration', None]


class Body(model.BaseBody['Keyword', 'For', 'While', 'If', 'Try', 'Var', 'Return',
                          'Continue', 'Break', 'Message', 'Error']):
    __slots__ = ()


class Branches(model.BaseBranches['Keyword', 'For', 'While', 'If', 'Try', 'Var', 'Return',
                                  'Continue', 'Break', 'Message', 'Error', IT]):
    __slots__ = ()


class Iterations(model.BaseIterations['Keyword', 'For', 'While', 'If', 'Try', 'Var', 'Return',
                                      'Continue', 'Break', 'Message', 'Error', FW]):
    __slots__ = ()


@Body.register
@Branches.register
@Iterations.register
class Message(model.Message):
    __slots__ = ()

    def to_dict(self) -> DataDict:
        data: DataDict = {
            'type': self.type,
            'message': self.message,
            'level': self.level,
            'html': self.html,
        }
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        return data


class StatusMixin:
    PASS = 'PASS'
    FAIL = 'FAIL'
    SKIP = 'SKIP'
    NOT_RUN = 'NOT RUN'
    NOT_SET = 'NOT SET'
    status: Literal['PASS', 'FAIL', 'SKIP', 'NOT RUN', 'NOT SET']
    __slots__ = ()

    @property
    def start_time(self) -> 'datetime|None':
        """Execution start time as a ``datetime`` or as a ``None`` if not set.

        If start time is not set, it is calculated based :attr:`end_time`
        and :attr:`elapsed_time` if possible.

        Can be set either directly as a ``datetime`` or as a string in ISO 8601
        format.

        New in Robot Framework 6.1. Heavily enhanced in Robot Framework 7.0.
        """
        if self._start_time:
            return self._start_time
        if self._end_time:
            return self._end_time - self.elapsed_time
        return None

    @start_time.setter
    def start_time(self, start_time: 'datetime|str|None'):
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        self._start_time = start_time

    @property
    def end_time(self) -> 'datetime|None':
        """Execution end time as a ``datetime`` or as a ``None`` if not set.

        If end time is not set, it is calculated based :attr:`start_time`
        and :attr:`elapsed_time` if possible.

        Can be set either directly as a ``datetime`` or as a string in ISO 8601
        format.

        New in Robot Framework 6.1. Heavily enhanced in Robot Framework 7.0.
        """
        if self._end_time:
            return self._end_time
        if self._start_time:
            return self._start_time + self.elapsed_time
        return None

    @end_time.setter
    def end_time(self, end_time: 'datetime|str|None'):
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        self._end_time = end_time

    @property
    def elapsed_time(self) -> timedelta:
        """Total execution time as a ``timedelta``.

        If not set, calculated based on :attr:`start_time` and :attr:`end_time`
        if possible. If that fails, calculated based on the elapsed time of
        child items.

        Can be set either directly as a ``timedelta`` or as an integer or a float
        representing seconds.

        New in Robot Framework 6.1. Heavily enhanced in Robot Framework 7.0.
        """
        if self._elapsed_time is not None:
            return self._elapsed_time
        if self._start_time and self._end_time:
            return self._end_time - self._start_time
        return self._elapsed_time_from_children()

    def _elapsed_time_from_children(self) -> timedelta:
        elapsed = timedelta()
        for child in self.body:
            if hasattr(child, 'elapsed_time'):
                elapsed += child.elapsed_time
        if getattr(self, 'has_setup', False):
            elapsed += self.setup.elapsed_time
        if getattr(self, 'has_teardown', False):
            elapsed += self.teardown.elapsed_time
        return elapsed

    @elapsed_time.setter
    def elapsed_time(self, elapsed_time: 'timedelta|int|float|None'):
        if isinstance(elapsed_time, (int, float)):
            elapsed_time = timedelta(seconds=elapsed_time)
        self._elapsed_time = elapsed_time

    @property
    def starttime(self) -> 'str|None':
        """Execution start time as a string or as a ``None`` if not set.

        The string format is ``%Y%m%d %H:%M:%S.%f``.

        Considered deprecated starting from Robot Framework 7.0.
        :attr:`start_time` should be used instead.
        """
        return self._datetime_to_timestr(self.start_time)

    @starttime.setter
    def starttime(self, starttime: 'str|None'):
        self.start_time = self._timestr_to_datetime(starttime)

    @property
    def endtime(self) -> 'str|None':
        """Execution end time as a string or as a ``None`` if not set.

        The string format is ``%Y%m%d %H:%M:%S.%f``.

        Considered deprecated starting from Robot Framework 7.0.
        :attr:`end_time` should be used instead.
        """
        return self._datetime_to_timestr(self.end_time)

    @endtime.setter
    def endtime(self, endtime: 'str|None'):
        self.end_time = self._timestr_to_datetime(endtime)

    @property
    def elapsedtime(self) -> int:
        """Total execution time in milliseconds.

        Considered deprecated starting from Robot Framework 7.0.
        :attr:`elapsed_time` should be used instead.
        """
        return round(self.elapsed_time.total_seconds() * 1000)

    def _timestr_to_datetime(self, ts: 'str|None') -> 'datetime|None':
        if not ts:
            return None
        ts = ts.ljust(24, '0')
        return datetime(int(ts[:4]), int(ts[4:6]), int(ts[6:8]),
                        int(ts[9:11]), int(ts[12:14]), int(ts[15:17]), int(ts[18:24]))

    def _datetime_to_timestr(self, dt: 'datetime|None') -> 'str|None':
        if not dt:
            return None
        return dt.isoformat(' ', timespec='milliseconds').replace('-', '')

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
    def skipped(self, skipped: Literal[True]):
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
    def not_run(self, not_run: Literal[True]):
        if not not_run:
            raise ValueError(f"`not_run` value must be truthy, got '{not_run}'.")
        self.status = self.NOT_RUN

    def to_dict(self):
        data = {'status': self.status,
                'elapsed_time': self.elapsed_time.total_seconds()}
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.message:
            data['message'] = self.message
        return data


class ForIteration(model.ForIteration, StatusMixin, DeprecatedAttributesMixin):
    body_class = Body
    __slots__ = ['assign', 'message', 'status', '_start_time', '_end_time',
                 '_elapsed_time']

    def __init__(self, assign: 'Mapping[str, str]|None' = None,
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(assign, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


@Body.register
class For(model.For, StatusMixin, DeprecatedAttributesMixin):
    iteration_class = ForIteration
    iterations_class = Iterations[iteration_class]
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']

    def __init__(self, assign: Sequence[str] = (),
                 flavor: Literal['IN', 'IN RANGE', 'IN ENUMERATE', 'IN ZIP'] = 'IN',
                 values: Sequence[str] = (),
                 start: 'str|None' = None,
                 mode: 'str|None' = None,
                 fill: 'str|None' = None,
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(assign, flavor, values, start, mode, fill, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    @setter
    def body(self, iterations: 'Sequence[ForIteration|DataDict]') -> iterations_class:
        return self.iterations_class(self.iteration_class, self, iterations)

    @property
    def _log_name(self):
        return str(self)[7:]    # Drop 'FOR    ' prefix.

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


class WhileIteration(model.WhileIteration, StatusMixin, DeprecatedAttributesMixin):
    body_class = Body
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']

    def __init__(self, status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


@Body.register
class While(model.While, StatusMixin, DeprecatedAttributesMixin):
    iteration_class = WhileIteration
    iterations_class = Iterations[iteration_class]
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']

    def __init__(self, condition: 'str|None' = None,
                 limit: 'str|None' = None,
                 on_limit: 'str|None' = None,
                 on_limit_message: 'str|None' = None,
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(condition, limit, on_limit, on_limit_message, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    @setter
    def body(self, iterations: 'Sequence[WhileIteration|DataDict]') -> iterations_class:
        return self.iterations_class(self.iteration_class, self, iterations)

    @property
    def _log_name(self):
        return str(self)[9:]    # Drop 'WHILE    ' prefix.

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


class IfBranch(model.IfBranch, StatusMixin, DeprecatedAttributesMixin):
    body_class = Body
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']

    def __init__(self, type: str = BodyItem.IF,
                 condition: 'str|None' = None,
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(type, condition, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    @property
    def _log_name(self):
        return self.condition or ''

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


@Body.register
class If(model.If, StatusMixin, DeprecatedAttributesMixin):
    branch_class = IfBranch
    branches_class = Branches[branch_class]
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']

    def __init__(self, status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


class TryBranch(model.TryBranch, StatusMixin, DeprecatedAttributesMixin):
    body_class = Body
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']

    def __init__(self, type: str = BodyItem.TRY,
                 patterns: Sequence[str] = (),
                 pattern_type: 'str|None' = None,
                 assign: 'str|None' = None,
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(type, patterns, pattern_type, assign, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    @property
    def _log_name(self):
        return str(self)[len(self.type)+4:]    # Drop '<type>    ' prefix.

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


@Body.register
class Try(model.Try, StatusMixin, DeprecatedAttributesMixin):
    branch_class = TryBranch
    branches_class = Branches[branch_class]
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']

    def __init__(self, status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


@Body.register
class Var(model.Var, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']
    body_class = Body

    def __init__(self, name: str = '',
                 value: 'str|Sequence[str]' = (),
                 scope: 'str|None' = None,
                 separator: 'str|None' = None,
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(name, value, scope, separator, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Child keywords and messages as a :class:`~.Body` object.

        Typically empty. Only contains something if running VAR has failed
        due to a syntax error or listeners have logged messages or executed
        keywords.
        """
        return self.body_class(self, body)

    @property
    def _log_name(self):
        return str(self)[7:]    # Drop 'VAR    ' prefix.

    def to_dict(self) -> DataDict:
        data = {**super().to_dict(), **StatusMixin.to_dict(self)}
        if self.body:
            data['body'] = self.body.to_dicts()
        return data


@Body.register
class Return(model.Return, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']
    body_class = Body

    def __init__(self, values: Sequence[str] = (),
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(values, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Child keywords and messages as a :class:`~.Body` object.

        Typically empty. Only contains something if running RETURN has failed
        due to a syntax error or listeners have logged messages or executed
        keywords.
        """
        return self.body_class(self, body)

    def to_dict(self) -> DataDict:
        data = {**super().to_dict(), **StatusMixin.to_dict(self)}
        if self.body:
            data['body'] = self.body.to_dicts()
        return data


@Body.register
class Continue(model.Continue, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']
    body_class = Body

    def __init__(self, status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Child keywords and messages as a :class:`~.Body` object.

        Typically empty. Only contains something if running CONTINUE has failed
        due to a syntax error or listeners have logged messages or executed
        keywords.
        """
        return self.body_class(self, body)

    def to_dict(self) -> DataDict:
        data = {**super().to_dict(), **StatusMixin.to_dict(self)}
        if self.body:
            data['body'] = self.body.to_dicts()
        return data


@Body.register
class Break(model.Break, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']
    body_class = Body

    def __init__(self, status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Child keywords and messages as a :class:`~.Body` object.

        Typically empty. Only contains something if running BREAK has failed
        due to a syntax error or listeners have logged messages or executed
        keywords.
        """
        return self.body_class(self, body)

    def to_dict(self) -> DataDict:
        data = {**super().to_dict(), **StatusMixin.to_dict(self)}
        if self.body:
            data['body'] = self.body.to_dicts()
        return data


@Body.register
class Error(model.Error, StatusMixin, DeprecatedAttributesMixin):
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']
    body_class = Body

    def __init__(self, values: Sequence[str] = (),
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(values, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.body = ()

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Messages as a :class:`~.Body` object.

        Typically contains the message that caused the error.
        """
        return self.body_class(self, body)

    def to_dict(self) -> DataDict:
        data = {**super().to_dict(), **StatusMixin.to_dict(self)}
        if self.body:
            data['body'] = self.body.to_dicts()
        return data


@Body.register
@Branches.register
@Iterations.register
class Keyword(model.Keyword, StatusMixin):
    """Represents an executed library or user keyword."""
    body_class = Body
    __slots__ = ['owner', 'source_name', 'doc', 'timeout', 'status', 'message',
                 '_start_time', '_end_time', '_elapsed_time', '_setup', '_teardown']

    def __init__(self, name: 'str|None' = '',
                 owner: 'str|None' = None,
                 source_name: 'str|None' = None,
                 doc: str = '',
                 args: model.Arguments = (),
                 assign: Sequence[str] = (),
                 tags: Sequence[str] = (),
                 timeout: 'str|None' = None,
                 type: str = BodyItem.KEYWORD,
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: BodyItemParent = None):
        super().__init__(name, args, assign, type, parent)
        #: Name of the library or resource containing this keyword.
        self.owner = owner
        #: Original name of keyword with embedded arguments.
        self.source_name = source_name
        self.doc = doc
        self.tags = tags
        self.timeout = timeout
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self._setup = None
        self._teardown = None
        self.body = ()

    @setter
    def args(self, args: model.Arguments) -> 'tuple[str, ...]':
        """Keyword arguments.

        Arguments originating from normal data are given as a list of strings.
        Programmatically it is possible to use also other types and named arguments
        can be specified using name-value tuples. Additionally, it is possible
        o give arguments directly as a list of positional arguments and a dictionary
        of named arguments. In all these cases arguments are stored as strings.
        """
        if len(args) == 2 and is_list_like(args[0]) and is_dict_like(args[1]):
            positional = [str(a) for a in args[0]]
            named = [f'{n}={v}' for n, v in args[1].items()]
            return tuple(positional + named)
        return tuple([a if isinstance(a, str) else self._arg_to_str(a) for a in args])

    def _arg_to_str(self, arg):
        if isinstance(arg, tuple):
            if len(arg) == 2:
                return f'{arg[0]}={arg[1]}'
            if len(arg) == 1:
                return str(arg[0])
        return str(arg)

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Possible keyword body as a :class:`~.Body` object.

        Body can consist of child keywords, messages, and control structures
        such as IF/ELSE. Library keywords typically have an empty body.
        """
        return self.body_class(self, body)

    @property
    def messages(self) -> 'list[Message]':
        """Keyword's messages.

        Starting from Robot Framework 4.0 this is a list generated from messages
        in :attr:`body`.
        """
        return self.body.filter(messages=True)    # type: ignore

    @property
    def full_name(self) -> 'str|None':
        """Keyword name in format ``owner.name``.

        Just ``name`` if :attr:`owner` is not set. In practice this is the
        case only with user keywords in the suite file.

        Cannot be set directly. Set :attr:`name` and :attr:`owner` separately
        instead.

        Notice that prior to Robot Framework 7.0, the ``name`` attribute contained
        the full name and keyword and owner names were in ``kwname`` and ``libname``,
        respectively.
        """
        return f'{self.owner}.{self.name}' if self.owner else self.name

    # TODO: Deprecate 'kwname', 'libname' and 'sourcename' loudly in RF 8.
    @property
    def kwname(self) -> 'str|None':
        """Deprecated since Robot Framework 7.0. Use :attr:`name` instead."""
        return self.name

    @kwname.setter
    def kwname(self, name: 'str|None'):
        self.name = name

    @property
    def libname(self) -> 'str|None':
        """Deprecated since Robot Framework 7.0. Use :attr:`owner` instead."""
        return self.owner

    @libname.setter
    def libname(self, name: 'str|None'):
        self.owner = name

    @property
    def sourcename(self) -> str:
        """Deprecated since Robot Framework 7.0. Use :attr:`source_name` instead."""
        return self.source_name

    @sourcename.setter
    def sourcename(self, name: str):
        self.source_name = name

    @property
    def setup(self) -> 'Keyword':
        """Keyword setup as a :class:`Keyword` object.

        See :attr:`teardown` for more information. New in Robot Framework 7.0.
        """
        if self._setup is None:
            self.setup = None
        return self._setup

    @setup.setter
    def setup(self, setup: 'Keyword|DataDict|None'):
        self._setup = create_fixture(self.__class__, setup, self, self.SETUP)

    @property
    def has_setup(self) -> bool:
        """Check does a keyword have a setup without creating a setup object.

        See :attr:`has_teardown` for more information. New in Robot Framework 7.0.
        """
        return bool(self._setup)

    @property
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
            self.teardown = None
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

    def to_dict(self) -> DataDict:
        data = {**super().to_dict(), **StatusMixin.to_dict(self)}
        if self.owner:
            data['owner'] = self.owner
        if self.source_name:
            data['source_name'] = self.source_name
        if self.doc:
            data['doc'] = self.doc
        if self.tags:
            data['tags'] = list(self.tags)
        if self.timeout:
            data['timeout'] = self.timeout
        if self.body:
            data['body'] = self.body.to_dicts()
        if self.has_setup:
            data['setup'] = self.setup.to_dict()
        if self.has_teardown:
            data['teardown'] = self.teardown.to_dict()
        return data


class TestCase(model.TestCase[Keyword], StatusMixin):
    """Represents results of a single test case.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['status', 'message', '_start_time', '_end_time', '_elapsed_time']
    body_class = Body
    fixture_class = Keyword

    def __init__(self, name: str = '',
                 doc: str = '',
                 tags: Sequence[str] = (),
                 timeout: 'str|None' = None,
                 lineno: 'int|None' = None,
                 status: str = 'FAIL',
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: 'TestSuite|None' = None):
        super().__init__(name, doc, tags, timeout, lineno, parent)
        self.status = status
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    @property
    def not_run(self) -> bool:
        return False

    @setter
    def body(self, body: 'Sequence[BodyItem|DataDict]') -> Body:
        """Test body as a :class:`~robot.result.Body` object."""
        return self.body_class(self, body)

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}


class TestSuite(model.TestSuite[Keyword, TestCase], StatusMixin):
    """Represents results of a single test suite.

    See the base class for documentation of attributes not documented here.
    """
    __slots__ = ['message', '_start_time', '_end_time', '_elapsed_time']
    test_class = TestCase
    fixture_class = Keyword

    def __init__(self, name: str = '',
                 doc: str = '',
                 metadata: 'Mapping[str, str]|None' = None,
                 source: 'Path|str|None' = None,
                 rpa: bool = False,
                 message: str = '',
                 start_time: 'datetime|str|None' = None,
                 end_time: 'datetime|str|None' = None,
                 elapsed_time: 'timedelta|int|float|None' = None,
                 parent: 'TestSuite|None' = None):
        super().__init__(name, doc, metadata, source, rpa, parent)
        #: Possible suite setup or teardown error message.
        self.message = message
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time

    def _elapsed_time_from_children(self) -> timedelta:
        elapsed = timedelta()
        if self.has_setup:
            elapsed += self.setup.elapsed_time
        if self.has_teardown:
            elapsed += self.teardown.elapsed_time
        for child in chain(self.suites, self.tests):
            elapsed += child.elapsed_time
        return elapsed

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
    def status(self) -> Literal['PASS', 'SKIP', 'FAIL']:
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

    @setter
    def suites(self, suites: 'Sequence[TestSuite|DataDict]') -> TestSuites['TestSuite']:
        return TestSuites['TestSuite'](self.__class__, self, suites)

    def remove_keywords(self, how: str):
        """Remove keywords based on the given condition.

        :param how: Which approach to use when removing keywords. Either
            ``ALL``, ``PASSED``, ``FOR``, ``WUKS``, or ``NAME:<pattern>``.

        For more information about the possible values see the documentation
        of the ``--removekeywords`` command line option.
        """
        self.visit(KeywordRemover.from_config(how))

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

    def to_dict(self) -> DataDict:
        return {**super().to_dict(), **StatusMixin.to_dict(self)}

    @overload
    def to_xml(self, file: None = None) -> str:
        ...

    @overload
    def to_xml(self, file: 'TextIO|Path|str') -> None:
        ...

    def to_xml(self, file: 'None|TextIO|Path|str' = None) -> 'str|None':
        """Serialize suite into XML.

        The format is the same that is used with normal output.xml files, but
        the ``<robot>`` root node is omitted and the result contains only
        the ``<suite>`` structure.

        The ``file`` parameter controls what to do with the resulting XML data.
        It can be:

        - ``None`` (default) to return the data as a string,
        - an open file object where to write the data to, or
        - a path (``pathlib.Path`` or string) to a file where to write
          the data using UTF-8 encoding.

        A serialized suite can be recreated by using the :meth:`from_xml` method.

        New in Robot Framework 7.0.
        """
        from robot.reporting.outputwriter import OutputWriter

        output, close = self._get_output(file)
        try:
            self.visit(OutputWriter(output, suite_only=True))
        finally:
            if close:
                output.close()
        return output.getvalue() if file is None else None

    def _get_output(self, output) -> 'tuple[TextIO|StringIO, bool]':
        close = False
        if output is None:
            output = StringIO()
        elif isinstance(output, (Path, str)):
            output = open(output, 'w')
            close = True
        return output, close

    @classmethod
    def from_xml(cls, source: 'str|TextIO|Path') -> 'TestSuite':
        """Create suite based on results in XML.

        The data is given as the ``source`` parameter. It can be:

        - a string containing the data directly,
        - an open file object where to read the data from, or
        - a path (``pathlib.Path`` or string) to a UTF-8 encoded file to read.

        Supports both normal output.xml files and files containing only the
        ``<suite>`` structure created, for example, with the :meth:`to_xml`
        method. When using normal output.xml files, possible execution errors
        listed in ``<errors>`` are silently ignored. If that is a problem,
        :class:`~robot.result.resultbuilder.ExecutionResult` should be used
        instead.

        New in Robot Framework 7.0.
        """
        from .resultbuilder import ExecutionResult

        return ExecutionResult(source).suite
