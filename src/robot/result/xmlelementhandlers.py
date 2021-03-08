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
    # 'metadata' is for RF < 4 compatibility.
    children = frozenset(('doc', 'metadata', 'meta', 'status', 'kw', 'test', 'suite'))

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
    # 'tags' is for RF < 4 compatibility.
    children = frozenset(('doc', 'tags', 'tag', 'timeout', 'status', 'kw', 'if', 'for',
                          'msg'))

    def start(self, elem, result):
        return result.tests.create(name=elem.get('name', ''))


@ElementHandler.register
class KeywordHandler(ElementHandler):
    tag = 'kw'
    # 'arguments', 'assign' and 'tags' are for RF < 4 compatibility.
    children = frozenset(('doc', 'arguments', 'arg', 'assign', 'var', 'tags', 'tag',
                          'timeout', 'status', 'msg', 'kw', 'if', 'for'))

    def start(self, elem, result):
        elem_type = elem.get('type')
        if not elem_type:
            creator = self._create_keyword
        else:
            creator = getattr(self, '_create_%s' % elem_type.lower().replace(' ', '_'))
        return creator(elem, result)

    def _create_keyword(self, elem, result):
        return result.body.create_keyword(kwname=elem.get('name', ''),
                                          libname=elem.get('library'))

    def _create_setup(self, elem, result):
        return result.setup.config(kwname=elem.get('name', ''),
                                   libname=elem.get('library'))

    def _create_teardown(self, elem, result):
        return result.teardown.config(kwname=elem.get('name', ''),
                                      libname=elem.get('library'))

    # RF < 4 compatibility.

    def _create_for(self, elem, result):
        return result.body.create_keyword(kwname=elem.get('name'), type='FOR')

    def _create_foritem(self, elem, result):
        return result.body.create_keyword(kwname=elem.get('name'), type='FOR ITERATION')

    _create_for_iteration = _create_foritem


@ElementHandler.register
class ForHandler(ElementHandler):
    tag = 'for'
    children = frozenset(('var', 'value', 'doc', 'status', 'iter', 'msg'))

    def start(self, elem, result):
        return result.body.create_for(flavor=elem.get('flavor'))


@ElementHandler.register
class ForIterationHandler(ElementHandler):
    tag = 'iter'
    children = frozenset(('var', 'doc', 'status', 'kw', 'if', 'for', 'msg'))

    def start(self, elem, result):
        return result.body.create_iteration()


@ElementHandler.register
class IfHandler(ElementHandler):
    tag = 'if'
    children = frozenset(('status', 'branch', 'msg'))

    def start(self, elem, result):
        return result.body.create_if()


@ElementHandler.register
class IfBranchHandler(ElementHandler):
    tag = 'branch'
    children = frozenset(('status', 'kw', 'if', 'for', 'msg'))

    def start(self, elem, result):
        return result.body.create_branch(elem.get('type'), elem.get('condition'))


@ElementHandler.register
class MessageHandler(ElementHandler):
    tag = 'msg'

    def end(self, elem, result):
        html_true = ('true', 'yes')    # 'yes' is compatibility for RF < 4.
        result.body.create_message(elem.text or '',
                                   elem.get('level', 'INFO'),
                                   elem.get('html') in html_true,
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


@ElementHandler.register
class DocHandler(ElementHandler):
    tag = 'doc'

    def end(self, elem, result):
        result.doc = elem.text or ''


@ElementHandler.register
class MetadataHandler(ElementHandler):   # RF < 4 compatibility.
    tag = 'metadata'
    children = frozenset(('item',))


@ElementHandler.register
class MetadataItemHandler(ElementHandler):    # RF < 4 compatibility.
    tag = 'item'

    def end(self, elem, result):
        result.metadata[elem.get('name', '')] = elem.text or ''


@ElementHandler.register
class MetaHandler(ElementHandler):
    tag = 'meta'

    def end(self, elem, result):
        result.metadata[elem.get('name', '')] = elem.text or ''


@ElementHandler.register
class TagsHandler(ElementHandler):    # RF < 4 compatibility.
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
class AssignHandler(ElementHandler):    # RF < 4 compatibility.
    tag = 'assign'
    children = frozenset(('var',))


@ElementHandler.register
class VarHandler(ElementHandler):
    tag = 'var'

    def end(self, elem, result):
        value = elem.text or ''
        if result.type == result.KEYWORD:
            result.assign += (value,)
        elif result.type == result.FOR:
            result.variables += (value,)
        elif result.type == result.FOR_ITERATION:
            result.variables[elem.get('name')] = value
        else:
            raise DataError("Invalid element '%s' for result '%r'." % (elem, result))


@ElementHandler.register
class ArgumentsHandler(ElementHandler):    # RF < 4 compatibility.
    tag = 'arguments'
    children = frozenset(('arg',))


@ElementHandler.register
class ArgumentHandler(ElementHandler):
    tag = 'arg'

    def end(self, elem, result):
        result.args += (elem.text or '',)


@ElementHandler.register
class ValueHandler(ElementHandler):
    tag = 'value'

    def end(self, elem, result):
        result.values += (elem.text or '',)


@ElementHandler.register
class ErrorsHandler(ElementHandler):
    tag = 'errors'

    def start(self, elem, result):
        return result.errors

    def get_child_handler(self, tag):
        return ErrorMessageHandler()


class ErrorMessageHandler(ElementHandler):

    def end(self, elem, result):
        html_true = ('true', 'yes')    # 'yes' is compatibility for RF < 4.
        result.messages.create(elem.text or '',
                               elem.get('level', 'INFO'),
                               elem.get('html') in html_true,
                               self._timestamp(elem, 'timestamp'))


@ElementHandler.register
class StatisticsHandler(ElementHandler):
    tag = 'statistics'

    def get_child_handler(self, tag):
        return self
