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

import zlib
import base64
from operator import itemgetter

from robot import utils


class _Handler(object):

    def __init__(self, context, attrs=None):
        self._context = context
        self._data_from_children = []
        self._handlers = {
            'robot'      : _RobotHandler,
            'suite'      : _SuiteHandler,
            'test'       : _TestHandler,
            'statistics' : _StatisticsHandler,
            'stat'       : _StatItemHandler,
            'errors'     : _Handler,
            'doc'        : _HtmlTextHandler,
            'kw'         : _KeywordHandler,
            'arg'        : _ArgumentHandler,
            'arguments'  : _ArgumentsHandler,
            'tag'        : _TextHandler,
            'tags'       : _Handler,
            'msg'        : _MsgHandler,
            'status'     : _StatusHandler,
            'metadata'   : _MetadataHandler,
            'item'       : _MetadataItemHandler,
            }

    def get_handler_for(self, name, attrs):
        return self._handlers[name](self._context, attrs)

    def add_child_data(self, data):
        self._data_from_children.append(data)

    def end_element(self, text):
        return self._data_from_children

    def _get_id(self, item):
        return self._context.get_id(item)

    def _get_ids(self, items):
        return [self._context.get_id(i) for i in items]


class RootHandler(_Handler):
    # TODO: Combine _RootHandler and _RobotHandler

    @property
    def data(self):
        return self._data_from_children[0]


class _RobotHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._generator = attrs.get('generator')

    def end_element(self, text):
        return {'generator': self._generator,
                'suite': self._data_from_children[0],
                'stats': self._data_from_children[1],
                'errors': self._data_from_children[2],
                'baseMillis': self._context.basemillis,
                'strings': self._context.dump_texts()}


class _SuiteHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._name = attrs.get('name')
        self._source = attrs.get('source') or ''
        self._suites = []
        self._tests = []
        self._keywords = []
        self._current_children = None
        self._context.start_suite(self._name)
        self._context.collect_stats()

    def get_handler_for(self, name, attrs):
        self._current_children = {
            'suite': self._suites,
            'test': self._tests,
            'kw': self._keywords
        }.get(name, self._data_from_children)
        return _Handler.get_handler_for(self, name, attrs)

    def add_child_data(self, data):
        self._current_children.append(data)

    def end_element(self, text):
        result = self._get_ids([self._source, self._name]) + \
                 self._data_from_children + [self._suites] + \
                 [self._tests] + [self._keywords] + \
                 [self._get_ids(self._context.dump_stats())]
        self._context.end_suite()
        return result


class _TestHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._name = attrs.get('name')
        self._timeout = attrs.get('timeout')
        self._keywords = []
        self._current_children = None
        self._context.start_test(self._name)

    def get_handler_for(self, name, attrs):
        if name == 'status':
            # TODO: Use 1/0 instead of Y/N. Possibly also 1/0/-1 instead of P/F/N.
            self._critical = 'Y' if attrs.get('critical') == 'yes' else 'N'
        self._current_children = {
            'kw': self._keywords
        }.get(name, self._data_from_children)
        return _Handler.get_handler_for(self, name, attrs)

    def add_child_data(self, data):
        self._current_children.append(data)

    def end_element(self, text):
        # TODO: refactor
        self._context.add_test(self._critical == 'Y', self._data_from_children[-1][0] == self._get_id('P'))
        kws = self._context.end_test(self._keywords)
        result = self._get_ids([self._name, self._timeout, self._critical]) + self._data_from_children
        result.append(kws)
        return result


class _KeywordHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._context.start_keyword()
        self._type = attrs.get('type')
        if self._type == 'for': self._type = 'forloop'
        self._name = attrs.get('name')
        self._timeout = attrs.get('timeout')
        self._keywords = []
        self._messages = []
        self._current_children = None

    def get_handler_for(self, name, attrs):
        if name == 'status':
            # TODO: Use 1/0 instead of Y/N. Possibly also 1/0/-1 instead of P/F/N.
            self._critical = 'Y' if attrs.get('critical') == 'yes' else 'N'
        self._current_children = {
            'kw': self._keywords,
            'msg': self._messages
        }.get(name, self._data_from_children)
        return _Handler.get_handler_for(self, name, attrs)

    def add_child_data(self, data):
        self._current_children.append(data)

    def end_element(self, text):
        if self._type == 'teardown' and self._data_from_children[-1][0] == self._get_id('F'):
            self._context.teardown_failed()
        result = self._get_ids([self._type, self._name, self._timeout]) + \
               self._data_from_children + [self._keywords] + [self._messages]
        self._context.end_keyword()
        return result


# TODO: StatisticsHandler and StatItemHandler should be separated somehow from suite handlers

class _StatisticsHandler(_Handler):

    def get_handler_for(self, name, attrs):
        return _Handler(self._context, attrs)


class _StatItemHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._attrs = dict(attrs)
        self._attrs['pass'] = int(self._attrs['pass'])
        self._attrs['fail'] = int(self._attrs['fail'])
        if 'doc' in self._attrs:
            self._attrs['doc'] = utils.html_format(self._attrs['doc'])
        # TODO: Should we only dump attrs that have value?
        # Tag stats have many attrs that are normally empty

    def end_element(self, text):
        self._attrs.update(label=text)
        return self._attrs


class _StatusHandler(_Handler):

    def __init__(self, context, attrs):
        self._context = context
        self._status = attrs.get('status')[0]
        self._starttime = self._context.timestamp(attrs.get('starttime'))
        endtime = self._context.timestamp(attrs.get('endtime'))
        self._elapsed = self._calculate_elapsed(endtime)

    def _calculate_elapsed(self, endtime):
        # Both start and end may be 0 so must compare against None
        if self._starttime is None or endtime is None:
            return None
        return endtime - self._starttime

    def end_element(self, text):
        result = [self._status,
                  self._starttime,
                  self._elapsed]
        if text:
            result.append(text)
        return self._get_ids(result)


class _ArgumentHandler(_Handler):

    def end_element(self, text):
        return text


class _ArgumentsHandler(_Handler):

    def end_element(self, text):
        return self._get_id(', '.join(self._data_from_children))


class _TextHandler(_Handler):

    def end_element(self, text):
        return self._get_id(text)


class _HtmlTextHandler(_Handler):

    def end_element(self, text):
        return self._get_id(utils.html_format(text))


class _MetadataHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._metadata = []

    def add_child_data(self, data):
        self._metadata.extend(data)

    def end_element(self, text):
        return self._metadata


class _MetadataItemHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._name = attrs.get('name')

    def end_element(self, text):
        return self._get_ids([self._name, utils.html_format(text)])


class _MsgHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._msg = [self._context.timestamp(attrs.get('timestamp')),
                     attrs.get('level')[0]]
        self._is_html = attrs.get('html')
        self._is_linkable = attrs.get("linkable") == "yes"

    def end_element(self, text):
        self._msg.append(text if self._is_html else utils.html_escape(text))
        self._handle_warning_linking()
        return self._get_ids(self._msg)

    def _handle_warning_linking(self):
        # TODO: should perhaps use the id version of this list for indexing?
        if self._is_linkable:
            self._msg.append(self._context.link_to(self._msg))
        elif self._msg[1] == 'W':
            self._context.create_link_to_current_location(self._msg)


class Context(object):

    def __init__(self, split_tests=False):
        self._main_text_cache = TextCache()
        self._current_texts = self._main_text_cache
        self._split_text_caches = []
        self._basemillis = 0
        self._stats = Stats()
        self._current_place = []
        self._kw_index = []
        self._links = {}
        self._split_tests = split_tests
        self._split_results = []

    @property
    def basemillis(self):
        return self._basemillis

    @property
    def split_results(self):
        return self._split_results

    def collect_stats(self):
        self._stats = self._stats.new_child()
        return self

    def dump_stats(self):
        try:
            return self._stats.dump()
        finally:
            self._stats = self._stats.parent

    def get_id(self, value):
        if value is None:
            return None
        if isinstance(value, basestring):
            return self._get_text_id(value)
        if isinstance(value, (int, long)):
            return value
        raise AssertionError('Unsupported type of value '+str(type(value)))

    def _get_text_id(self, text):
        return self._current_texts.add(text)

    def dump_texts(self):
        return self._current_texts.dump()

    def timestamp(self, time):
        if time == 'N/A':
            return None
        millis = int(utils.timestamp_to_secs(time, millis=True) * 1000)
        if not self._basemillis:
            self._basemillis = millis
        return millis - self.basemillis

    def start_suite(self, name):
        self._current_place.append(('suite', name))
        self._kw_index.append(0)

    def end_suite(self):
        self._current_place.pop()
        self._kw_index.pop()

    def start_test(self, name):
        self._current_place.append(('test', name))
        self._kw_index.append(0)

    def end_test(self, kw_data=None):
        self._current_place.pop()
        self._kw_index.pop()
        if self._split_tests:
            self._split_results.append({'keywords': kw_data,
                                        'strings': self._split_text_caches[-1].dump()})
            return len(self._split_results)
        return kw_data

    def start_keyword(self):
        if self._split_tests and self._current_place[-1][0] == 'test':
            self._split_text_caches.append(TextCache())
            self._current_texts = self._split_text_caches[-1]
        self._current_place.append(('keyword', self._kw_index[-1]))
        self._kw_index[-1] += 1
        self._kw_index.append(0)

    def end_keyword(self):
        self._current_place.pop()
        self._kw_index.pop()
        if self._split_tests and self._current_place[-1][0] == 'test':
            self._current_texts = self._main_text_cache

    def create_link_to_current_location(self, key):
        self._links[tuple(key)] = self._create_link()

    def _create_link(self):
        return "keyword_"+".".join(str(v) for _, v in self._current_place)

    def link_to(self, key):
        return self._links[tuple(key)]

    def add_test(self, critical, passed):
        self._stats.add_test(critical, passed)

    def teardown_failed(self):
        self._stats.fail_all()


class Stats(object):
    TOTAL = 0
    TOTAL_PASSED = 1
    CRITICAL = 2
    CRITICAL_PASSED = 3

    def __init__(self, parent=None):
        self.parent = parent
        self._stats = [0,0,0,0]
        self._children = []

    def new_child(self):
        self._children.append(Stats(self))
        return self._children[-1]

    def add_test(self, critical, passed):
        self._stats[Stats.TOTAL] += 1
        if passed:
            self._stats[Stats.TOTAL_PASSED] +=1
        if critical:
            self._stats[Stats.CRITICAL] += 1
            if passed:
                self._stats[Stats.CRITICAL_PASSED] += 1

    def dump(self):
        if self.parent:
            for i in range(4):
                self.parent._stats[i] += self._stats[i]
        return self._stats

    def fail_all(self):
        self._stats[1] = 0
        self._stats[3] = 0
        for child in self._children:
            child.fail_all()

class TextIndex(int):
    pass

ZERO_TEXT_INDEX = TextIndex(0)

class TextCache(object):
    # TODO: Tune compressing thresholds
    _compress_threshold = 20
    _use_compressed_threshold = 1.1

    def __init__(self):
        self.texts = {'*': ZERO_TEXT_INDEX}
        self.index = 1

    def add(self, text):
        if not text:
            return 0
        text = self._encode(text)
        if text not in self.texts:
            self.texts[text] = TextIndex(self.index)
            self.index += 1
        return self.texts[text]

    def _encode(self, text):
        raw = self._raw(text)
        if raw in self.texts or len(raw) < self._compress_threshold:
            return raw
        compressed = self._compress(text)
        if len(compressed) * self._use_compressed_threshold < len(raw):
            return compressed
        return raw

    def _compress(self, text):
        return base64.b64encode(zlib.compress(text.encode('UTF-8'), 9))

    def _raw(self, text):
        return '*'+text

    def dump(self):
        # TODO: Could we yield or return an iterator?
        # TODO: Duplicate with IntegerCache.dump
        return [item[0] for item in sorted(self.texts.iteritems(),
                                           key=itemgetter(1))]

