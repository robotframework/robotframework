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

from datetime import datetime
from pathlib import Path
from typing import overload, TextIO

from robot.errors import DataError
from robot.model import Statistics
from robot.utils import JsonDumper, JsonLoader, setter
from robot.version import get_full_version

from .executionerrors import ExecutionErrors
from .model import TestSuite


def is_json_source(source) -> bool:
    if isinstance(source, bytes):
        # ISO-8859-1 is most likely *not* the right encoding, but decoding bytes
        # with it always succeeds and characters we care about ought to be correct
        # at least if the right encoding is UTF-8 or any ISO-8859-x encoding.
        source = source.decode('ISO-8859-1')
    if isinstance(source, str):
        source = source.strip()
        first, last = (source[0], source[-1]) if source else ('', '')
        if (first, last) == ('{', '}'):
            return True
        if (first, last) == ('<', '>'):
            return False
        path = Path(source)
    elif isinstance(source, Path):
        path = source
    elif hasattr(source, 'name') and isinstance(source.name, str):
        path = Path(source.name)
    else:
        return False
    return bool(path and path.suffix.lower() == '.json')


class Result:
    """Test execution results.

    Can be created based on XML output files using the
    :func:`~.resultbuilder.ExecutionResult`
    factory method. Also returned by the
    :meth:`robot.running.TestSuite.run <robot.running.model.TestSuite.run>`
    method.
    """

    def __init__(self, source: 'Path|str|None' = None,
                 suite: 'TestSuite|None' = None,
                 errors: 'ExecutionErrors|None' = None,
                 rpa: 'bool|None' = None,
                 generator: str = 'unknown',
                 generation_time: 'datetime|str|None' = None):
        self.source = Path(source) if isinstance(source, str) else source
        self.suite = suite or TestSuite()
        self.errors = errors or ExecutionErrors()
        self.rpa = rpa
        self.generator = generator
        self.generation_time = generation_time
        self._status_rc = True
        self._stat_config = {}

    @setter
    def rpa(self, rpa: 'bool|None') -> 'bool|None':
        if rpa is not None:
            self._set_suite_rpa(self.suite, rpa)
        return rpa

    def _set_suite_rpa(self, suite, rpa):
        suite.rpa = rpa
        for child in suite.suites:
            self._set_suite_rpa(child, rpa)

    @setter
    def generation_time(self, timestamp: 'datetime|str|None') -> 'datetime|None':
        if datetime is None:
            return None
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp)
        return timestamp

    @property
    def statistics(self) -> Statistics:
        """Execution statistics.

        Statistics are created based on the contained ``suite`` and possible
        :func:`configuration <configure>`.

        Statistics are created every time this property is accessed. Saving
        them to a variable is thus often a good idea to avoid re-creating
        them unnecessarily::

            from robot.api import ExecutionResult

            result = ExecutionResult('output.xml')
            result.configure(stat_config={'suite_stat_level': 2,
                                          'tag_stat_combine': 'tagANDanother'})
            stats = result.statistics
            print(stats.total.failed)
            print(stats.total.passed)
            print(stats.tags.combined[0].total)
        """
        return Statistics(self.suite, rpa=self.rpa, **self._stat_config)

    @property
    def return_code(self) -> int:
        """Execution return code.

        By default, returns the number of failed tests or tasks (max 250),
        but can be :func:`configured <configure>` to always return 0.
        """
        if self._status_rc:
            return min(self.suite.statistics.failed, 250)
        return 0

    @property
    def generated_by_robot(self) -> bool:
        return self.generator.split()[0].upper() == 'ROBOT'

    def configure(self, status_rc=True, suite_config=None, stat_config=None):
        """Configures the result object and objects it contains.

        :param status_rc: If set to ``False``, :attr:`return_code` always
            returns 0.
        :param suite_config: A dictionary of configuration options passed
            to :meth:`~.result.testsuite.TestSuite.configure` method of
            the contained ``suite``.
        :param stat_config: A dictionary of configuration options used when
            creating :attr:`statistics`.
        """
        if suite_config:
            self.suite.configure(**suite_config)
        self._status_rc = status_rc
        self._stat_config = stat_config or {}

    @classmethod
    def from_json(cls, source: 'str|bytes|TextIO|Path',
                  rpa: 'bool|None' = None) -> 'Result':
        """Construct a result object from JSON data.

        The data is given as the ``source`` parameter. It can be:

        - a string (or bytes) containing the data directly,
        - an open file object where to read the data from, or
        - a path (``pathlib.Path`` or string) to a UTF-8 encoded file to read.

        Data can contain either:

        - full result data (contains suite information, execution errors, etc.)
          got, for example, from the :meth:`to_json` method, or
        - only suite information got, for example, from
          :meth:`result.testsuite.TestSuite.to_json <TestSuite.to_json>`.

        :attr:`statistics` are populated automatically based on suite information
        and thus ignored if they are present in the data.

        The ``rpa`` argument can be used to override the RPA mode. The mode is
        got from the data by default.

        New in Robot Framework 7.2.
        """
        try:
            data = JsonLoader().load(source)
        except (TypeError, ValueError) as err:
            raise DataError(f'Loading JSON data failed: {err}')
        if 'suite' in data:
            result = cls._from_full_json(data)
        else:
            result = cls._from_suite_json(data)
        result.rpa = data.get('rpa', False) if rpa is None else rpa
        if isinstance(source, Path):
            result.source = source
        elif isinstance(source, str) and source[0] != '{' and Path(source).exists():
            result.source = Path(source)
        return result

    @classmethod
    def _from_full_json(cls, data) -> 'Result':
        return Result(suite=TestSuite.from_dict(data['suite']),
                      errors=ExecutionErrors(data.get('errors')),
                      generator=data.get('generator'),
                      generation_time=data.get('generated'))

    @classmethod
    def _from_suite_json(cls, data) -> 'Result':
        return Result(suite=TestSuite.from_dict(data))

    @overload
    def to_json(self, file: None = None, *,
                include_statistics: bool = True,
                ensure_ascii: bool = False, indent: int = 0,
                separators: 'tuple[str, str]' = (',', ':')) -> str:
        ...

    @overload
    def to_json(self, file: 'TextIO|Path|str', *,
                include_statistics: bool = True,
                ensure_ascii: bool = False, indent: int = 0,
                separators: 'tuple[str, str]' = (',', ':')) -> None:
        ...

    def to_json(self, file: 'None|TextIO|Path|str' = None, *,
                include_statistics: bool = True,
                ensure_ascii: bool = False, indent: int = 0,
                separators: 'tuple[str, str]' = (',', ':')) -> 'str|None':
        """Serialize results into JSON.

        The ``file`` parameter controls what to do with the resulting JSON data.
        It can be:

        - ``None`` (default) to return the data as a string,
        - an open file object where to write the data to, or
        - a path (``pathlib.Path`` or string) to a file where to write
          the data using UTF-8 encoding.

        The ``include_statistics`` controls including statistics information
        in the resulting JSON data. Statistics are not needed if the serialized
        JSON data is converted back to a ``Result`` object, but they can be
        useful for external tools.

        The remaining optional parameters are used for JSON formatting.
        They are passed directly to the underlying json__ module, but
        the defaults differ from what ``json`` uses.

        New in Robot Framework 7.2.

        __ https://docs.python.org/3/library/json.html
        """
        data = {'generator': get_full_version('Rebot'),
                'generated': datetime.now().isoformat(),
                'rpa': self.rpa,
                'suite': self.suite.to_dict()}
        if include_statistics:
            data['statistics'] = self.statistics.to_dict()
        data['errors'] = self.errors.messages.to_dicts()
        return JsonDumper(ensure_ascii=ensure_ascii, indent=indent,
                          separators=separators).dump(data, file)

    def save(self, target=None, legacy_output=False):
        """Save results as XML or JSON file.

        :param target: Target where to save results to. Can be a path
            (``pathlib.Path`` or ``str``) or an open file object. If omitted,
            uses the :attr:`source` which overwrites the original file.
        :param legacy_output: Save XML results in Robot Framework 6.x compatible
            format. New in Robot Framework 7.0.

        File type is got based on the ``target``. The type is JSON if the ``target``
        is a path that has a ``.json`` suffix or if it is an open file that has
        a ``name`` attribute with a ``.json`` suffix. Otherwise, the type is XML.

        It is also possible to use :meth:`to_json` for JSON serialization. Compared
        to this method, it allows returning the JSON in addition to writing it
        into a file, and it also supports customizing JSON formatting.

        Support for saving results in JSON is new in Robot Framework 7.0.
        Originally only suite information was saved in that case, but starting
        from Robot Framework 7.2, also JSON results contain full result data
        including, for example, execution errors and statistics.
        """
        from robot.reporting.outputwriter import LegacyOutputWriter, OutputWriter

        target = target or self.source
        if not target:
            raise ValueError('Path required.')
        if is_json_source(target):
            self.to_json(target)
        else:
            writer = OutputWriter if not legacy_output else LegacyOutputWriter
            self.visit(writer(target, rpa=self.rpa))

    def visit(self, visitor):
        """An entry point to visit the whole result object.

        :param visitor: An instance of :class:`~.visitor.ResultVisitor`.

        Visitors can gather information, modify results, etc. See
        :mod:`~robot.result` package for a simple usage example.

        Notice that it is also possible to call :meth:`result.suite.visit
        <robot.result.testsuite.TestSuite.visit>` if there is no need to
        visit the contained ``statistics`` or ``errors``.
        """
        visitor.visit_result(self)

    def handle_suite_teardown_failures(self):
        """Internal usage only."""
        if self.generated_by_robot:
            self.suite.handle_suite_teardown_failures()

    def set_execution_mode(self, other):
        """Set execution mode based on other result. Internal usage only."""
        if other.rpa is None:
            pass
        elif self.rpa is None:
            self.rpa = other.rpa
        elif self.rpa is not other.rpa:
            this, that = ('task', 'test') if other.rpa else ('test', 'task')
            raise DataError("Conflicting execution modes. File '%s' has %ss "
                            "but files parsed earlier have %ss. Use '--rpa' "
                            "or '--norpa' options to set the execution mode "
                            "explicitly." % (other.source, this, that))


class CombinedResult(Result):
    """Combined results of multiple test executions."""

    def __init__(self, results=None):
        super().__init__()
        for result in results or ():
            self.add_result(result)

    def add_result(self, other):
        self.set_execution_mode(other)
        self.suite.suites.append(other.suite)
        self.errors.add(other.errors)
