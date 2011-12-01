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


class XmlHandler(object):

    def __init__(self, result, root_handler=None):
        self._results = [result]
        self._handlers = [root_handler or RootHandler()]

    @property
    def _result(self):
        return self._results[-1]

    @property
    def _handler(self):
        return self._handlers[-1]

    def start(self, elem):
        self._handlers.append(self._handler.child_handler(elem.tag))
        self._results.append(self._handler.start(elem, self._result))

    def end(self, elem):
        self._handlers.pop().end(elem, self._results.pop())
        elem.clear()


class _Handler(object):
    tag = ''

    def start(self, elem, result):
        return result

    def end(self, elem, result):
        pass

    def child_handler(self, tag):
        # TODO: replace _children() list with dict
        for child_type in self._children():
            if child_type.tag == tag:
                return child_type()
        raise DataError("Incompatible XML handler '%s'" % tag)

    def _children(self):
        return []


class RootHandler(_Handler):

    def _children(self):
        return [RobotHandler]


class RobotHandler(_Handler):
    tag = 'robot'

    def start(self, elem, result):
        result.generator = elem.get('generator', 'unknown').split()[0].upper()
        return result

    def _children(self):
        return [RootSuiteHandler, StatisticsHandler, ErrorsHandler]


class SuiteHandler(_Handler):
    tag = 'suite'

    def start(self, elem, result):
        return result.suites.create(name=elem.get('name'),
                                    source=elem.get('source'))

    def _children(self):
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

    def _children(self):
        return [KeywordHandler, TagsHandler, DocHandler, TestStatusHandler]


class KeywordHandler(_Handler):
    tag = 'kw'

    def start(self, elem, result):
        return result.keywords.create(name=elem.get('name'),
                                      timeout=elem.get('timeout'),
                                      type=elem.get('type'))

    def _children(self):
        return [DocHandler, ArgumentsHandler, KeywordHandler, MessageHandler,
                KeywordStatusHandler]


class MessageHandler(_Handler):
    tag = 'msg'

    def end(self, elem, result):
        html = elem.get('html', 'no') == 'yes'
        linkable = elem.get('linkable', 'no') == 'yes'
        result.messages.create(elem.text or '', elem.get('level'),
                               html, elem.get('timestamp'), linkable)


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

    def _children(self):
        return [MetadataItemHandler]


class MetadataItemHandler(_Handler):
    tag = 'item'

    def _children(self):
        return [MetadataItemHandler]

    def end(self, elem, result):
        result.metadata[elem.get('name')] = elem.text or ''


class TagsHandler(_Handler):
    tag = 'tags'

    def _children(self):
        return [TagHandler]


class TagHandler(_Handler):
    tag = 'tag'

    def end(self, elem, result):
        result.tags.add(elem.text or '')


class ArgumentsHandler(_Handler):
    tag = 'arguments'

    def _children(self):
        return [ArgumentHandler]


class ArgumentHandler(_Handler):
    tag = 'arg'

    def end(self, elem, result):
        result.args.append(elem.text or '')


class ErrorsHandler(_Handler):
    tag = 'errors'

    def start(self, elem, result):
        return result.errors

    def _children(self):
        return [MessageHandler]


class StatisticsHandler(_Handler):
    tag = 'statistics'

    def child_handler(self, tag):
        return self
