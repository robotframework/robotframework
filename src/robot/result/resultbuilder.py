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

from __future__ import with_statement

from robot.errors import DataError
from robot.utils import ET, ETSource, get_error_message

from .xmlelementhandlers import XmlElementHandler
from .executionresult import Result, CombinedResult


def ExecutionResult(*sources, **options):
    """Factory method to constructs :class:`~.executionresult.Result` objects.

    :param sources: Path(s) to output XML file(s).
    :param options: Configuration options passed to
                    :py:class:`~ExecutionResultBuilder` as keyword arguments.
    :returns: :class:`~.executionresult.Result` instance.

    See :mod:`~robot.result` package for a usage example.
    """
    if not sources:
        raise DataError('One or more data source needed.')
    if len(sources) > 1:
        return _combined_result(sources, options)
    return _single_result(sources[0], options)


def _combined_result(sources, options):
    return CombinedResult(ExecutionResult(src, **options) for src in sources)


def _single_result(source, options):
    ets = ETSource(source)
    try:
        return ExecutionResultBuilder(ets, **options).build(Result(source))
    except IOError, err:
        error = err.strerror
    except:
        error = get_error_message()
    raise DataError("Reading XML source '%s' failed: %s" % (unicode(ets), error))


class ExecutionResultBuilder(object):

    def __init__(self, source, include_keywords=True):
        """Builds :class:`~.executionresult.Result` objects from existing
        output XML files on the file system.

        :param source: Path to output XML file.
        :param include_keywords: Include keyword information to the
            :class:`~.executionresult.Result` objects
        """
        self._source = source \
            if isinstance(source, ETSource) else ETSource(source)
        self._include_keywords = include_keywords

    def build(self, result):
        # Parsing is performance optimized. Do not change without profiling!
        handler = XmlElementHandler(result)
        with self._source as source:
            self._parse(source, handler.start, handler.end)
        result.handle_suite_teardown_failures()
        return result

    def _parse(self, source, start, end):
        context = ET.iterparse(source, events=('start', 'end'))
        if not self._include_keywords:
            context = self._omit_keywords(context)
        for event, elem in context:
            if event == 'start':
                start(elem)
            else:
                end(elem)
                elem.clear()

    def _omit_keywords(self, context):
        started_kws = 0
        for event, elem in context:
            start = event == 'start'
            kw = elem.tag == 'kw'
            if kw and start:
                started_kws += 1
            if not started_kws:
                yield event, elem
            elif not start:
                elem.clear()
            if kw and not start:
                started_kws -= 1
