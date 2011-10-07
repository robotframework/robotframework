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


class _Handler(object):

    def __init__(self, context, attrs=None):
        self._context = context
        self._data_from_children = []
        self._handlers = {
            'robot'      : _RobotHandler,
            'suite'      : _SuiteHandler,
            'test'       : _TestHandler,
            'doc'        : _HtmlTextHandler,
            'kw'         : _KeywordHandler,
            'status'     : _StatusHandler,
            'arguments'  : _ArgumentsHandler,
            'arg'        : _ArgumentHandler,
            'tags'       : _Handler,
            'tag'        : _TextHandler,
            'metadata'   : _MetadataHandler,
            'item'       : _MetadataItemHandler,
            'msg'        : _MsgHandler,
            'statistics' : _StatisticsHandler,
            'stat'       : _StatItemHandler,
            'errors'     : _Handler
            }

    def get_handler_for(self, name, attrs):
        return self._handlers[name](self._context, attrs)

    def add_child_data(self, data):
        self._data_from_children.append(data)

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


class RootHandler(_Handler):

    @property
    def data(self):
        return self._data_from_children[0]


class _RobotHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._generator = attrs.get('generator').split()[0].lower()

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
        self._name_and_sources = self._get_name_and_sources(attrs)
        self._suites = []
        self._tests = []
        self._keywords = []
        self._current_children = None
        self._teardown_failed = False
        self._context.start_suite()

    def _get_name_and_sources(self, attrs):
        source = attrs.get('source', '')
        return self._get_ids(attrs.get('name'), source,
                             self._context.get_rel_log_path(source))

    def _set_teardown_failed(self):
        self._teardown_failed = True

    def get_handler_for(self, name, attrs):
        self._current_children = {
            'suite': self._suites,
            'test': self._tests,
            'kw': self._keywords
        }.get(name, self._data_from_children)
        if name == 'kw':
            return _SuiteSetupTeardownHandler(self._context, attrs,
                                              self._set_teardown_failed)
        return _Handler.get_handler_for(self, name, attrs)

    def add_child_data(self, data):
        self._current_children.append(data)

    def end_element(self, text):
        stats = self._context.end_suite()
        return self._name_and_sources + self._data_from_children + \
                 [self._suites, self._tests, self._keywords,
                  int(self._teardown_failed), stats]


class _CombiningSuiteHandler(_SuiteHandler):

    def __init__(self, context, attrs):
        self._name = 'Verysimple & Verysimple'
        _SuiteHandler.__init__(self, context, attrs)
        self._data_from_children.append(self._get_id(''))
        self._data_from_children.append([])

    def get_handler_for(self, name, attrs):
        return _Handler.get_handler_for(self, name, attrs)

    def add_child_data(self, data):
        self._suites.append(data['suite'])

    def _get_name_and_sources(self, attrs):
        return self._get_ids(self._name, '', '')

    def end_element(self, text):
        self._data_from_children.append([1, None, 250])
        return _SuiteHandler.end_element(self, text)


class CombiningRobotHandler(_Handler):

    def __init__(self, context, attrs=None):
        _Handler.__init__(self, context, attrs)
        self._combining_suite = _CombiningSuiteHandler(context, {})
        self._suite_ready = False

    def add_child_data(self, data):
        if self._suite_ready:
            _Handler.add_child_data(self, data)
        else:
            self._combining_suite.add_child_data(data)

    def get_handler_for(self, name, attrs):
        if name != 'robot':
            self._suite_ready = True
        return _Handler.get_handler_for(self, name, attrs)

    def end_element(self, text):
        return {'generator': 'rebot',
                'suite': self._combining_suite.end_element(''),
                'stats': [[{'label':'Critical Tests', 'fail':0, 'pass':4},
          {'label': 'All Tests', 'fail':0, 'pass':4}],
            [{'label':'t1', 'pass':2, 'fail':0},
             {'label':'t2', 'pass':2, 'fail':0}],
            [{'label':self._combining_suite._name,
              'fail':0, 'name':self._combining_suite._name, 'id':'s1', 'pass':4},
            {'label':'Verysimple & Verysimple.Verysimple',
             'fail':0, 'name':"Verysimple", 'id':'s1-s1', 'pass':2},
             {'label':'Verysimple & Verysimple.Verysimple',
             'fail':0, 'name':"Verysimple", 'id':'s1-s2', 'pass':2}]],
                'errors': [],
                'baseMillis': self._context.basemillis,
                'strings': self._context.dump_texts()}


class _TestHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._name = attrs.get('name')
        self._timeout = attrs.get('timeout')
        self._keywords = []
        self._current_children = None
        self._context.start_test()

    def get_handler_for(self, name, attrs):
        if name == 'status':
            self._critical = int(attrs.get('critical') == 'yes')
        self._current_children = {
            'kw': self._keywords
        }.get(name, self._data_from_children)
        return _Handler.get_handler_for(self, name, attrs)

    def add_child_data(self, data):
        self._current_children.append(data)

    def end_element(self, text):
        self._context.add_test(self._critical, self._last_child_passed())
        kws = self._context.end_test(self._keywords)
        return self._get_ids(self._name, self._timeout, self._critical) + \
                self._data_from_children + [kws]


class _KeywordHandler(_Handler):
    _types = {'kw': 0, 'setup': 1, 'teardown': 2, 'for': 3, 'foritem': 4}

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._type = self._types[attrs.get('type')]
        self._name = attrs.get('name')
        self._timeout = attrs.get('timeout')
        self._keywords = []
        self._messages = []
        self._current_children = None
        self._start()

    def _start(self):
        self._context.start_keyword()

    def get_handler_for(self, name, attrs):
        self._current_children = {
            'kw': self._keywords,
            'msg': self._messages
        }.get(name, self._data_from_children)
        return _Handler.get_handler_for(self, name, attrs)

    def add_child_data(self, data):
        self._current_children.append(data)

    def end_element(self, text):
        return self._get_ids(self._type, self._name, self._timeout) + \
                self._data_from_children + [self._get_keywords(), self._messages]

    def _get_keywords(self):
        self._context.end_keyword()
        return self._keywords


class _SuiteSetupTeardownHandler(_KeywordHandler):

    def __init__(self, context, attrs, teardown_failed_callback):
        _KeywordHandler.__init__(self, context, attrs)
        self._set_teardown_failed = teardown_failed_callback

    def _start(self):
        self._context.start_suite_setup_or_teardown()

    def end_element(self, text):
        if self._is_teardown() and not self._last_child_passed():
            self._context.suite_teardown_failed()
            self._set_teardown_failed()
        return _KeywordHandler.end_element(self, text)

    def _is_teardown(self):
        return self._type == 2

    def _get_keywords(self):
        return self._context.end_suite_setup_or_teardown(self._keywords)


class _StatusHandler(_Handler):
    _statuses = {'FAIL': 0, 'PASS': 1, 'NOT_RUN': 2}

    def __init__(self, context, attrs):
        self._context = context
        self._status = self._statuses[attrs.get('status')]
        self._starttime = self._context.timestamp(attrs.get('starttime'))
        self._elapsed = self._calculate_elapsed(attrs)

    def _calculate_elapsed(self, attrs):
        endtime = self._context.timestamp(attrs.get('endtime'))
        # Must compare against None because either start and end may be 0.
        if self._starttime is not None or endtime is not None:
            return endtime - self._starttime
        # Only RF 2.6+ outputs have elapsedtime when start or end is N/A.
        return int(attrs.get('elapsedtime', 0))

    def end_element(self, text):
        result = [self._status, self._starttime, self._elapsed]
        if text:
            result.append(text)
        return self._get_ids(*result)


class _ArgumentsHandler(_Handler):

    def end_element(self, text):
        return self._get_id(', '.join(self._data_from_children))


class _ArgumentHandler(_Handler):

    def end_element(self, text):
        return text


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
        return self._get_ids(self._name, utils.html_format(text))


class _MsgHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._msg = [self._context.timestamp(attrs.get('timestamp')),
                     LEVELS[attrs.get('level')]]
        self._is_html = attrs.get('html')
        self._is_linkable_in_error_table = attrs.get("linkable") == "yes"
        self._is_warning = attrs.get('level') == 'WARN'

    def end_element(self, text):
        self._msg.append(text if self._is_html else utils.html_escape(text))
        self._handle_warning_linking()
        return self._get_ids(*self._msg)

    def _handle_warning_linking(self):
        if self._is_linkable_in_error_table:
            self._msg.append(self._context.link_to(self._msg))
        elif self._is_warning:
            self._context.create_link_to_current_location(self._msg)


class _StatisticsHandler(_Handler):

    def get_handler_for(self, name, attrs):
        return _Handler(self._context, attrs)


class _StatItemHandler(_Handler):

    def __init__(self, context, attrs):
        _Handler.__init__(self, context)
        self._attrs = self._prune_empty_strings_from_attrs(dict(attrs))
        self._attrs['pass'] = int(self._attrs['pass'])
        self._attrs['fail'] = int(self._attrs['fail'])
        if 'doc' in self._attrs:
            self._attrs['doc'] = utils.html_format(self._attrs['doc'])
        # Cannot use 'id' attribute in XML due to http://bugs.jython.org/issue1768
        if 'idx' in self._attrs:
            self._attrs['id'] = self._attrs.pop('idx')

    def _prune_empty_strings_from_attrs(self, attrs):
        return dict((n, v) for n, v in attrs.iteritems() if v != '')

    def end_element(self, text):
        self._attrs.update(label=text)
        return self._attrs
