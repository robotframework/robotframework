#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

import os

from robot.errors import DataError
from robot.utils.etreewrapper import ET
from robot import utils

from model import ExecutionResult, CombinedExecutionResult
from suiteteardownfailed import SuiteTeardownFailureHandler


def ResultFromXML(*sources):
    if not sources:
        raise DataError('One or more data source needed.')
    if len(sources) > 1:
        return CombinedExecutionResult(*[ResultFromXML(src) for src in sources])
    source = sources[0]
    _validate_source(source)
    try:
        return ExecutionResultBuilder(source).build(ExecutionResult())
    # TODO: handle source in errors messages when it's a file object
    except DataError:
        raise DataError("File '%s' is not Robot Framework output file." % source)
    except:
        raise DataError("Opening XML file '%s' failed: %s"
                        % (source, utils.get_error_message()))

def _validate_source(source):
    # TODO: add support for xml strings.
    if isinstance(source, basestring) and not os.path.isfile(source):
        raise DataError("Output file '%s' does not exist." % source)


class ExecutionResultBuilder(object):

    def __init__(self, source):
        self._source = source

    def build(self, result):
        elements = ElementStack(RootElement())
        for action, elem in ET.iterparse(self._source, events=('start', 'end')):
            result = getattr(elements, action)(elem, result)
        SuiteTeardownFailureHandler(result.generator).visit_suite(result.suite)
        return result


class ElementStack(object):

    def __init__(self, root_element):
        self._elements = [root_element]

    @property
    def _current(self):
        return self._elements[-1]

    def start(self, elem, result):
        self._elements.append(self._current.child_element(elem.tag))
        return self._current.start(elem, result)

    def end(self, elem, result):
        result = self._current.end(elem, result)
        elem.clear()
        self._elements.pop()
        return result


class _Element(object):
    tag = ''

    def start(self, elem, result):
        return result

    def end(self, elem, result):
        return result

    def child_element(self, tag):
        # TODO: replace _children() list with dict
        for child_type in self._children():
            if child_type.tag == tag:
                return child_type()
        raise DataError("Unexpected element '%s'" % tag)

    def _children(self):
        return []


class _CollectionElement(_Element):

    def end(self, elem, result):
        return result.parent


class RootElement(_Element):

    def _children(self):
        return [RobotElement]


class RobotElement(_Element):
    tag = 'robot'

    def start(self, elem, result):
        result.generator = elem.get('generator', 'unknown').split()[0].upper()
        return result

    def _children(self):
        return [RootSuiteElement, StatisticsElement, ErrorsElement]


class SuiteElement(_CollectionElement):
    tag = 'suite'

    def start(self, elem, result):
        return result.suites.create(name=elem.get('name'),
                                    source=elem.get('source'))

    def _children(self):
        return [SuiteElement, DocElement, SuiteStatusElement,
                KeywordElement, TestCaseElement, MetadataElement]


class RootSuiteElement(SuiteElement):

    def start(self, elem, result):
        self._result = result
        self._result.suite.name = elem.get('name')
        self._result.suite.source = elem.get('source')
        return self._result.suite

    def end(self, elem, result):
        return self._result


class TestCaseElement(_CollectionElement):
    tag = 'test'

    def start(self, elem, result):
        return result.tests.create(name=elem.get('name'),
                                   timeout=elem.get('timeout'))

    def _children(self):
        return [KeywordElement, TagsElement, DocElement, TestStatusElement]


class KeywordElement(_CollectionElement):
    tag = 'kw'

    def start(self, elem, result):
        return result.keywords.create(name=elem.get('name'),
                                      timeout=elem.get('timeout'),
                                      type=elem.get('type'))

    def _children(self):
        return [DocElement, ArgumentsElement, KeywordElement, MessageElement,
                KeywordStatusElement]


class MessageElement(_Element):
    tag = 'msg'

    def end(self, elem, result):
        html = elem.get('html', 'no') == 'yes'
        linkable = elem.get('linkable', 'no') == 'yes'
        result.messages.create(elem.text or '', elem.get('level'),
                               html, elem.get('timestamp'), linkable)
        return result


class _StatusElement(_Element):
    tag = 'status'

    # TODO: Could elements handle default values themselves?

    def _set_status(self, elem, result):
        result.status = elem.get('status', 'FAIL').upper()

    def _set_message(self, elem, result):
        result.message = elem.text or ''

    def _set_times(self, elem, result):
        result.starttime = elem.get('starttime', 'N/A')
        result.endtime = elem.get('endtime', 'N/A')


class KeywordStatusElement(_StatusElement):

    def end(self, elem, result):
        self._set_status(elem, result)
        self._set_times(elem, result)
        return result


class SuiteStatusElement(_StatusElement):

    def end(self, elem, result):
        self._set_message(elem, result)
        self._set_times(elem, result)
        return result


class TestStatusElement(_StatusElement):

    def end(self, elem, result):
        self._set_status(elem, result)
        self._set_criticality(elem, result)
        self._set_message(elem, result)
        self._set_times(elem, result)
        return result

    def _set_criticality(self, elem, result):
        result._critical = elem.get('critical', 'yes')


class DocElement(_Element):
    tag = 'doc'

    def end(self, elem, result):
        result.doc = elem.text or ''
        return result


class MetadataElement(_Element):
    tag = 'metadata'

    def _children(self):
        return [MetadataItemElement]


class MetadataItemElement(_Element):
    tag = 'item'

    def _children(self):
        return [MetadataItemElement]

    def end(self, elem, result):
        result.metadata[elem.get('name')] = elem.text
        return result


class TagsElement(_Element):
    tag = 'tags'

    def _children(self):
        return [TagElement]


class TagElement(_Element):
    tag = 'tag'

    def end(self, elem, result):
        result.tags.add(elem.text)
        return result


class ArgumentsElement(_Element):
    tag = 'arguments'

    def _children(self):
        return [ArgumentElement]


class ArgumentElement(_Element):
    tag = 'arg'

    def end(self, elem, result):
        result.args.append(elem.text)
        return result


class ErrorsElement(_Element):
    tag = 'errors'

    def start(self, elem, result):
        self._result = result
        return self._result.errors

    def end(self, elem, result):
        return self._result

    def _children(self):
        return [MessageElement]


class StatisticsElement(_Element):
    tag = 'statistics'

    def child_element(self, tag):
        return self
