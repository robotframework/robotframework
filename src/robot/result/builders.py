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

from model import TestSuite
from robot.utils.etreewrapper import ET


class ExecutionResult(object):

    def __init__(self, source):
        self.suite = SuiteBuilder(source).build()
        self.errors = []
        self._statistics = None


class SuiteBuilder(object):

    def __init__(self, source):
        self._source = source
        self._result = TestSuite()
        self._elements = _ElementStack(self._result)

    def build(self):
        _actions = {'start': self._start, 'end': self._end}
        for action, elem in ET.iterparse(self._source, events=('start', 'end')):
            _actions[action](elem)
        return self._result

    def _start(self, elem):
        self._elements.start(elem)

    def _end(self, elem):
        self._elements.end(elem)
        elem.clear()


class _ElementStack(object):

    def __init__(self, initial_result):
        self._current = RootElement(initial_result)

    def start(self, elem):
        self._current = self._current.child_element(elem.tag)
        self._current.start(elem)

    def end(self, elem):
        self._current.end(elem)
        self._current = self._current.parent


class _Element(object):
    tag = ''

    def __init__(self, result, parent=None):
        self.parent = parent
        self._result = result

    def start(self, elem):
        pass

    def end(self, elem):
        pass

    def child_element(self, tag):
        for child_type in self._children():
            if child_type.tag == tag:
                return child_type(self._result, self)
        raise RuntimeError('no child (%s) of mine (%s)', tag, self.tag)

    def _children(self):
        return []

    def _attribute_from(self, elem, name, default=''):
        return elem.attrib.get(name, default)

    def _name_from(self, elem):
        return self._attribute_from(elem, 'name')


class RootElement(_Element):

    def _children(self):
        return [RobotElement]


class RobotElement(_Element):
    tag = 'robot'

    def _children(self):
        return [SuiteElement, StatisticsElement, ErrorsElement]


class SuiteElement(_Element):
    tag = 'suite'

    def end(self, elem):
        self._result.name = self._name_from(elem)
        self._result.source = self._attribute_from(elem, 'source')

    def _children(self):
        return [SuiteElement, DocElement, StatusElement,
                KeywordElement, TestCaseElement, MetadataElement]


class TestCaseElement(_Element):
    tag = 'test'

    def start(self, elem):
        self._result = self._result.create_test(self._name_from(elem))

    def _children(self):
        return [KeywordElement, TagsElement, DocElement, TestStatusElement]


class KeywordElement(_Element):
    tag = 'kw'

    def start(self, elem):
        self._result = self._result.create_keyword(self._name_from(elem))

    def _children(self):
        return [DocElement, ArgumentsElement, KeywordElement, MessageElement,
                StatusElement]


class MessageElement(_Element):
    tag = 'msg'

    def start(self, elem):
        self._result = self._result.create_message()

    def end(self, elem):
        self._result.message = elem.text or ''
        self._result.level = self._attribute_from(elem, 'level')
        self._result.timestamp = self._attribute_from(elem, 'timestamp')
        self._result.html = self._attribute_from(elem, 'html', False)
        self._result.linkable = self._attribute_from(elem, 'html', False)


class StatusElement(_Element):
    tag = 'status'

    def end(self, elem):
        self._result.status = self._attribute_from(elem, 'status')
        self._result.starttime = self._attribute_from(elem, 'starttime')
        self._result.endtime = self._attribute_from(elem, 'endtime')

class TestStatusElement(StatusElement):

    def end(self, elem):
        StatusElement.end(self, elem)
        self._result.critical = self._attribute_from(elem, 'critical') == 'yes'


class DocElement(_Element):
    tag = 'doc'

    def end(self, elem):
        self._result.doc = elem.text or ''


class MetadataElement(_Element):
    tag = 'metadata'

    def _children(self):
        return [MetadataItemElement]

class MetadataItemElement(_Element):
    tag = 'item'

    def _children(self):
        return [MetadataItemElement]

    def end(self, elem):
        self._result.metadata[self._name_from(elem)] = elem.text


class TagsElement(_Element):
    tag = 'tags'

    def _children(self):
        return [TagElement]

class TagElement(_Element):
    tag = 'tag'

    def end(self, elem):
        self._result.tags.add(elem.text)


class ArgumentsElement(_Element):
    tag = 'arguments'

    def _children(self):
        return [ArgumentElement]

class ArgumentElement(_Element):
    tag = 'arg'

    def end(self, elem):
        self._result.args.append(elem.text)


class StatisticsElement(_Element):
    tag = 'statistics'

    def _children(self):
        return [TotalStatisticsElement, TagStatisticsElement,
                SuiteStatisticsElement]

class TotalStatisticsElement(_Element):
    tag = 'total'

    def _children(self):
        return [StatElement]

class TagStatisticsElement(_Element):
    tag = 'tag'

    def _children(self):
        return [StatElement]

class SuiteStatisticsElement(_Element):
    tag = 'suite'

    def _children(self):
        return [StatElement]

class StatElement(_Element):
    tag = 'stat'


class ErrorsElement(_Element):
    tag = 'errors'
