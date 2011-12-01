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

from robot.errors import DataError


class XmlElementHandler(object):

    def __init__(self, result, root_handler=None):
        self._stack = [(root_handler or RootHandler(), result)]

    def start(self, elem):
        handler, result = self._stack[-1]
        self._stack.append(handler.handle_child(elem, result))

    def end(self, elem):
        handler, result = self._stack.pop()
        handler.end(elem, result)
        elem.clear()


class _Handler(object):

    def __init__(self):
        self._children = dict((c.tag, c) for c in self._child_handlers())

    def _child_handlers(self):
        for child_class in self._child_classes():
            yield child_class() if type(self) is not child_class else self

    def _child_classes(self):
        return []

    def handle_child(self, elem, result):
        try:
            handler = self._children[elem.tag]
        except KeyError:
            raise DataError("Incompatible XML element '%s'" % elem.tag)
        else:
            return handler, handler.start(elem, result)

    def start(self, elem, result):
        return result

    def end(self, elem, result):
        pass


class RootHandler(_Handler):

    def _child_classes(self):
        return [RobotHandler]


class RobotHandler(_Handler):
    tag = 'robot'

    def start(self, elem, result):
        result.generator = elem.get('generator', 'unknown').split()[0].upper()
        return result

    def _child_classes(self):
        return [RootSuiteHandler, StatisticsHandler, ErrorsHandler]


class SuiteHandler(_Handler):
    tag = 'suite'

    def start(self, elem, result):
        return result.suites.create(name=elem.get('name'),
                                    source=elem.get('source'))

    def _child_classes(self):
        return [SuiteHandler, DocHandler, SuiteStatusHandler,
                KeywordHandler, TestCaseHandler, MetadataHandler]


class RootSuiteHandler(SuiteHandler):

    def start(self, elem, result):
        result.suite.name = elem.get('name')
        result.suite.source = elem.get('source')
        return result.suite


class TestCaseHandler(_Handler):
    tag = 'test'

    def start(self, elem, result):
        return result.tests.create(name=elem.get('name'),
                                   timeout=elem.get('timeout'))

    def _child_classes(self):
        return [KeywordHandler, TagsHandler, DocHandler, TestStatusHandler]


class KeywordHandler(_Handler):
    tag = 'kw'

    def start(self, elem, result):
        return result.keywords.create(name=elem.get('name'),
                                      timeout=elem.get('timeout'),
                                      type=elem.get('type'))

    def _child_classes(self):
        return [DocHandler, ArgumentsHandler, KeywordHandler, MessageHandler,
                KeywordStatusHandler]


class MessageHandler(_Handler):
    tag = 'msg'

    def end(self, elem, result):
        result.messages.create(elem.text or '',
                               elem.get('level'),
                               elem.get('html', 'no') == 'yes',
                               elem.get('timestamp'),
                               elem.get('linkable', 'no') == 'yes')


class _StatusHandler(_Handler):
    tag = 'status'

    def _set_status(self, elem, result):
        result.status = elem.get('status', 'FAIL')

    def _set_message(self, elem, result):
        result.message = elem.text or ''

    def _set_times(self, elem, result):
        result.starttime = elem.get('starttime', 'N/A')
        result.endtime = elem.get('endtime', 'N/A')


class KeywordStatusHandler(_StatusHandler):

    def end(self, elem, result):
        self._set_status(elem, result)
        self._set_times(elem, result)


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

    def _child_classes(self):
        return [MetadataItemHandler]


class MetadataItemHandler(_Handler):
    tag = 'item'

    def _child_classes(self):
        return [MetadataItemHandler]

    def end(self, elem, result):
        result.metadata[elem.get('name')] = elem.text or ''


class TagsHandler(_Handler):
    tag = 'tags'

    def _child_classes(self):
        return [TagHandler]


class TagHandler(_Handler):
    tag = 'tag'

    def end(self, elem, result):
        result.tags.add(elem.text or '')


class ArgumentsHandler(_Handler):
    tag = 'arguments'

    def _child_classes(self):
        return [ArgumentHandler]


class ArgumentHandler(_Handler):
    tag = 'arg'

    def end(self, elem, result):
        result.args.append(elem.text or '')


class ErrorsHandler(_Handler):
    tag = 'errors'

    def start(self, elem, result):
        return result.errors

    def _child_classes(self):
        return [MessageHandler]


class StatisticsHandler(_Handler):
    tag = 'statistics'

    def handle_child(self, elem, result):
        return self, result
