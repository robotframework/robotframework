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

from __future__ import with_statement
import xml.sax as sax
from xml.sax.handler import ContentHandler
import zlib
import base64

from robot import utils


class Context(object):

    def __init__(self):
        self._texts = TextCache()
        self._basemillis = None
        self._stats = Stats()
        self._current_place = []
        self._kw_index = []
        self._links = {}

    @property
    def basemillis(self):
        return self._basemillis

    def collect_stats(self):
        self._stats = self._stats.new_child()
        return self

    def dump_stats(self):
        try:
            return self._stats.dump()
        finally:
            self._stats = self._stats.parent

    def get_text_id(self, text):
        return self._texts.add(text)

    def dump_texts(self):
        return self._texts.dump()

    def timestamp(self, time):
        if time == 'N/A':
            return None
        millis = int(utils.timestamp_to_secs(time, millis=True) * 1000)
        if self._basemillis is None:
            self._basemillis = millis
        return millis - self.basemillis

    def start_suite(self, name):
        self._current_place += [('suite', name)]
        self._kw_index += [0]

    def end_suite(self):
        self._current_place.pop()
        self._kw_index.pop()

    def start_test(self, name):
        self._current_place += [('test', name)]
        self._kw_index += [0]

    def end_test(self):
        self._current_place.pop()
        self._kw_index.pop()

    def start_keyword(self):
        self._current_place += [('keyword', self._kw_index[-1])]
        self._kw_index[-1] += 1
        self._kw_index += [0]

    def end_keyword(self):
        self._current_place.pop()
        self._kw_index.pop()

    def create_link_to_current_location(self, key):
        self._links[str(key)] = self._create_link()

    def _create_link(self):
        return "keyword_"+".".join(str(v) for _, v in self._current_place)

    def link_to(self, key):
        return self._links[str(key)]

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
        self._children += [Stats(self)]
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


class _TextIndex(int):
    pass


class TextCache(object):
    _zero_index = _TextIndex(0)
    # TODO: Tune compressing thresholds
    _compress_threshold = 20
    _use_compressed_threshold = 1.1

    def __init__(self):
        self.texts = {}
        self.index = 1

    def add(self, text):
        if not text:
            return self._zero_index
        text = self._encode(text)
        if text not in self.texts:
            self.texts[text] = _TextIndex(self.index)
            self.index += 1
        return self.texts[text]

    def _encode(self, text):
        raw = self._raw(text)
        if raw in self.texts or len(raw) < self._compress_threshold:
            return raw
        compressed = base64.b64encode(zlib.compress(text.encode('UTF-8'), 9))
        if len(raw) * self._use_compressed_threshold > len(compressed):
            return compressed
        return raw

    def _raw(self, text):
        return '*'+text

    def dump(self):
        l = range(len(self.texts)+1)
        l[0] = '*'
        for k, v in self.texts.items():
            l[v] = k
        return l

levels = {'TRACE':'T',
          'DEBUG':'D',
          'INFO':'I',
          'WARN':'W',
          'ERROR':'E',
          'FAIL':'F'}

def create_datamodel_from(input_filename):
    robot = _RobotOutputHandler(Context())
    with open(input_filename, 'r') as input:
        sax.parse(input, robot)
    return robot.datamodel


class _Handler(object):

    def __init__(self, context, *args):
        self._context = context
        self._children = []
        self._handlers = {
        'robot'      : _RobotHandler,
        'suite'      : _SuiteHandler,
        'test'       : _TestHandler,
        'statistics' : _StatisticsHandler,
        'stat'       : _StatItemHandler,
        'errors'     : _Handler,
        'doc'        : _TextHandler,
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

    def get_handler_for(self, name, *args):
        return self._handlers[name](self.context, *args)

    @property
    def context(self):
        return self._context

    @property
    def children(self):
        return self._children

    def add_child(self, child):
        self._children += [child]

    def end_element(self, text):
        return self._children


class _RobotHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context, attrs)
        self._generator = attrs.getValue('generator')
        self._generated = attrs.getValue('generated')

    def end_element(self, text):
        if self._generated:
            self._generated = self.context.timestamp(self._generated)
        return [self._generated, self._generator] + self.children


class _StatisticsHandler(_Handler):

    def get_handler_for(self, name, *args):
        return _Handler(self.context, *args)


class _StatItemHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context, attrs)
        self._pass = int(attrs.getValue('pass'))
        self._fail = int(attrs.getValue('fail'))
        self._doc = attrs.get('doc') or ''
        self._info = attrs.get('info') or ''
        self._links = attrs.get('links') or ''

    def end_element(self, text):
        return [text, self._pass, self._fail, self._doc, self._info, self._links]


class _SuiteHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context, attrs)
        self._name = attrs.getValue('name')
        self._source = attrs.get('source') or ''
        self.context.start_suite(self._name)
        self.context.collect_stats()

    def end_element(self, text):
        try:
            return ['suite',
                     self._source,
                     self._name] + self._children + [self.context.dump_stats()]
        finally:
            self.context.end_suite()


class _TestHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context, attrs)
        name = attrs.getValue('name')
        self._name_id = self.context.get_text_id(name)
        self._timeout = self.context.get_text_id(attrs.get('timeout'))
        self.context.start_test(name)

    def get_handler_for(self, name, *args):
        if name == 'status':
            return _TestStatusHandler(self, *args)
        return _Handler.get_handler_for(self, name, *args)

    def end_element(self, text):
        result = ['test', self._name_id, self._timeout, self._critical] + self.children
        self.context.add_test(self._critical == 'Y', result[-1][0] == 'P')
        self.context.end_test()
        return result


class _StatusHandler(object):
    def __init__(self, context, attrs):
        self._context = context
        self._status = attrs.getValue('status')[0]
        self._starttime = self._context.timestamp(attrs.getValue('starttime'))
        endtime = self._context.timestamp(attrs.getValue('endtime'))
        self._elapsed = endtime-self._starttime if endtime is not None and self._starttime is not None else None

    def end_element(self, text):
        result = [self._status,
                  self._starttime,
                  self._elapsed]
        if text:
           result += [self._context.get_text_id(text)]
        return result


class _TestStatusHandler(_StatusHandler):

    def __init__(self, test, attrs):
        _StatusHandler.__init__(self, test.context, attrs)
        test._critical = 'Y' if attrs.get('critical') == 'yes' else 'N'


class _KeywordHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context, attrs)
        self.context.start_keyword()
        self._type = attrs.getValue('type')
        self._name = self.context.get_text_id(attrs.getValue('name'))
        self._timeout = self.context.get_text_id(attrs.getValue('timeout'))

    def end_element(self, text):
        if self._type == 'teardown' and self.children[-1][0] == 'F':
            self.context.teardown_failed()
        self.context.end_keyword()
        return [self._type, self._name, self._timeout]+self.children


class _ArgumentHandler(_Handler):

    def end_element(self, text):
        return text


class _ArgumentsHandler(_Handler):

    def end_element(self, text):
        return self._context.get_text_id(', '.join(self.children))


class _TextHandler(_Handler):

    def end_element(self, text):
        return self.context.get_text_id(text)


class _MetadataHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context, attrs)
        self._dictionary = {}

    def add_child(self, child):
        self._dictionary[child[0]] = child[1]

    def end_element(self, text):
        return self._dictionary


class _MetadataItemHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context, attrs)
        self._name = attrs.getValue('name')

    def end_element(self, text):
        return (self._name, self.context.get_text_id(text))


class _MsgHandler(object):

    def __init__(self, context, attrs):
        self._context = context
        self._msg = []
        self._msg += [self._context.timestamp(attrs.getValue('timestamp'))]
        self._msg += [levels[attrs.getValue('level')]]
        self._is_html = attrs.get('html')
        self._is_linkable = attrs.get("linkable") == "yes"

    def end_element(self, text):
        self._add_text(text)
        self._handle_warning_linking()
        return self._msg

    def _handle_warning_linking(self):
        if self._is_linkable:
            self._msg += [self._context.link_to(self._msg)]
        elif self._msg[1] == 'W':
            self._context.create_link_to_current_location(self._msg)

    def _add_text(self, text):
        if self._is_html:
            self._msg += [self._context.get_text_id(text)]
        else:
            self._msg += [self._context.get_text_id(utils.html_escape(text, replace_whitespace=False))]


class _RootHandler(_Handler):

    def add_child(self, child):
        self.data = child


class _RobotOutputHandler(ContentHandler):

    def __init__(self, context):
        self._context = context
        self._handler_stack = [_RootHandler(context)]

    @property
    def datamodel(self):
        return DataModel(self._context.basemillis, self._handler_stack[0].data, self._context.dump_texts())

    def startElement(self, name, attrs):
        handler = self._handler_stack[-1].get_handler_for(name, attrs)
        self._charbuffer = []
        self._handler_stack.append(handler)

    def endElement(self, name):
        handler = self._handler_stack.pop()
        self._handler_stack[-1].add_child(handler.end_element(''.join(self._charbuffer)))

    def characters(self, content):
        self._charbuffer += [content]


class DataModel(object):

    def __init__(self, basemillis, robot_data, texts):
        self._basemillis = basemillis
        self._robot_data = robot_data
        self._texts = texts

    def write_to(self, output):
        output.write('window.basemillis = '+str(self._basemillis)+';\n')
        output.write('window.data = ')
        json_dump(self._robot_data, output)
        output.write(';\n')
        output.write('window.strings =')
        json_dump(self._texts, output)
        output.write(';\n')

    def remove_keywords(self):
        self._robot_data = self._remove_keywords_from(self._robot_data)
        self._prune_unused_texts()

    def _remove_keywords_from(self, data):
        if not isinstance(data, list):
            return data
        return [self._remove_keywords_from(item) for item in data if not self._is_keyword(item)]

    def _is_keyword(self, item):
        return isinstance(item, list) and item and item[0] in ['kw', 'setup', 'teardown']

    def _prune_unused_texts(self):
        used = self._collect_used_text_indices(self._robot_data, set())
        self._texts = [text if index in used else '' for index, text in enumerate(self._texts)]

    def _collect_used_text_indices(self, data, result):
        for item in data:
            if isinstance(item, _TextIndex):
                result.add(item)
            elif isinstance(item, list):
                self._collect_used_text_indices(item, result)
            elif isinstance(item, dict):
                self._collect_used_text_indices(item.values(), result)
        return result


def encode_basestring(string):
    def get_matching_char(c):
        val = ord(c)
        if val < 127 and val > 31:
            return c
        return '\\u' + hex(val)[2:].rjust(4,'0')
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    string = string.replace('\b', '\\b')
    string = string.replace('\f', '\\f')
    string = string.replace('\n', '\\n')
    string = string.replace('\r', '\\r')
    string = string.replace('\t', '\\t')
    result = []
    for c in string:
        result += [get_matching_char(c)]
    return '"'+''.join(result)+'"'

def json_dump(data, output):
    if data is None:
        output.write('null')
    elif isinstance(data, int):
        output.write(str(data))
    elif isinstance(data, long):
        output.write(str(data))
    elif isinstance(data, basestring):
        output.write(encode_basestring(data))
    elif isinstance(data, list):
        output.write('[')
        for index, item in enumerate(data):
            json_dump(item, output)
            if index < len(data)-1:
                output.write(',')
        output.write(']')
    elif type(data) == dict:
        output.write('{')
        for index, item in enumerate(data.items()):
            json_dump(item[0], output)
            output.write(':')
            json_dump(item[1], output)
            if index < len(data)-1:
                output.write(',')
        output.write('}')
    else:
        raise Exception('Data type (%s) serialization not supported' % type(data))

def parse_js(input_filename, output):
    create_datamodel_from(input_filename).write_to(output)
