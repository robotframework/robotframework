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
        handler = handler.get_child_handler(elem.tag)
        result = handler.start(elem, result)
        self._stack.append((handler, result))

    def end(self, elem):
        handler, result = self._stack.pop()
        handler.end(elem, result)


class ElementHandler(object):
    element_handlers = {}
    tag = None
    children = frozenset()

    @classmethod
    def register(cls, handler):
        cls.element_handlers[handler.tag] = handler()
        return handler

    def get_child_handler(self, tag):
        if tag not in self.children:
            if not self.tag:
                raise DataError("Incompatible root element '%s'." % tag)
            raise DataError("Incompatible child element '%s' for '%s'."
                            % (tag, self.tag))
        return self.element_handlers[tag]

    def start(self, elem, result):
        return result

    def end(self, elem, result):
        pass

    def _timestamp(self, elem, attr_name):
        timestamp = elem.get(attr_name)
        return timestamp if timestamp != 'N/A' else None


class RootHandler(ElementHandler):
    children = frozenset(('robot',))


@ElementHandler.register
class RobotHandler(ElementHandler):
    tag = 'robot'
    children = frozenset(('suite', 'statistics', 'errors'))

    def start(self, elem, result):
        generator = elem.get('generator', 'unknown').split()[0].upper()
        result.generated_by_robot = generator == 'ROBOT'
        if result.rpa is None:
            result.rpa = elem.get('rpa', 'false') == 'true'
        return result


@ElementHandler.register
class SuiteHandler(ElementHandler):
    tag = 'suite'
    children = frozenset(('doc', 'metadata', 'status', 'kw', 'test', 'suite'))

    def start(self, elem, result):
        if hasattr(result, 'suite'):    # root
            return result.suite.config(name=elem.get('name', ''),
                                       source=elem.get('source'),
                                       rpa=result.rpa)
        return result.suites.create(name=elem.get('name', ''),
                                    source=elem.get('source'),
                                    rpa=result.rpa)

    def get_child_handler(self, tag):
        if tag == 'status':
            return StatusHandler(set_status=False)
        return ElementHandler.get_child_handler(self, tag)


@ElementHandler.register
class TestHandler(ElementHandler):
    tag = 'test'
    children = frozenset(('doc', 'tags', 'timeout', 'status', 'kw', 'if', 'for'))

    def start(self, elem, result):
        return result.tests.create(name=elem.get('name', ''))


@ElementHandler.register
class KeywordHandler(ElementHandler):
    tag = 'kw'
    children = frozenset(('doc', 'arguments', 'assign', 'tags', 'timeout',
                          'status', 'msg', 'kw', 'if', 'for'))

    def start(self, elem, result):
        creator = getattr(self, '_create_%s' % elem.get('type', 'kw'))
        return creator(elem, result)

    def _create_kw(self, elem, result):
        return result.body.create_keyword(kwname=elem.get('name', ''),
                                          libname=elem.get('library', ''))

    def _create_setup(self, elem, result):
        return result.setup.config(kwname=elem.get('name', ''),
                                   libname=elem.get('library', ''))

    def _create_teardown(self, elem, result):
        return result.teardown.config(kwname=elem.get('name', ''),
                                      libname=elem.get('library', ''))


@ElementHandler.register
class ForHandler(ElementHandler):
    tag = 'for'
    children = frozenset(('assign', 'arguments', 'doc', 'status', 'iter', 'msg'))

    def start(self, elem, result):
        return result.body.create_for(flavor=elem.get('flavor'))


@ElementHandler.register
class IterationHandler(ElementHandler):
    tag = 'iter'
    children = frozenset(('doc', 'status', 'kw', 'if', 'for', 'msg'))

    def start(self, elem, result):
        return result.body.create_iteration(info=elem.get('info'))


@ElementHandler.register
class IfHandler(ElementHandler):
    tag = 'if'
    children = frozenset(('status', 'kw', 'if', 'for', 'msg'))

    def start(self, elem, result):
        creator = getattr(self, '_create_%s' % elem.get('type', 'if'))
        return creator(elem, result)

    def _create_if(self, elem, result):
        return result.body.create_if(condition=elem.get('condition'))

    def _create_elseif(self, elem, result):
        return result.orelse.config(condition=elem.get('condition'))

    def _create_else(self, elem, result):
        return result.orelse.config()


@ElementHandler.register
class MessageHandler(ElementHandler):
    tag = 'msg'

    def end(self, elem, result):
        result.body.create_message(elem.text or '',
                                   elem.get('level', 'INFO'),
                                   elem.get('html', 'no') == 'yes',
                                   self._timestamp(elem, 'timestamp'))


@ElementHandler.register
class StatusHandler(ElementHandler):
    tag = 'status'

    def __init__(self, set_status=True):
        self.set_status = set_status

    def end(self, elem, result):
        if self.set_status:
            result.status = elem.get('status', 'FAIL')
        result.starttime = self._timestamp(elem, 'starttime')
        result.endtime = self._timestamp(elem, 'endtime')
        if elem.text:
            result.message = elem.text
        if hasattr(result, 'branch_status'):
            result.branch_status = elem.get('branch')


@ElementHandler.register
class DocHandler(ElementHandler):
    tag = 'doc'

    def end(self, elem, result):
        result.doc = elem.text or ''


@ElementHandler.register
class MetadataHandler(ElementHandler):
    tag = 'metadata'
    children = frozenset(('item',))


@ElementHandler.register
class MetadataItemHandler(ElementHandler):
    tag = 'item'

    def end(self, elem, result):
        result.metadata[elem.get('name', '')] = elem.text or ''


@ElementHandler.register
class TagsHandler(ElementHandler):
    tag = 'tags'
    children = frozenset(('tag',))


@ElementHandler.register
class TagHandler(ElementHandler):
    tag = 'tag'

    def end(self, elem, result):
        result.tags.add(elem.text or '')


@ElementHandler.register
class TimeoutHandler(ElementHandler):
    tag = 'timeout'

    def end(self, elem, result):
        result.timeout = elem.get('value')


@ElementHandler.register
class AssignHandler(ElementHandler):
    tag = 'assign'
    children = frozenset(('var',))


@ElementHandler.register
class AssignVarHandler(ElementHandler):
    tag = 'var'

    def end(self, elem, result):
        # Handles FOR loops and keywords.
        if hasattr(result, 'variables'):
            result.variables += (elem.text or '',)
        else:
            result.assign += (elem.text or '',)


@ElementHandler.register
class ArgumentsHandler(ElementHandler):
    tag = 'arguments'
    children = frozenset(('arg',))


@ElementHandler.register
class ArgumentHandler(ElementHandler):
    tag = 'arg'

    def end(self, elem, result):
        # Handles FOR loops and keywords.
        if hasattr(result, 'values'):
            result.values += (elem.text or '',)
        else:
            result.args += (elem.text or '',)


@ElementHandler.register
class ErrorsHandler(ElementHandler):
    tag = 'errors'

    def start(self, elem, result):
        return result.errors

    def get_child_handler(self, tag):
        return ErrorMessageHandler()


class ErrorMessageHandler(ElementHandler):

    def end(self, elem, result):
        result.messages.create(elem.text or '',
                               elem.get('level', 'INFO'),
                               elem.get('html', 'no') == 'yes',
                               self._timestamp(elem, 'timestamp'))


@ElementHandler.register
class StatisticsHandler(ElementHandler):
    tag = 'statistics'

    def get_child_handler(self, tag):
        return self
