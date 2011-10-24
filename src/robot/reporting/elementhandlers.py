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
        self._source = attrs.get('source', '')
        self._name = attrs.get('name')
        self._suites = []
        self._tests = []
        self._keywords = []
        self._current_children = None
        self._teardown_failed = False
        self._context.start_suite()

    def _get_name_and_sources(self):
        return self._get_ids(self._name, self._source,
                             self._context.get_rel_log_path(self._source))

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
        return self._get_name_and_sources() + self._data_from_children + \
                 [self._suites, self._tests, self._keywords,
                  int(self._teardown_failed), stats]


class _CombiningSuiteHandler(_SuiteHandler):

    def __init__(self, context, suite_name=None, suite_doc=None):
        self._total_stats = [{'label':'Critical Tests', 'fail':0, 'pass':0},
                            {'label': 'All Tests', 'fail':0, 'pass':0}]
        self._tag_stats = []
        self._tag_stats_by_label = {}
        self._suite_stats = []
        self._partial_suite_stats = []
        self._status = [1, None, 0]
        self.stats = [self._total_stats, self._tag_stats, self._suite_stats]
        _SuiteHandler.__init__(self, context, {})
        self._name = suite_name
        self._collect_name = suite_name is None
        self._source = ''
        self._data_from_children.append(self._get_id(suite_doc or ''))
        self._data_from_children.append([])

    def get_handler_for(self, name, attrs):
        return _Handler.get_handler_for(self, name, attrs)

    def add_child_data(self, data):
        if self._collect_name:
            self._update_name(data['stats'][2][0]['label'])
        self._suites.append(data['suite'])
        self._merge_stats(data['stats'])
        self._merge_status(data['suite'])

    def _update_name(self, new_name):
        if not self._name:
            self._name = new_name
        else:
            self._name = self._name+' & '+ new_name

    def _merge_status(self, suite):
        status = suite[5]
        self._status = [self._status[0] * status[0], None, self._status[2]+status[2]]

    def _merge_stats(self, stats):
        self._merge_total_stats(stats[0])
        self._merge_tag_stat(stats[1])
        self._partial_suite_stats += [stats[2]]

    def _merge_total_stats(self, total_stats):
        self._total_stats[0]['fail'] += total_stats[0]['fail']
        self._total_stats[0]['pass'] += total_stats[0]['pass']
        self._total_stats[1]['fail'] += total_stats[1]['fail']
        self._total_stats[1]['pass'] += total_stats[1]['pass']

    def _merge_tag_stat(self, tag_stats):
        for tag_stat in tag_stats:
            label = tag_stat['label']
            if label not in self._tag_stats_by_label:
                self._tag_stats_by_label[label] = tag_stat
                self._tag_stats += [tag_stat]
            else:
                self._tag_stats_by_label[label]['pass'] += tag_stat['pass']
                self._tag_stats_by_label[label]['fail'] += tag_stat['fail']

    def end_element(self, text):
        self._data_from_children.append(self._status)
        self._build_suite_stats()
        return _SuiteHandler.end_element(self, text)

    def _build_suite_stats(self):
        self._suite_stats += [{'label':self._name, 'fail':self._total_stats[1]['fail'], 'name':self._name, 'id':'s1', 'pass':self._total_stats[1]['pass']}]
        for index, stat in enumerate(self._partial_suite_stats):
            stat = stat[0]
            stat['label'] = self._name + '.' + stat['label']
            if 'id' in stat:
                stat['id'] = 's1-s%d' % (index+1) + stat['id'][2:]
            self._suite_stats += [stat]


class CombiningRobotHandler(_Handler):

    def __init__(self, context, main_suite_name, main_suite_doc):
        _Handler.__init__(self, context, None)
        self._combining_suite = _CombiningSuiteHandler(context,
                                                       main_suite_name,
                                                       main_suite_doc)

    def add_child_data(self, data):
        self._combining_suite.add_child_data(data)

    def end_element(self, text):
        return {'generator': 'rebot',
                'suite': self._combining_suite.end_element(''),
                'stats': self._combining_suite.stats,
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
