#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

import os.path

from robot import utils


class LogSerializer:

    def __init__(self, output, split_level=-1):
        self._writer = utils.HtmlWriter(output)
        self._writer.element('h2', 'Test Execution Log')
        self._idgen = utils.IdGenerator()
        self._suite_level = 0
        self._split_level = split_level

    def start_suite(self, suite):
        suite.id = self._idgen.get_id('suite')
        self._writer.start('table', {'class': 'suite', 'id': suite.id})
        self._write_suite_or_test_name(suite, 'suite')
        self._writer.start_many(['tr', 'td'])
        self._writer.start('div', {'class': 'indent',
                                   'style': self._get_display_style(suite),
                                   'id': '%s_children' % suite.id})
        self._write_suite_metadata(suite)
        self._suite_level += 1

    def end_suite(self, suite):
        self._writer.end_many(['div','td','tr','table'])
        self._suite_level -= 1

    def start_test(self, test):
        test.id = self._idgen.get_id('test')
        self._writer.start('table', {'class': 'test', 'id': test.id})
        self._write_suite_or_test_name(test, 'test')
        self._writer.start_many(['tr', 'td'])
        self._writer.start('div', {'class': 'indent',
                                   'style': self._get_display_style(test),
                                   'id': '%s_children' % test.id})
        self._write_test_metadata(test)

    def end_test(self, test):
        self._writer.end_many(['div','td','tr','table'])

    def start_keyword(self, kw):
        kw.id = self._idgen.get_id('kw')
        self._writer.start('table', {'class': 'keyword', 'id': kw.id})
        self._write_keyword_name(kw)
        self._writer.start('tr')
        self._writer.start('td', newline=True)
        self._writer.start('div', {'class': 'indent',
                                   'style': self._get_display_style(kw),
                                   'id': '%s_children' % kw.id})
        self._write_keyword_info(kw)

    def end_keyword(self, kw):
        self._writer.end_many(['div','td','tr','table'])

    def message(self, msg):
        self._writer.start('table', {'class': 'messages'})
        self._writer.start('tr')
        attrs = {'class': 'time'}
        if msg.level in ['WARN', 'ERROR']:
            # Allow linking from Test Execution Errors table
            attrs['id'] = 'msg_%s' % msg.get_timestamp(sep='_')
        self._writer.element('td', msg.time, attrs)
        self._writer.element('td', msg.level,
                             {'class': '%s level' % msg.level.lower()})
        self._writer.element('td', msg.message, {'class': 'msg'},
                             escape=not msg.html)
        self._writer.end_many(['tr', 'table'])

    def _write_suite_or_test_name(self, item, type_):
        self._writer.start_many(['tr', 'td'])
        self._write_expand_all(item)
        self._write_folding_button(item)
        label = type_ == 'suite' and 'TEST&nbsp;SUITE: ' or 'TEST&nbsp;CASE: '
        self._writer.element('span', label, {'class': item.status.lower()},
                             escape=False)
        name = item.get_long_name(self._split_level)
        self._writer.element('a', item.name, {'name': '%s_%s' % (type_, name),
                                              'class': 'name', 'title': name})
        self._writer.end_many(['td', 'tr'])

    def _write_expand_all(self, item):
        # Overridden by testdoc.py tool.
        attrs = {'href': "javascript:expand_all_children('%s')" % item.id,
                 'class': 'expand'}
        self._writer.element('a', 'Expand All', attrs)

    def _write_keyword_name(self, kw):
        self._writer.start('tr')
        self._writer.start('td')
        self._write_folding_button(kw)
        status = {'class': kw.status.lower()}
        if kw.type == 'for':
            self._writer.element('span', 'FOR ', status)
            self._writer.element('span', kw.name, {'class': 'arg'})
        elif kw.type == 'foritem':
            self._writer.element('span', 'VAR: ', status)
            self._writer.element('span', kw.name, {'class': 'arg'})
        else:
            kw_type = kw.type in ['setup','teardown'] and kw.type or 'keyword'
            self._writer.element('span', kw_type.upper()+': ', status)
            self._writer.element('span', kw.name+' ', {'class': 'name'})
            self._writer.element('span', ', '.join(kw.args), {'class': 'arg'})
        self._writer.end_many(['td', 'tr'])

    def _write_keyword_info(self, kw):
        self._writer.start('table', {'class': 'metadata'})
        doc = utils.html_escape(kw.doc, formatting=True)
        self._write_metadata_row('Documentation', doc, escape=False)
        self._write_metadata_row('Timeout', kw.timeout)
        self._write_times(kw)
        self._writer.end('table')

    def _write_folding_button(self, item):
        fold, unfold = self._is_element_open(item) and ('-','+') or ('+','-')
        onclk = "toggle_child_visibility('%s');" % item.id
        self._write_button(unfold, 'none', item.id+'_unfoldlink', onclk)
        self._write_button(fold, 'block', item.id+'_foldlink', onclk)

    def _write_button(self, label, display, id_, onclick):
        attrs = {'style': 'display: %s;' % display, 'class': 'foldingbutton',
                 'id': id_, 'onclick': onclick}
        self._writer.element('div', label, attrs)

    def _is_element_open(self, item):
        if item.status == 'FAIL':
            return True
        try:
            return item.all_stats.failed > 0 or self._suite_level == 0
        except AttributeError:
            return False

    def _get_display_style(self, item):
        style = self._is_element_open(item) and 'block' or 'none'
        return 'display: %s;' % style

    def _write_suite_metadata(self, suite):
        self._start_suite_or_test_metadata(suite)
        for name, value in suite.get_metadata(html=True):
            self._write_metadata_row(name, value, escape=False,
                                     escape_name=True, write_empty=True)
        self._write_source(suite.source)
        self._write_times(suite)
        self._write_metadata_row('Overall Status', suite.status,
                                 {'class': suite.status.lower()})
        self._write_metadata_row('Message', suite.get_full_message(html=True),
                                 escape=False)
        self._write_split_suite_details_link()
        self._writer.end('table')

    def _write_source(self, source):
        if source:
            if os.path.exists(source):
                ref = utils.get_link_path(source, self._writer.output.name)
                source = '<a href="%s">%s</a>' % (ref, source)
            self._write_metadata_row('Source', source, escape=False)

    def _write_test_metadata(self, test):
        self._start_suite_or_test_metadata(test)
        self._write_metadata_row('Timeout', test.timeout)
        self._write_metadata_row('Tags', ', '.join(test.tags))
        self._write_times(test)
        crit = test.critical == 'yes' and 'critical' or 'non-critical'
        self._write_metadata_row('Status', '%s (%s)' % (test.status, crit),
                                 {'class': test.status.lower()})
        self._write_metadata_row('Message', test.message)
        self._writer.end('table')

    def _start_suite_or_test_metadata(self, item):
        self._writer.start('table', {'class': 'metadata'})
        self._write_metadata_row('Full Name', item.longname)
        self._write_metadata_row('Documentation', item.htmldoc, escape=False)

    def _write_times(self, item):
        titles = '&nbsp;/&nbsp;'.join(['Start','End','Elapsed'])
        times = ' / '.join([item.starttime, item.endtime,
                            utils.elapsed_time_to_string(item.elapsedtime)])
        self._write_metadata_row(titles, times)

    def _write_metadata_row(self, name, value, attrs={}, escape=True,
                            escape_name=False, write_empty=False):
        if value or write_empty:
            self._writer.start('tr', newline=False)
            self._writer.element('th', name+':', escape=escape_name,
                                 newline=False)
            self._writer.element('td', value, attrs, escape=escape,
                                 newline=False)
            self._writer.end('tr')

    def _write_split_suite_details_link(self):
        pass


class SplitLogSerializer(LogSerializer):

    def __init__(self, output, split_level):
        LogSerializer.__init__(self, output, split_level)
        self._namegen = utils.FileNameGenerator(os.path.basename(output.name))

    def start_suite(self, suite):
        if self._suite_level <= self._split_level:
            LogSerializer.start_suite(self, suite)
        else:
            self._suite_level += 1

    def end_suite(self, suite):
        if self._suite_level <= self._split_level + 1:
            LogSerializer.end_suite(self, suite)
        else:
            self._suite_level -= 1

    def start_test(self, test):
        if self._suite_level <= self._split_level:
            LogSerializer.start_test(self, test)

    def end_test(self, test):
        if self._suite_level <= self._split_level:
            LogSerializer.end_test(self, test)

    def start_keyword(self, kw):
        if self._suite_level <= self._split_level:
            LogSerializer.start_keyword(self, kw)

    def end_keyword(self, kw):
        if self._suite_level <= self._split_level:
            LogSerializer.end_keyword(self, kw)

    def message(self, msg):
        if self._suite_level <= self._split_level:
            LogSerializer.message(self, msg)

    def _write_suite_or_test_name(self, item, type_):
        if type_ == 'test' or self._suite_level < self._split_level:
            LogSerializer._write_suite_or_test_name(self, item, type_)
        elif self._suite_level == self._split_level:
            self._write_split_suite_name(item)

    def _write_split_suite_name(self, suite):
        self._writer.start_many(['tr', 'td'])
        self._write_folding_button(suite)
        self._writer.element('span', 'TEST&nbsp;SUITE: ',
                             {'class': suite.status.lower()}, escape=False)
        link = '%s#suite_%s' % (self._namegen.get_name(), suite.name)
        self._writer.element('a', suite.name,
                             {'name': 'suite_%s' % suite.longname,
                              'href': link, 'class': 'splitname',
                              'title': suite.longname})
        self._writer.end_many(['td', 'tr'])

    def _write_split_suite_details_link(self):
        if self._suite_level == self._split_level:
            name = self._namegen.get_prev()
            link = '<a href="%s">%s</a>' % (name, name)
            self._write_metadata_row('Details', link, escape=False)


class ErrorSerializer:

    def __init__(self, output):
        self._writer = utils.HtmlWriter(output)

    def start_errors(self, errors):
        if errors.messages:
            self._writer.element('h2', 'Test Execution Errors')
            self._writer.start('table', {'class': 'errors'})

    def message(self, msg):
        self._writer.start('tr')
        self._writer.start('td', {'class': 'time'}, newline=False)
        self._write_timestamp(msg)
        self._writer.end('td')
        self._writer.element('td', msg.level,
                             {'class': '%s level' % msg.level.lower()})
        self._writer.element('td', msg.message, {'class': 'msg'})
        self._writer.end('tr')

    def _write_timestamp(self, msg):
        if msg.linkable:
            attrs = {'href': "#msg_%s" % msg.get_timestamp(sep='_'),
                     'onclick': "set_element_visible('msg_%s')" % msg.get_timestamp(sep='_'),
                     'title': 'Link to details.'}
            self._writer.start('a', attrs, newline=False)
        self._writer.content(msg.get_timestamp(sep='&nbsp;'), escape=False)
        if msg.linkable:
            self._writer.end('a', newline=False)

    def end_errors(self, errors):
        if errors.messages:
            self._writer.end('table')
