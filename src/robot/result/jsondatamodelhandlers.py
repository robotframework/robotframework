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
import time

from robot import utils
from robot.output import LEVELS
from robot.reporting.parsingcontext import TextIndex


class _Handler(object):

    def __init__(self, context):
        self._context = context
        self._suites = []
        self._tests = []
        self._keywords = []
        self._messages = []
        self._errors = []
        self._statistics = []
        self._stats = []

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

    def statistics_handler(self):
        return StatisticsHandler(self._context)

    def stat_handler(self):
        return StatHandler(self._context)

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

    def add_statistics(self, data):
        self._statistics.append(data)

    def add_stat(self, data):
        self._stats.append(data)

    def _status(self, item):
        return StatusHandler(self._context).build(item)

    def _id(self, text):
        return self._context.get_id(text)

    def _id_html(self, text):
        return self._id(utils.html_format(text))

    def _timestamp(self, time_string):
        return self._context.timestamp(time_string)


class ExecutionResultHandler(_Handler):

    def build(self, _):
        return JsExecutionResult(
            suite=self._suites[0],
            strings=self._context.dump_texts(),
            data= {
                'stats': self._statistics,
                'errors': self._errors,
                'baseMillis': self._context.basemillis
            },
            split_results= self._context.split_results
        )


class JsExecutionResult(object):

    def __init__(self, suite, strings, data, split_results=None):
        self.suite = suite
        self.strings = strings
        self.data = data
        self._set_generated(time.localtime())
        self.split_results = split_results or []

    def _set_generated(self, timetuple):
        genMillis = long(time.mktime(timetuple) * 1000) - self.data['baseMillis']
        self.data['generatedMillis'] = genMillis
        self.data['generatedTimestamp'] = utils.format_time(timetuple, gmtsep=' ')

    def remove_keywords(self):
        self._remove_keywords_from_suite(self.suite)
        self._prune_unused_indices()

    def remove_errors(self):
        self.data.pop('errors')

    def _remove_keywords_from_suite(self, suite):
        suite[8] = []
        for subsuite in suite[6]:
            self._remove_keywords_from_suite(subsuite)
        for test in suite[7]:
            test[-1] = []

    def _prune_unused_indices(self):
        used = self._collect_used_indices(self.suite, set())
        remap = {}
        self.strings = \
            list(self._prune(self.strings, used, remap))
        self._remap_indices(self.suite, remap)

    def _prune(self, data, used, index_remap, map_index=None, offset_increment=1):
        offset = 0
        for index, text in enumerate(data):
            index = map_index(index) if map_index else index
            if index in used:
                index_remap[index] = index - offset
                yield text
            else:
                offset += offset_increment

    def _remap_indices(self, data, remap):
        for i, item in enumerate(data):
            if isinstance(item, TextIndex):
                data[i] = remap[item]
            elif isinstance(item, list):
                self._remap_indices(item, remap)

    def _collect_used_indices(self, data, result):
        for item in data:
            if isinstance(item, TextIndex):
                result.add(item)
            elif isinstance(item, list):
                self._collect_used_indices(item, result)
            elif isinstance(item, dict):
                self._collect_used_indices(item.values(), result)
                self._collect_used_indices(item.keys(), result)
        return result



class ErrorsHandler(_Handler):

    def build(self, errors):
        return self._messages


class StatisticsHandler(_Handler):

    def build(self, stats):
        return self._stats


class StatHandler(_Handler):

    def build(self, stat):
        return stat.get_attributes(include_label=True, exclude_empty=True)


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
                self._get_metadata(suite),
                self._status(suite),
                self._suites,
                self._tests,
                self._keywords,
                self._get_stats(suite)]

    def _get_metadata(self, suite):
        metadata = []
        for name, value in suite.metadata.items():
            metadata.extend([self._id(name), self._id_html(value)])
        return metadata

    def _get_stats(self, suite):
        stats = suite.statistics  # Access property only once
        return [stats.all.total, stats.all.passed,
                stats.critical.total, stats.critical.passed]


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
