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

from robot import utils
from robot.output import LEVELS
from robot.result.visitor import ResultVisitor


class _Handler(object):

    def __init__(self, context):
        self._context = context
        self._suites = []
        self._tests = []
        self._keywords = []
        self._messages = []
        self._errors = []

    def build(self, item):
        return None

    def suite_handler(self):
        return SuiteHandler(self._context)

    def test_handler(self):
        return TestHandler(self._context)

    def keyword_handler(self):
        return KeywordHandler(self._context)

    def message_handler(self):
        return MessageHandler(self._context)

    def errors_handler(self):
        return ErrorsHandler(self._context)

    def add_suite(self, data):
        self._suites.append(data)

    def add_test(self, data):
        self._tests.append(data)

    def add_keyword(self, data):
        self._keywords.append(data)

    def add_message(self, data):
        self._messages.append(data)

    def add_errors(self, data):
        self._errors = data

    def _status(self, item):
        return StatusHandler(self._context).build(item)

    def _id(self, text):
        return self._context.get_id(text)

    def _id_html(self, text):
        return self._id(utils.html_format(text))

    def _timestamp(self, time_string):
        return self._context.timestamp(time_string)


class ExecutionResultHandler(_Handler):

    def __init__(self, context, execution_result):
        _Handler.__init__(self, context)
        self._generator = execution_result.generator

    def visit_statistics(self, stats):
        self._stats = []
        return StatisticsHandler(self._stats, stats)

    def build(self, _):
        return {'generator': self._generator,
                'suite': self._suites[0],
                'stats': self._stats,
                'errors': self._errors,
                'baseMillis': self._context.basemillis,
                'strings': self._context.dump_texts()}


class ErrorsHandler(_Handler):

    def build(self, errors):
        return self._messages


class SuiteStatVisitor(ResultVisitor):

    def __init__(self, collection):
        self.collection = collection

    def visit_stat(self, stats):
        stat = self._create_stat(stats)
        stat['id'] = stats.attrs['idx']
        stat['name'] = stats.attrs['name']
        self.collection += [stat]

    def _create_stat(self, stat_elem):
        return {'pass':stat_elem.passed,
                'fail':stat_elem.failed,
                'label':stat_elem.name}


class StatisticsHandler(object):

    def __init__(self, stats_list, stats):
        self._result = stats_list
        self._result.append(self._parse_totals(stats.total))
        self._result.append(self._parse_tag(stats.tags))
        self._result.append(self._parse_suite(stats.suite))

    def _parse_totals(self, total):
        return [self._create_stat(total.critical), self._create_stat(total.all)]

    def _parse_tag(self, tags):
        return [self._create_stat(tag) for tag in tags]

    def _parse_suite(self, suite):
        stats = []
        suite.visit(SuiteStatVisitor(stats))
        return stats

    def _create_stat(self, stat_elem):
        return {'pass':stat_elem.passed,
                'fail':stat_elem.failed,
                'label':stat_elem.name}

    def end_element(self, _):
        return self._result


class SuiteHandler(_Handler):

    def __init__(self, context):
        _Handler.__init__(self, context)
        self._context.start_suite()

    def keyword_handler(self):
        return SuiteKeywordHandler(self._context)

    def build(self, suite):
        return [self._id(suite.name),
                self._id(suite.source),
                self._id(self._context.get_rel_log_path(suite.source)),
                self._id_html(suite.doc),
                self._metadata(suite),
                self._status(suite),
                self._suites,
                self._tests,
                self._keywords,
                self._stats(suite)]

    def _metadata(self, suite):
        metadata = []
        for name, value in suite.metadata.items():
            metadata.extend([self._id(name), self._id(utils.html_format(value))])
        return metadata

    def _stats(self, suite):
        stats = suite.statistics  # Access property only once
        return [stats.all.total, stats.all.failed,
                stats.critical.total, stats.critical.failed]


class TestHandler(_Handler):

    def __init__(self, context):
        _Handler.__init__(self, context)
        self._context.start_test()

    def build(self, test):
        self._keywords = self._context.end_test(self._keywords)
        return [self._id(test.name),
                self._id(test.timeout),
                int(test.critical == 'yes'),
                self._id_html(test.doc),
                [self._id(tag) for tag in test.tags],
                self._status(test),
                self._keywords]


class KeywordHandler(_Handler):
    _types = {'kw': 0, 'setup': 1, 'teardown': 2, 'for': 3, 'foritem': 4}

    def __init__(self, context):
        _Handler.__init__(self, context)
        context.start_keyword()

    def build(self, keyword):
        result = self._create_result(keyword)
        self._context.end_keyword()
        return result

    def _create_result(self, keyword):
        return [self._types[keyword.type],
                  self._id(keyword.name),
                  self._id(keyword.timeout),
                  self._id_html(keyword.doc),
                  self._id(', '.join(keyword.args)),
                  self._status(keyword),
                  self._keywords,
                  self._messages]


class SuiteKeywordHandler(KeywordHandler):

    def __init__(self, context):
        _Handler.__init__(self, context)
        self._context.start_suite_setup_or_teardown()

    def build(self, keyword):
        self._keywords = self._context.end_suite_setup_or_teardown(self._keywords)
        return self._create_result(keyword)


class StatusHandler(_Handler):
    _statuses = {'FAIL': 0, 'PASS': 1, 'NOT_RUN': 2}

    def build(self, item):
        model = [self._statuses[item.status],
                 self._timestamp(item.starttime),
                 int(item.elapsedtime)]
        msg = getattr(item, 'message', '')
        if msg:
            model.append(self._id(msg))
        return model


class MessageHandler(_Handler):

    def build(self, message):
        msg = [self._timestamp(message.timestamp),
               LEVELS[message.level],
               self._format_message_text(message)]
        self._handle_warning_linking(msg, message)
        # linking doesn't work without this late _id thing
        # because the text id:s are different in errors
        # than in the target test
        # when texts have been split with splitlog option
        msg[2] = self._id(msg[2])
        return msg

    def _format_message_text(self, message):
        return message.message if message.html else \
                    utils.html_escape(message.message)

    def _handle_warning_linking(self, msg, message):
        if message.linkable:
            msg.append(self._id(self._context.link_to(msg)))
        elif message.level == 'WARN':
            self._context.create_link_to_current_location(msg)
