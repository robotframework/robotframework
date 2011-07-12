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
        self._name = attrs.get('name')
        self._source = attrs.get('source', '')
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
                 [self._context.dump_stats()]
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
        # Cannot use 'id' attribute in XML due to http://bugs.jython.org/issue1768
        if 'idx' in self._attrs:
            self._attrs['id'] = self._attrs.pop('idx')
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
