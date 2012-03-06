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

from __future__ import with_statement

from robot.errors import DataError
from robot.utils import ET, ETSource

from .suiteteardownfailed import SuiteTeardownFailureHandler
from .xmlelementhandlers import XmlElementHandler
from .executionresult import Result, CombinedResult


def ExecutionResult(*sources):
    """Constructs :class:`Result` object based on execution result xml file(s).

    :param sources: The Robot Framework output xml file(s).
    """
    if not sources:
        raise DataError('One or more data source needed.')
    if len(sources) > 1:
        return CombinedResult(*[ExecutionResult(src) for src in sources])
    source = ETSource(sources[0])
    try:
        return ExecutionResultBuilder(source).build(Result(sources[0]))
    except DataError, err:
        raise DataError("Reading XML source '%s' failed: %s"
                        % (unicode(source), unicode(err)))


class ExecutionResultBuilder(object):

    def __init__(self, source):
        self._source = source \
            if isinstance(source, ETSource) else ETSource(source)

    def build(self, result):
        handler = XmlElementHandler(result)
        # Faster attribute lookup inside for loop
        start, end = handler.start, handler.end
        with self._source as source:
            for event, elem in ET.iterparse(source, events=('start', 'end')):
                start(elem) if event == 'start' else end(elem)
        SuiteTeardownFailureHandler(result.generator).visit_suite(result.suite)
        return result
