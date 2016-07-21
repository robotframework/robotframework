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

from robot.errors import DataError


class XmlElementHandler(object):

    def __init__(self, execution_result, root_handler=None):
        self._stack = [(root_handler or RootHandler(), execution_result)]

    def start(self, elem):
        handler, result = self._stack[-1]
        handler = handler.get_child_handler(elem)
        result = handler.start(elem, result)
        self._stack.append((handler, result))

    def end(self, elem):
        handler, result = self._stack.pop()
        handler.end(elem, result)


class _Handler(object):

    def __init__(self):
        self._child_handlers = dict((c.tag, c) for c in self._children())

    def _children(self):
        return []

    def get_child_handler(self, elem):
        try:
            return self._child_handlers[elem.tag]
        except KeyError:
            raise DataError("Incompatible XML element '%s'." % elem.tag)

    def start(self, elem, result):
        return result

    def end(self, elem, result):
        pass

    def _timestamp(self, elem, attr_name):
        timestamp = elem.get(attr_name)
        return timestamp if timestamp != 'N/A' else None


class RootHandler(_Handler):

    def _children(self):
        return [RobotHandler()]


class RobotHandler(_Handler):
    tag = 'robot'

    def start(self, elem, result):
        generator = elem.get('generator', 'unknown').split()[0].upper()
        result.generated_by_robot = generator == 'ROBOT'
        return result

    def _children(self):
        return [RootSuiteHandler(), StatisticsHandler(), ErrorsHandler()]


class SuiteHandler(_Handler):
    tag = 'suite'

    def start(self, elem, result):
        return result.suites.create(name=elem.get('name', ''),
                                    source=elem.get('source'))

    def _children(self):
        return [DocHandler(), MetadataHandler(), SuiteStatusHandler(),
                KeywordHandler(), TestCaseHandler(), self]


class RootSuiteHandler(SuiteHandler):

    def start(self, elem, result):
        result.suite.name = elem.get('name', '')
        result.suite.source = elem.get('source')
        return result.suite

    def _children(self):
        return SuiteHandler._children(self)[:-1] + [SuiteHandler()]


class TestCaseHandler(_Handler):
    tag = 'test'

    def start(self, elem, result):
        return result.tests.create(name=elem.get('name', ''))

    def _children(self):
        return [DocHandler(), TagsHandler(), TimeoutHandler(),
                TestStatusHandler(), KeywordHandler()]


class KeywordHandler(_Handler):
    tag = 'kw'

    def start(self, elem, result):
        return result.keywords.create(kwname=elem.get('name', ''),
                                      libname=elem.get('library', ''),
                                      type=elem.get('type', 'kw'))

    def _children(self):
        return [DocHandler(), ArgumentsHandler(), AssignHandler(),
                TagsHandler(), TimeoutHandler(), KeywordStatusHandler(),
                MessageHandler(), self]


class MessageHandler(_Handler):
    tag = 'msg'

    def end(self, elem, result):
        result.messages.create(elem.text or '',
                               elem.get('level', 'INFO'),
                               elem.get('html', 'no') == 'yes',
                               self._timestamp(elem, 'timestamp'))


class _StatusHandler(_Handler):
    tag = 'status'

    def _set_status(self, elem, result):
        result.status = elem.get('status', 'FAIL')

    def _set_message(self, elem, result):
        result.message = elem.text or ''

    def _set_times(self, elem, result):
        result.starttime = self._timestamp(elem, 'starttime')
        result.endtime = self._timestamp(elem, 'endtime')


class KeywordStatusHandler(_StatusHandler):

    def end(self, elem, result):
        self._set_status(elem, result)
        self._set_times(elem, result)
        if result.type == result.TEARDOWN_TYPE:
            self._set_message(elem, result)


class SuiteStatusHandler(_StatusHandler):

    def end(self, elem, result):
        self._set_message(elem, result)
        self._set_times(elem, result)


class TestStatusHandler(_StatusHandler):

    def end(self, elem, result):
        self._set_status(elem, result)
        self._set_message(elem, result)
        self._set_times(elem, result)


class DocHandler(_Handler):
    tag = 'doc'

    def end(self, elem, result):
        result.doc = elem.text or ''


class MetadataHandler(_Handler):
    tag = 'metadata'

    def _children(self):
        return [MetadataItemHandler()]


class MetadataItemHandler(_Handler):
    tag = 'item'

    def end(self, elem, result):
        result.metadata[elem.get('name', '')] = elem.text or ''


class TagsHandler(_Handler):
    tag = 'tags'

    def _children(self):
        return [TagHandler()]


class TagHandler(_Handler):
    tag = 'tag'

    def end(self, elem, result):
        result.tags.add(elem.text or '')


class TimeoutHandler(_Handler):
    tag = 'timeout'

    def end(self, elem, result):
        result.timeout = elem.get('value')


class AssignHandler(_Handler):
    tag = 'assign'

    def _children(self):
        return [AssignVarHandler()]


class AssignVarHandler(_Handler):
    tag = 'var'

    def end(self, elem, result):
        result.assign += (elem.text or '',)


class ArgumentsHandler(_Handler):
    tag = 'arguments'

    def _children(self):
        return [ArgumentHandler()]


class ArgumentHandler(_Handler):
    tag = 'arg'

    def end(self, elem, result):
        result.args += (elem.text or '',)


class ErrorsHandler(_Handler):
    tag = 'errors'

    def start(self, elem, result):
        return result.errors

    def _children(self):
        return [MessageHandler()]


class StatisticsHandler(_Handler):
    tag = 'statistics'

    def get_child_handler(self, elem):
        return self
