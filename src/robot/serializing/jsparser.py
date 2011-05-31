from __future__ import with_statement
from lxml import etree
import xml.sax as sax
from xml.sax.handler import ContentHandler
import json
import zlib
import base64
from datetime import datetime
from time import mktime
from robot.utils import html_escape

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
        dt = datetime.strptime(time+"000", "%Y%m%d %H:%M:%S.%f")
        millis = int(mktime(dt.timetuple())*1000+dt.microsecond/1000)
        if self.basemillis is None:
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


class TextCache(object):

    def __init__(self):
        self.texts = {}
        self.index = 1

    def add(self, text):
        if not text:
            return 0
        text = self._encode(text)
        if text not in self.texts:
            self.texts[text] = self.index
            self.index +=1
        return self.texts[text]

    def _encode(self, text):
        encoded = base64.b64encode(zlib.compress(text.encode('utf-8'), 9))
        raw = '*'+text
        return encoded if len(encoded) < len(raw) else raw

    def dump(self):
        l = range(len(self.texts)+1)
        l[0] = '*'
        for k, v in self.texts.items():
            l[v] = k
        return l


def _keyword_node_parser(node, context):
    context.start_keyword()
    try:
        result = [node.get('type'),
                  context.get_text_id(node.get('name')),
                  context.get_text_id(node.get('timeout'))]+_children(node, context)
        if result[0] == 'teardown' and result[-1][0] == 'F':
            context.teardown_failed()
        return result
    finally:
        context.end_keyword()

def _test_node_parser(node, context):
    name = node.get('name')
    context.start_test(name)
    try:
        critical = 'Y' if node.find('status').get('critical') == 'yes' else 'N'
        result = ['test',
                  context.get_text_id(name),
                  context.get_text_id(node.get('timeout')),
                  critical]+_children(node, context)
        context.add_test(critical == 'Y', result[-1][0] == 'P')
        return result
    finally:
        context.end_suite()

def _errors_node_parser(node, context):
    return _children(node, context)

def _children(node, context):
    return [_create_from_node(child, context) for child in node.getchildren()]

def _doc_node_parser(node, context):
    return context.get_text_id(node.text)

levels = {'TRACE':'T',
          'DEBUG':'D',
          'INFO':'I',
          'WARN':'W',
          'ERROR':'E',
          'FAIL':'F'}

def _get_level(node):
    return levels[node.get('level')]

def _get_msg_text_id(node, context):
    if node.get('html'):
        return context.get_text_id(node.text)
    else:
        return context.get_text_id(html_escape(node.text, replace_whitespace=False))

def _message_node_parser(node, context):
    msg = [context.timestamp(node.get('timestamp')),
            _get_level(node),
            _get_msg_text_id(node, context)]
    if node.get("linkable") == "yes":
        msg += [context.link_to(msg)]
    elif msg[1] == 'W':
        context.create_link_to_current_location(msg)
    return msg

def _metadata_node_parser(node, context):
    items = {}
    for item in node.getchildren():
        items[item.get('name')] = context.get_text_id(item.text)
    return items

def _status_node_parser(node, context):
    status = node.get('status')[0]
    starttime = context.timestamp(node.get('starttime'))
    endtime = context.timestamp(node.get('endtime'))
    return [status,
            starttime,
            endtime-starttime]

def _tags_node_parser(node, context):
    return [context.get_text_id(c.text) for c in node.getchildren()]

def _arguments_node_parser(node, context):
    return context.get_text_id(', '.join(c.text for c in node.getchildren() if c.text is not None))

def _suite_node_parser(node, context):
    name = node.get('name')
    context.start_suite(name)
    try:
        return ['suite',
                node.get('source'),
                name]+\
                _children(node, context.collect_stats())+\
                [context.dump_stats()]
    finally:
        context.end_suite()


def _robot_node_parser(node, context):
    generator = node.get('generator')
    children = _children(node, context)
    generated = node.get('generated')
    if generated:
        generated = context.timestamp(generated)
    return [generated, generator]+children

def _statistics_parser(node, context):
    return [_stat_from(c) for c in node.getchildren()]

def _stat_from(node):
    return [[stat.text, int(stat.get('pass')), int(stat.get('fail')),
             stat.get('doc', ''), stat.get('info', ''), stat.get('links', '')]
             for stat in node.getchildren()]


_node_parsers = {
'robot':_robot_node_parser,
'suite':_suite_node_parser,
'doc':_doc_node_parser,
'metadata':_metadata_node_parser,
'status':_status_node_parser,
'errors':_errors_node_parser,
'test':_test_node_parser,
'kw':_keyword_node_parser,
'tags':_tags_node_parser,
'arguments':_arguments_node_parser,
'statistics':_statistics_parser,
'msg':_message_node_parser
}

def _create_from_node(node, context):
    return _node_parsers[node.tag](node, context)

def create_datamodel_from(input_filename):
    context = Context()
    with open(input_filename, 'r') as file:
        xml = etree.parse(file)
        robot_data = _create_from_node(xml.getroot(), context)
        return DataModel(context.basemillis, robot_data, context.dump_texts())


class _MsgHandler(object):

    def __init__(self, context, attrs):
        self._context = context
        self._msg = []
        self._msg += [self._context.timestamp(attrs.getValue('timestamp'))]
        self._msg += [levels[attrs.getValue('level')]]
        self._is_html = attrs.get('html')

    def end_element(self, text):
        if self._is_html:
            return self._msg + [self._context.get_text_id(text)]
        else:
            return self._msg + [self._context.get_text_id(html_escape(text, replace_whitespace=False))]


class _StatusHandler(object):
    def __init__(self, context, attrs):
        self._context = context
        self._status = attrs.getValue('status')[0]
        self._starttime = self._context.timestamp(attrs.getValue('starttime'))
        self._endtime = self._context.timestamp(attrs.getValue('endtime'))

    def end_element(self, text):
        return [self._status,
                self._starttime,
                self._endtime-self._starttime]


class _RobotOutputHandler(ContentHandler):

    _handlers = {
        'msg' : _MsgHandler,
        'status' : _StatusHandler
    }


    def __init__(self, context):
        self._context = context
        self._handler_stack = []
        self._data = []

    @property
    def datamodel(self):
        return DataModel(self._context.basemillis, self._data, self._context.dump_texts())

    def startElement(self, name, attrs):
        handler = self._handlers[name](self._context,attrs)
        self._charbuffer = ''
        self._handler_stack.append(handler)

    def endElement(self, name):
        handler = self._handler_stack.pop()
        self._data = handler.end_element(self._charbuffer)

    def characters(self, content):
        self._charbuffer += content


class DataModel(object):

    def __init__(self, basemillis, robot_data, texts):
        self._basemillis = basemillis
        self._robot_data = robot_data
        self._texts = texts

    def write_to(self, output):
        output.write('window.basemillis = '+str(self._basemillis)+';\n')
        output.write('window.data = ')
        json.dump(self._robot_data, output, separators=(',', ':'))
        output.write(';\n')
        output.write('window.strings =')
        json.dump(self._texts, output, separators=(',', ':'))
        output.write(';\n')

def parse_js(input_filename, output):
    create_datamodel_from(input_filename).write_to(output)
