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
from .model import TestSuite

class JsonElementHandler(object):

    def __init__(self, execution_result):
        self._result = execution_result

    def parse(self, json_data):
        parse_robot(json_data, self._result)


def parse_robot(root_element, result):
    ElementHandler.element_handlers.get('robot').parse(root_element, result)


class ElementHandler(object):
    element_handlers = {}
    list_children = frozenset()
    children = frozenset()

    @classmethod
    def register(cls, handler):
        # Because JSON differentiates between lists and single
        # objects some handlers will have multiple tags
        for tag in handler.tags:
            cls.element_handlers[tag] = handler()
        return handler

    def parse(self, elem, result):
        handler_result = self.start(elem, result)
        for child_list in self.list_children:
            if child_list not in elem:
                continue
            for child in elem[child_list]:
                self.element_handlers[child_list].parse(child, handler_result)
        for child in self.children:
            if child not in elem:
                continue
            self.element_handlers[child].parse(elem[child], handler_result)
        self.end(elem, handler_result)
        

    def start(self, elem, result):
        return result

    def end(self, elem, result):
        pass

    def _timestamp(self, elem, attr_name):
        timestamp = elem.get(attr_name)
        return timestamp if timestamp != 'N/A' else None


@ElementHandler.register
class RobotHandler(ElementHandler):
    tags = ['robot']
    children = frozenset(('suite', 'statistics', 'errors'))

    def start(self, elem, result):
        generator = elem.get('generator', 'unknown').split()[0].upper()
        result.generated_by_robot = generator == 'ROBOT'
        if result.rpa is None:
            result.rpa = elem.get('rpa', 'false') == 'true'
        return result


@ElementHandler.register
class SuiteHandler(ElementHandler):
    tags = ['suite', 'suites']
    list_children = frozenset(('kw', 'tests', 'suites'))
    children = frozenset(('doc', 'metadata', 'status', 'setup', 'teardown'))

    def start(self, elem, result):
        if hasattr(result, 'suite'):    # root
            return result.suite.config(name=elem.get('name', ''),
                                       source=elem.get('source'),
                                       rpa=result.rpa)
        return result.suites.create(name=elem.get('name', ''),
                                    source=elem.get('source'),
                                    rpa=result.rpa)


@ElementHandler.register
class TestHandler(ElementHandler):
    tags = ['tests']
    list_children = frozenset(('body', 'tags'))
    children = frozenset(('doc', 'timeout', 'status', 'msg', 'setup', 'teardown'))

    def start(self, elem, result):
        return result.tests.create(name=elem.get('name', ''))


@ElementHandler.register
class KeywordHandler(ElementHandler):
    tags = ['kw', 'teardown', 'setup']
    # 'arguments', 'assign' and 'tags' are for RF < 4 compatibility.
    list_children = frozenset(('body', 'msgs', 'tags', 'args', 'var'))
    children = frozenset(('doc', 'timeout', 'status', 'teardown'))

    def start(self, elem, result):
        elem_type = elem.get('type')
        if not elem_type:
            creator = self._create_keyword
        else:
            creator = getattr(self, '_create_%s' % elem_type.lower().replace(' ', '_'))
        return creator(elem, result)

    def _create_keyword(self, elem, result):
        return result.body.create_keyword(kwname=elem.get('name', ''),
                                          libname=elem.get('lib'))

    def _create_setup(self, elem, result):
        return result.setup.config(kwname=elem.get('name', ''),
                                   libname=elem.get('lib'))

    def _create_teardown(self, elem, result):
        return result.teardown.config(kwname=elem.get('name', ''),
                                      libname=elem.get('lib'))

    # RF < 4 compatibility.

    def _create_for(self, elem, result):
        return result.body.create_keyword(kwname=elem.get('name'), type='FOR')

    def _create_foritem(self, elem, result):
        return result.body.create_keyword(kwname=elem.get('name'), type='FOR ITERATION')

    _create_for_iteration = _create_foritem


@ElementHandler.register
class BodyHandler(ElementHandler):
    tags = ['body']

    def parse(self, elem, result):
        body_type = elem['type'] if 'type' in elem else 'KW'
        if body_type == 'KW':
            self.element_handlers['kw'].parse(elem, result)
        elif body_type == 'FOR':
            self.element_handlers['for'].parse(elem, result)
        elif body_type == 'IF/ELSE ROOT':
            self.element_handlers['if'].parse(elem, result)
        elif body_type == 'MESSAGE':
            self.element_handlers['msg'].parse(elem, result)


@ElementHandler.register
class ForHandler(ElementHandler):
    tags = ['for']
    list_children = frozenset(('iter', 'var', 'value', 'msgs'))
    children = frozenset(('doc', 'status'))

    def start(self, elem, result):
        return result.body.create_for(flavor=elem.get('flavor'))


@ElementHandler.register
class ForIterationHandler(ElementHandler):
    tags = ['iter']
    list_children = frozenset(('body', 'msgs'))
    children = frozenset(('doc', 'status', 'var'))

    def start(self, elem, result):
        return result.body.create_iteration()


@ElementHandler.register
class IfHandler(ElementHandler):
    tags = ['if']
    list_children = frozenset(('branches', 'msgs'))
    children = frozenset(('status', 'msg'))

    def start(self, elem, result):
        return result.body.create_if()


@ElementHandler.register
class IfBranchHandler(ElementHandler):
    tags = ['branch', 'branches']
    list_children = frozenset(('body', 'msgs'))
    children = frozenset(('status', 'msg'))

    def start(self, elem, result):
        return result.body.create_branch(elem.get('type'), elem.get('condition'))


@ElementHandler.register
class MessageHandler(ElementHandler):
    tags = ['msg', 'msgs']

    def end(self, elem, result):
        html_true = ('true', 'yes')    # 'yes' is compatibility for RF < 4.
        result.body.create_message(elem.get('msg', ''),
                                   elem.get('level', 'INFO'),
                                   elem.get('html') in html_true,
                                   self._timestamp(elem, 'timestamp'))


@ElementHandler.register
class StatusHandler(ElementHandler):
    tags = ['status']

    def end(self, elem, result):
        if not isinstance(result, TestSuite):
            result.status = elem.get('status', 'FAIL')
        result.starttime = self._timestamp(elem, 'starttime')
        result.endtime = self._timestamp(elem, 'endtime')
        message = elem.get('msg')
        if message:
            result.message = message


@ElementHandler.register
class DocHandler(ElementHandler):
    tags = ['doc']

    def end(self, elem, result):
        result.doc = elem or ''


@ElementHandler.register
class MetaHandler(ElementHandler):
    tags = ['metadata']

    def end(self, elem, result):
        result.metadata[elem.get('name', '')] = elem.get('value', '')


@ElementHandler.register
class TagHandler(ElementHandler):
    tags = ['tag', 'tags']

    def end(self, elem, result):
        result.tags.add(elem or '')


@ElementHandler.register
class TimeoutHandler(ElementHandler):
    tags = ['timeout']

    def end(self, elem, result):
        result.timeout = elem


@ElementHandler.register
class VarHandler(ElementHandler):
    tags = ['var', 'vars']

    def end(self, elem, result):
        if result.type == result.KEYWORD:
            result.assign += (elem,)
        elif result.type == result.FOR:
            result.variables += (elem,)
        elif result.type == result.FOR_ITERATION:
            for name, value in elem.items():
                result.variables[name] = value
        else:
            raise DataError("Invalid element '%s' for result '%r'." % (elem, result))


@ElementHandler.register
class ArgumentHandler(ElementHandler):
    tags = ['arg', 'args']

    def end(self, elem, result):
        result.args += (elem or '',)


@ElementHandler.register
class ValueHandler(ElementHandler):
    tags = ['value']

    def end(self, elem, result):
        result.values += (elem or '',)


@ElementHandler.register
class ErrorsHandler(ElementHandler):
    tags = ['errors']

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
    tags = ['statistics']

    def get_child_handler(self, tag):
        return self



# def parse_root_suite(suite_element, result):
#     result.suite.name = suite_element.get('name', '')
#     result.suite.source = suite_element.get('source')
#     result.suite.rpa = result.rpa
#     result.suite.doc = suite_element.get('doc', '')

#     for suite in suite_element.get('suites', []):
#         parse_suite(suite, result.suite)
#     for element in suite_element.get('tests', []):
#         parse_test(element, result.suite)
#     for element in suite_element.get('kw', []):
#         if element['type'] == "SETUP":
#             parse_keyword(element, result.setup)
#         elif element['type'] == "TEARDOWN":
#             parse_keyword(element, result.teardown)

#     parse_metadata(suite_element.get('metadata', None), result.suite)
#     parse_status(suite_element.get('status', None), result.suite, "suite")


# def parse_suite(suite_element, result):
#     if not suite_element:
#         return
#     try:
#         suite = result.suites.create(name=suite_element.get('name', ''),
#                                      source=suite_element.get('source', ''),
#                                      rpa=result.rpa)
#     except Exception as e:
#         print(e)
#     suite.doc = suite_element.get('doc', '')
#     parse_metadata(suite_element.get('metadata', None), suite)
#     parse_status(suite_element.get('status', None), suite, "suite")
#     for element in suite_element.get('suites', []):
#         parse_suite(element, suite)
#     for element in suite_element.get('tests', []):
#         parse_test(element, suite)
#     for element in suite_element.get('kw', []):
#         parse_keyword(element, suite)


# def parse_metadata(metadata_element, result):
#     if not metadata_element:
#         return
#     for key, value in metadata_element.items():
#         result.metadata[key] = value


# def parse_status(status_element, result, type):
#     if not status_element:
#         return
#     result.starttime = status_element.get('starttime', None)
#     result.endtime = status_element.get('endtime', None)
#     if type != "suite":
#         result.status = status_element.get('status', 'FAIL')
#     if type != "keyword" or result.type == result.TEARDOWN:
#         result.message = status_element.get('message', None)


# def parse_test(test_element, result):
#     if not test_element:
#         return
#     test = result.tests.create(name=test_element.get('name', ''))
#     test.doc = test_element.get('doc', '')
#     test.timeout = test_element.get('timeout', None)
#     for tag in test_element.get('tags', []):
#         test.tags.add(tag)
#     parse_status(test_element.get('status', None), test, "test")
#     for element in test_element.get('kw', []):
#         parse_keyword(element, test)


# def parse_keyword(keyword_element, result):
#     if not keyword_element:
#         return
#     keyword = result.body.create_keyword(kwname=keyword_element.get('name', ''),
#                                          libname=keyword_element.get('lib', ''),
#                                          type=keyword_element.get('type', 'kw'))
#     keyword.doc = keyword_element.get('doc', '')
#     keyword.timeout = keyword_element.get('timeout', None)
#     for arg in keyword_element.get('args', []):
#         if not keyword.args:
#             keyword.args = list()
#         keyword.args.append(arg)
#     for assign in keyword_element.get('assign', []):
#         keyword.assign += (assign or '',)
#     for tag in keyword_element.get('tags', []):
#         keyword.tags.add(tag)
#     for element in keyword_element.get('msgs', []):
#         parse_message(element, keyword)
#     for element in keyword_element.get('kw', []):
#         parse_keyword(element, keyword)
#     parse_status(keyword_element.get('status', None), keyword, "keyword")


# def parse_message(message_element, result):
#     result.body.create_message(message_element.get('msg', ''),
#                                message_element.get('level', 'INFO'),
#                                message_element.get('html', False),
#                                message_element.get('timestamp', None))
