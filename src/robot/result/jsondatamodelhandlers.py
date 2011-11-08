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
from robot.result.model import TestSuite, Keyword, TestCase


class _Handler(object):

    def __init__(self, context, attrs=None):
        self._context = context
        self._current_children = None
        self._suites = []
        self._keywords = []
        self._tests = []
        self._stats = []
        self._data_from_children = []

    def add_child_data(self, data):
        self._data_from_children.append(data)

    def start_suite(self, suite):
        self._current_children = self._suites
        return SuiteHandler(self._context, suite)

    def start_keyword(self, keyword):
        self._current_children = self._keywords
        return KeywordHandler(self._context, keyword)

    def start_test(self, test):
        self._current_children = self._tests
        return TestHandler(self._context, test)

    def message(self, message):
        self._data_from_children.append(_MsgHandler(self._context, message).end_element(message.message))

    def end_element(self, text):
        return self._data_from_children

    def _get_id(self, item):
        return self._context.get_id(item)

    def _get_ids(self, *items):
        return [self._get_id(i) for i in items]

    def _last_child_passed(self):
        return self._last_child_status() == 1

    def _last_child_status(self):
        return self._data_from_children[-1][0]

class ExecutionResultHandler(_Handler):

    def __init__(self, context, execution_result):
        _Handler.__init__(self, context)
        self._generator = execution_result.generator

    def visit_statistics(self, stats):
        self._current_children = self._stats
        return StatisticsHandler(self._stats, stats)

    def end_element(self, text):
        return {'generator': self._generator,
                'suite': self._data_from_children[0],
                'stats': self._stats,
                #                'errors': self._data_from_children[2],
                'baseMillis': self._context.basemillis,
                'strings': self._context.dump_texts()}

class StatisticsHandler(object):

    def __init__(self, stats_list, stats):
        self._result = stats_list
        self._result.append(self._parse_totals(stats.total))
        self._result.append(self._parse_tag(stats.tags))
        self._result.append(self._parse_suite(stats.suite))

    def _parse_totals(self, total):
        return [self._create_stat(total.critical), self._create_stat(total.all)]

    def _parse_tag(self, tags):
        return [self._create_stat(tag) for tag in tags.stats.values()]

    def _parse_suite(self, suite):
        all_stat = self._create_stat(suite.all)
        all_stat['id'] = suite.all.id
        all_stat['name'] = suite.all.longname
        return [all_stat]

    def _create_stat(self, stat_elem):
        return {'pass':stat_elem.passed,
                'fail':stat_elem.failed,
                'label':stat_elem.name}

    def end_element(self, text):
        return self._result


class SuiteHandler(_Handler):

    def __init__(self, context, suite):
        _Handler.__init__(self, context)
        self._source = suite.source
        self._name = suite.name
        self._suites = []
        self._tests = []
        self._keywords = []
        self._current_children = None
        self._teardown_failed = False
        self._context.start_suite()
        self._doc = self._get_id(suite.doc)
        self._data_from_children.append(self._doc)
        self._metadata = []
        for i in [self._get_ids(key, value) for key, value in suite.metadata.items()]:
            self._metadata.extend(i)
        self._data_from_children.append(self._metadata)

    def _get_name_and_sources(self):
        return self._get_ids(self._name, self._source,
                             self._context.get_rel_log_path(self._source))

    def _set_teardown_failed(self):
        self._teardown_failed = True

    def add_child_data(self, data):
        self._current_children.append(data)

    def end_element(self, suite):
        stats = self._context.end_suite()
        self._data_from_children.append(_StatusHandler(self._context, suite).end_element(''))
        return self._get_name_and_sources() + self._data_from_children + \
                 [self._suites, self._tests, self._keywords,
                  int(self._teardown_failed), stats]


class TestHandler(_Handler):

    def __init__(self, context, test):
        _Handler.__init__(self, context)
        self._name = test.name
        self._timeout = test.timeout
        self._keywords = []
        self._current_children = None
        self._context.start_test()
        self._critical = int(test.critical == 'yes')
        self._doc = self._get_id(test.doc)
        self._data_from_children.append(self._doc)
        self._status = _StatusHandler(self._context, test).end_element('')

    def add_child_data(self, data):
        self._current_children.append(data)

    def end_element(self, test):
        self._data_from_children.append([self._get_id(tag) for tag in test.tags])
        self._data_from_children.append(self._status)
        self._context.add_test(self._critical, self._last_child_passed())
        kws = self._context.end_test(self._keywords)
        return self._get_ids(self._name, self._timeout, self._critical) + \
                self._data_from_children + [kws]


class KeywordHandler(_Handler):
    _types = {'kw': 0, 'setup': 1, 'teardown': 2, 'for': 3, 'foritem': 4}

    def __init__(self, context, keyword):
        _Handler.__init__(self, context)
        self._type = self._types[keyword.type]
        self._name = keyword.name
        self._timeout = keyword.timeout
        self._keywords = []
        self._messages = []
        self._current_children = None
        self._start()

        self._doc = self._get_id(keyword.doc)
        self._data_from_children.append(self._doc)

        self._args = self._get_id(', '.join(keyword.args))
        self._data_from_children.append(self._args)

        self._status = _StatusHandler(self._context, keyword).end_element('')

    def _start(self):
        self._context.start_keyword()

    def add_child_data(self, data):
        self._current_children.append(data)

    def message(self, message):
        self._messages.append(_MsgHandler(self._context, message).end_element(message.message))

    def end_element(self, keyword):
        self._data_from_children.append(self._status)
        return self._get_ids(self._type, self._name, self._timeout) + \
                self._data_from_children + [self._get_keywords(), self._messages]

    def _get_keywords(self):
        self._context.end_keyword()
        return self._keywords


class _StatusHandler(_Handler):

    _statuses = {'FAIL': 0, 'PASS': 1, 'NOT_RUN': 2}

    def __init__(self, context, item):
        self._context = context
        self._status = self._statuses[item.status]
        self._starttime = self._context.timestamp(item.starttime)
        self._elapsed = self._calculate_elapsed(item)

    def _calculate_elapsed(self, item):
        endtime = self._context.timestamp(item.endtime)
        # Must compare against None because either start and end may be 0.
        if self._starttime is not None or endtime is not None:
            return endtime - self._starttime
        # Only RF 2.6+ outputs have elapsedtime when start or end is N/A.
        return int(item.elapsed)

    def end_element(self, text):
        result = [self._status, self._starttime, self._elapsed]
        if text:
            result.append(text)
        return self._get_ids(*result)


class _MsgHandler(_Handler):

    def __init__(self, context, message):
        _Handler.__init__(self, context)
        self._msg = [self._context.timestamp(message.timestamp),
                     LEVELS[message.level]]
        self._is_html = message.html
        self._is_linkable_in_error_table = message.linkable
        self._is_warning = message.level == 'WARN'

    def end_element(self, text):
        self._msg.append(text if self._is_html else utils.html_escape(text))
        self._handle_warning_linking()
        return self._get_ids(*self._msg)

    def _handle_warning_linking(self):
        if self._is_linkable_in_error_table:
            self._msg.append(self._context.link_to(self._msg))
        elif self._is_warning:
            self._context.create_link_to_current_location(self._msg)
