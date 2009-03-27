#  Copyright 2008 Nokia Siemens Networks Oyj
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
from robot.output import XmlLogger


class OutputSerializer(XmlLogger):
    
    def __init__(self, outpath, split):
        XmlLogger.__init__(self, outpath, 'TRACE', split, generator='Rebot')


class _StatisticsSerializer:

    def __init__(self, output):
        self._writer = utils.HtmlWriter(output)

    def start_statistics(self, statistics):
        self._writer.whole_element('h2', 'Test Statistics')

    def end_statistics(self, statistics):
        pass

    def start_total_stats(self, total_stats):
        self._statistics_table(total_stats, 'Total Statistics')

    def start_tag_stats(self, tag_stats):
        self._statistics_table(tag_stats, 'Statistics by Tag')

    def start_suite_stats(self, suite_stats):
        self._statistics_table(suite_stats, 'Statistics by Suite')

    def end_total_stats(self, total_stats):
        self._writer.end_element('table')

    end_tag_stats = end_suite_stats = end_total_stats

    def stat(self, stat):
        self._writer.start_element('tr')
        self._writer.start_element('td', {'class': 'col_stat_name'})
        self._stat_name(stat)
        if stat.type == 'tag':
            self._tag_stat_link(stat)
        self._writer.end_element('td')
        self._writer.whole_element('td', str(stat.passed + stat.failed), 
                                   {'class': 'col_stat'})
        self._writer.whole_element('td', stat.passed, {'class': 'col_stat'})
        self._writer.whole_element('td', stat.failed, {'class': 'col_stat'})
        self._writer.start_element('td', {'class': 'col_graph'})
        self._writer.start_element('div', {'class': 'graph'})
        pass_title, fail_title, pass_width, fail_width = self._get_percents(stat)
        self._writer.whole_element('b', None, {'class': 'pass_bar', 
                                               'style': 'width: %s;' % pass_width,
                                               'title': pass_title})
        self._writer.whole_element('b', None, {'class': 'fail_bar', 
                                               'style': 'width: %s;' % fail_width,
                                               'title': fail_title})
        self._writer.end_elements(['div', 'td', 'tr'])
        
    def _get_percents(self, stat):
        # See utils.percents_to_widths to understand why different title and 
        # width values are needed 
        percents = utils.calc_percents(stat.passed, stat.failed)
        pass_title, fail_title = [ '%.1f%%' % item for item in percents ]
        pass_width, fail_width = [ '%.2f%%' % item for item in 
                                   utils.percents_to_widths(*percents) ]
        return pass_title, fail_title, pass_width, fail_width

    def _statistics_table(self, statistics, title):
        self._writer.start_element('table', {'class': 'statistics'})
        self._writer.start_element('tr')
        self._writer.whole_element('th', title, {'class': 'col_stat_name'})
        self._writer.whole_element('th', 'Total', {'class': 'col_stat'})
        self._writer.whole_element('th', 'Pass', {'class': 'col_stat'})
        self._writer.whole_element('th', 'Fail', {'class': 'col_stat'})
        self._writer.whole_element('th', 'Graph', {'class': 'col_graph'})
        self._writer.end_element('tr')
        # processing tag stats but no tags specified
        if hasattr(statistics, 'stats') and statistics.stats == {}:
            self._no_tag_statistics()

    def _no_tag_statistics(self):
        self._writer.start_element('tr')
        self._writer.whole_element('td', 'No Tags', {'class': 'col_stat_name'})
        self._writer.whole_element('td', None, {'class': 'col_stat'})
        self._writer.whole_element('td', None, {'class': 'col_stat'})
        self._writer.whole_element('td', None, {'class': 'col_stat'})
        self._writer.start_element('td', {'class': 'col_graph'})
        self._writer.start_element('div', {'class': 'graph'})
        self._writer.whole_element('b', None, {'class': 'no_tags_bar', 
                                               'style': 'width: 100%;'})
        self._writer.end_elements(['div', 'td', 'tr'])

    def _stat_name(self, stat):
        self._writer.start_element('div', {'class': 'stat_name'}, newline=False)
        elem = self._get_element_name(stat)
        if elem == 'a':
            attrs = self._get_link_attributes(stat)
        else:
            attrs = {}
        if stat.doc is not None:
            attrs['title'] = stat.doc
        self._writer.whole_element(elem, stat.name, attrs, newline=False)
        self._write_criticality(stat)
        self._writer.end_element('div')
        
    def _get_element_name(self, stat):
        raise NotImplementedError
        
    def _get_link_attributes(self, stat):
        raise NotImplementedError
    
    def _write_criticality(self, stat):
        if stat.type == 'tag' and stat.critical is True:
            self._writer.content(' (critical)')
        if stat.type == 'tag' and stat.non_critical is True:
            self._writer.content(' (non-critical)')

    def _tag_stat_link(self, stat):
        self._writer.start_element('div', {'class': 'tag_links'})
        for item in stat.links:
            self._writer.start_element('span', newline=False)
            link, title = item
            self._writer.content('[')
            self._writer.whole_element('a', title, {'href': link}, newline=False)
            self._writer.content(']')
            self._writer.end_element('span')
        self._writer.end_element('div')


class LogStatisticsSerializer(_StatisticsSerializer):

    def _get_element_name(self, stat):
        return stat.type == 'suite' and 'a' or 'span'

    def _get_link_attributes(self, stat):
        target = '%s_%s' % (stat.type, stat.name)
        return { 'href': '#' + target, 
                 'onclick': "set_element_visible('%s')" % target }


class ReportStatisticsSerializer(_StatisticsSerializer):

    def _get_element_name(self, stat):
        return stat.type in ['suite', 'tag'] and 'a' or 'span'

    def _get_link_attributes(self, stat):
        return { 'href': '#%s_%s' % (stat.type, stat.name) }
    
    
class SummaryStatisticsSerializer(_StatisticsSerializer):

    def _get_element_name(self, stat):
        return 'span'
    

class SplitLogStatisticsSerializer(LogStatisticsSerializer):
    
    def __init__(self, output, split_level):
        LogStatisticsSerializer.__init__(self, output)
        self._namegen = utils.FileNameGenerator(os.path.basename(output.name))
        self._split_level = split_level
        self._in_suite_table = False
        
    def start_suite_stats(self, suite_stats):
        LogStatisticsSerializer.start_suite_stats(self, suite_stats)
        self._in_suite_table = True
        
    def end_suite_stats(self, suite_stats):
        LogStatisticsSerializer.end_suite_stats(self, suite_stats)
        self._in_suite_table = False
        
    def _get_link_attributes(self, stat):
        if not self._in_suite_table:
            return LogStatisticsSerializer._get_link_attributes(self, stat)
        level, name = self._get_suite_level_and_name(stat)
        if level <= self._split_level:
            return LogStatisticsSerializer._get_link_attributes(self, stat)
        if level == self._split_level + 1:
            self._link_target = self._namegen.get_name()
        return { 'href': '%s#%s_%s' % (self._link_target, stat.type, name) }

    def _get_suite_level_and_name(self, stat):
        level = 0
        tokens = stat.name.split('.')
        for item in tokens:
            level += 1 
            if len(item) > 1:
                break
        return level, '.'.join(tokens[self._split_level:])
    

class LogSyslogSerializer:
    
    def __init__(self, output):
        self._writer = utils.HtmlWriter(output)

    def start_syslog(self, syslog):
        if syslog.messages:
            self._writer.whole_element('h2', 'Test Execution Errors')
            self._writer.start_element('table', {'class': 'syslog'})

    def message(self, msg):
        self._writer.start_element('tr')
        timestamp = msg.timestamp.replace(' ', '&nbsp;')
        self._writer.whole_element('td', timestamp, {'class': 'time'}, 
                                   escape=False)
        level_class = '%s level' % (msg.level.lower())
        self._writer.whole_element('td', msg.level, {'class': level_class})
        self._writer.whole_element('td', msg.message, {'class': 'msg'})
        self._writer.end_element('tr')    

    def end_syslog(self, syslog):
        if syslog.messages:
            self._writer.end_element('table')


class LogSuiteSerializer:

    def __init__(self, output):
        self._writer = utils.HtmlWriter(output)
        self._writer.whole_element('h2', 'Test Execution Log')
        self._idgen = utils.IdGenerator()
        self._suite_level = 0

    def start_suite(self, suite):
        suite.id = self._idgen.get_id('suite')
        self._writer.start_element('table', {'class': 'suite', 'id': suite.id})
        self._write_suite_or_test_name(suite, 'suite')
        self._writer.start_elements(['tr', 'td'])
        self._writer.start_element('div', 
                                   {'class': 'indent', 
                                    'style': self._get_display_style(suite),
                                    'id': '%s_children' % suite.id})
        self._write_suite_metadata(suite)
        self._suite_level += 1
        
    def end_suite(self, suite):
        self._writer.end_elements(['div','td','tr','table'])
        self._suite_level -= 1
        
    def start_test(self, test):
        test.id = self._idgen.get_id('test')
        self._writer.start_element('table', {'class': 'test', 'id': test.id})
        self._write_suite_or_test_name(test, 'test')
        self._writer.start_elements(['tr', 'td'])
        self._writer.start_element('div', 
                                   {'class': 'indent', 
                                    'style': self._get_display_style(test),
                                    'id': '%s_children' % test.id})
        self._write_test_metadata(test)
    
    def end_test(self, test):
        self._writer.end_elements(['div','td','tr','table'])
     
    def start_keyword(self, kw):
        kw.id = self._idgen.get_id('kw')
        self._writer.start_element('table', {'class': 'keyword'})
        self._write_keyword_name(kw)
        self._writer.start_element('tr', {'id': kw.id})
        self._writer.start_element('td', newline=True)
        self._writer.start_element('div', {'class': 'indent', 
                                           'style': self._get_display_style(kw),
                                           'id': '%s_children' % kw.id})
        self._write_keyword_info(kw)

    def end_keyword(self, kw):
        self._writer.end_elements(['div','td','tr','table'])

    def message(self, msg):
        self._writer.start_element('table', {'class': 'messages'})
        self._writer.start_element('tr')
        timestamp = msg.timestamp.split()[1]   # don't log date
        self._writer.whole_element('td', timestamp, {'class': 'time'})
        level_class = '%s level' % (msg.level.lower())
        self._writer.whole_element('td', msg.level, {'class': level_class})
        self._writer.whole_element('td', msg.message, {'class': 'msg'}, escape=not msg.html)
        self._writer.end_elements(['tr', 'table'])    

    def _write_suite_or_test_name(self, item, type_):
        self._writer.start_elements(['tr', 'td'])
        self._write_expand_all(item)
        self._write_folding_button(item)
        label = type_ == 'suite' and 'TEST&nbsp;SUITE: ' or 'TEST&nbsp;CASE: '
        self._writer.whole_element('span', label,
                                   {'class': item.status.lower()}, escape=False)
        self._writer.whole_element('a', item.name, 
                                   {'name': '%s_%s' % (type_, item.mediumname),
                                    'class': 'name', 'title': item.longname})
        self._writer.end_elements(['td', 'tr'])
        
    def _write_expand_all(self, item):
        # Overridden by testdoc.py tool.
        attrs = { 'href': "javascript:expand_all_children('%s')" % item.id,
                  'class': 'expand' }
        self._writer.whole_element('a', 'Expand All', attrs)
        
    def _write_keyword_name(self, kw):
        self._writer.start_element('tr', {'id': kw.id})
        self._writer.start_element('td')
        self._write_folding_button(kw)
        status = {'class': kw.status.lower()}
        if kw.type == 'for':
            self._writer.whole_element('span', 'FOR ', status)
            self._writer.whole_element('span', kw.name, {'class': 'arg'})
        elif kw.type == 'foritem':
            self._writer.whole_element('span', 'VAR: ', status)
            self._writer.whole_element('span', kw.name, {'class': 'arg'})
        elif kw.type == 'parallel':
            self._writer.whole_element('span', 'PARALLEL:', status)
        else:
            kw_type = kw.type in ['setup','teardown'] and kw.type.upper() or 'KEYWORD'
            self._writer.whole_element('span', kw_type+': ', status)
            self._writer.whole_element('span', kw.name+' ', {'class': 'name'})
            self._writer.whole_element('span', u', '.join(kw.args), {'class': 'arg'})
        self._writer.end_elements(['td', 'tr'])
        
    def _write_keyword_info(self, kw):
        self._writer.start_element('table', {'class': 'metadata'})
        doc = utils.html_escape(kw.doc, formatting=True)
        self._write_metadata_row('Documentation', doc, escape=False)
        self._write_metadata_row('Timeout', kw.timeout)
        self._write_times(kw)
        self._writer.end_element('table')
        
    def _write_folding_button(self, item):
        fold, unfold = self._is_element_open(item) and ('-','+') or ('+','-')
        onclk = "toggle_child_visibility('%s');" % item.id
        self._write_button(unfold, 'none', item.id+'_unfoldlink', onclk)
        self._write_button(fold, 'block', item.id+'_foldlink', onclk)
        
    def _write_button(self, label, display, id_, onclick):
        attrs = { 'style': 'display: %s;' % display, 'class': 'foldingbutton', 
                  'id': id_, 'onclick': onclick }
        self._writer.whole_element('div', label, attrs)
        
    def _is_element_open(self, item):
        if item.status == 'FAIL':
            return True
        try:
            return item.all_stats.failed > 0 or self._suite_level == 0
        except AttributeError:
            return False

    def _get_display_style(self, item):
        style = self._is_element_open(item) and 'block' or 'none'
        return 'display: %s;' % (style)

    def _write_suite_metadata(self, suite):
        self._start_suite_or_test_metadata(suite)
        for name, value in suite.get_metadata(html=True):
            self._write_metadata_row(name, value, escape=False, write_empty=True)
        if suite.source:
            if os.path.exists(suite.source):
                path = '<a href="%s">%s</a>' % (suite.source, suite.source)
            else:
                path = suite.source
            self._write_metadata_row('Source', path, escape=False)
        self._write_times(suite)
        self._write_metadata_row('Overall Status', suite.status, 
                                 {'class': suite.status.lower()})
        self._write_metadata_row('Message', suite.get_full_message(html=True),
                                 escape=False)
        self._write_split_suite_details_link()
        self._writer.end_element('table')

    def _write_test_metadata(self, test):
        self._start_suite_or_test_metadata(test)
        self._write_metadata_row('Timeout', test.timeout)
        self._write_metadata_row('Tags', ', '.join(test.tags))
        self._write_times(test)
        crit = test.critical == 'yes' and 'critical' or 'non-critical'
        self._write_metadata_row('Status', '%s (%s)' % (test.status, crit), 
                                 {'class': test.status.lower()})
        self._write_metadata_row('Message', test.message)
        self._writer.end_element('table')

    def _start_suite_or_test_metadata(self, item):
        self._writer.start_element('table', {'class': 'metadata'})
        self._write_metadata_row('Full Name', item.longname)
        self._write_metadata_row('Documentation', item.htmldoc, escape=False)

    def _write_times(self, item):
        times = [item.starttime, item.endtime, item.elapsedtime]
        self._write_metadata_row('Start / End / Elapsed', '  /  '.join(times))

    def _write_metadata_row(self, name, value, attrs={}, escape=True,
                            write_empty=False):
        if value or write_empty:
            self._writer.start_element('tr', newline=False)
            self._writer.whole_element('th', name+':', escape=False, newline=False)
            self._writer.whole_element('td', value, attrs, escape=escape, newline=False)
            self._writer.end_element('tr')

    def _write_split_suite_details_link(self):
        pass


class SplitLogSuiteSerializer(LogSuiteSerializer):

    def __init__(self, output, split_level):
        LogSuiteSerializer.__init__(self, output)
        self._split_level = split_level
        self._namegen = utils.FileNameGenerator(os.path.basename(output.name))
        
    def start_suite(self, suite):
        if self._suite_level <= self._split_level:
            LogSuiteSerializer.start_suite(self, suite)
        else:
            self._suite_level += 1
        
    def end_suite(self, suite):
        if self._suite_level <= self._split_level + 1:
            LogSuiteSerializer.end_suite(self, suite)
        else:
            self._suite_level -= 1

    def start_test(self, test):
        if self._suite_level <= self._split_level:
            LogSuiteSerializer.start_test(self, test)
            
    def end_test(self, test):
        if self._suite_level <= self._split_level:
            LogSuiteSerializer.end_test(self, test)
            
    def start_keyword(self, kw):
        if self._suite_level <= self._split_level:
            LogSuiteSerializer.start_keyword(self, kw)
            
    def end_keyword(self, kw):
        if self._suite_level <= self._split_level:
            LogSuiteSerializer.end_keyword(self, kw)
    
    def message(self, msg):
        if self._suite_level <= self._split_level:
            LogSuiteSerializer.message(self, msg)
            
    def _write_suite_or_test_name(self, item, type_):
        if type_ == 'test' or self._suite_level < self._split_level:
            LogSuiteSerializer._write_suite_or_test_name(self, item, type_)
        elif self._suite_level == self._split_level:
            self._write_split_suite_name(item)
            
    def _write_split_suite_name(self, suite):
        self._writer.start_elements(['tr', 'td'])
        self._write_folding_button(suite)
        self._writer.whole_element('span', 'TEST&nbsp;SUITE: ',
                                   {'class': suite.status.lower()}, 
                                   escape=False)
        link = '%s#suite_%s' % (self._namegen.get_name(), suite.name)
        self._writer.whole_element('a', suite.name, 
                                   {'name': 'suite_%s' % (suite.mediumname),
                                    'href': link,
                                    'class': 'splitname',
                                    'title': suite.longname})
        self._writer.end_elements(['td', 'tr'])
    
    def _write_split_suite_details_link(self):
        if self._suite_level == self._split_level:
            name = self._namegen.get_prev()
            link = '<a href="%s">%s</a>' % (name, name)
            self._write_metadata_row('Details', link, escape=False)
        

class _ReportTableHelper:

    def _start_table(self, name, tag_column_name):
        self._writer.start_element('table', {'class': name})
        self._writer.start_element('tr')
        self._writer.whole_element('th', 'Name', {'class': 'col_name'})
        self._writer.whole_element('th', 'Documentation', {'class': 'col_doc'})
        self._writer.whole_element('th', tag_column_name, 
                                   {'class': 'col_tags'}, escape=False)
        self._writer.whole_element('th', 'Crit.', {'class': 'col_crit'})
        self._writer.whole_element('th', 'Status', {'class': 'col_status'})
        self._writer.whole_element('th', 'Message', {'class': 'col_msg'})
        self._writer.whole_element('th', 'Start&nbsp;/&nbsp;Elapsed', 
                                   {'class': 'col_times'}, escape=False)
        self._writer.end_element('tr')

    def _test_row(self, test):
        self._start_suite_or_test_row(test, 'test')
        self._end_test_row(test)

    def _suite_row(self, suite):
        self._start_suite_or_test_row(suite, 'suite')
        self._end_suite_row(suite)

    def _start_suite_or_test_row(self, item, type_):
        self._writer.start_element('tr', {'class': '%s_row' % type_})
        self._writer.start_element('td', {'class': 'col_name'}, newline=False)
        elem, attrs = self._get_name_params(item, type_)
        self._writer.whole_element(elem, item.mediumname, attrs, newline=False)        
        self._writer.end_element('td')
        self._writer.whole_element('td', item.htmldoc, {'class': 'col_doc'}, 
                                   escape=False)

    def _get_name_params(self, item, type_):
        attrs = { 'id' : '%s_%s' % (type_, item.mediumname),
                  'title' : item.longname }
        if item.linkpath is not None:
            elem = 'a'
            attrs['href'] = '%s#%s_%s' % (item.linkpath, type_, item.linkname)
        else:
            elem = 'span'
        return elem, attrs

    def _end_test_row(self, test):
        self._writer.whole_element('td', ', '.join(test.tags), {'class': 'col_tags'})
        self._writer.whole_element('td', test.critical, {'class': 'col_crit'})
        self._writer.whole_element('td', test.status, 
                                   {'class': 'col_status %s' % test.status.lower()})
        self._writer.whole_element('td', test.message, {'class': 'col_msg'})
        self._writer.whole_element('td', self._get_times(test), 
                                   {'class': 'col_times'}, escape=False )
        self._writer.end_element('tr')

    def _get_times(self, item):
        """Return start and elapsed time in html format without millis.
        
        Millis are stripped from start time but elapsed is rounded to closest
        second.
        """
        if item.starttime == 'N/A':
            start = 'N/A'
        else:
            start = item.starttime[:-4].replace(' ', '&nbsp;')
        if item.elapsedmillis < 0:   # --CombinedTime NONE
            elapsed = '&nbsp;'
        else:
            rounded_millis = round(item.elapsedmillis, -3)
            elapsed = utils.elapsed_millis_to_string(rounded_millis)[:-4]
        return '%s<br />%s' % (start, elapsed)


class ReportSuiteSerializer(_ReportTableHelper):

    end_test = start_keyword = end_keyword = message = lambda self, arg : None

    def __init__(self, output, logpath=None):
        self._writer = utils.HtmlWriter(output)
        self._loglink = logpath is not None and \
                utils.get_link_path(logpath, output.name) or None
        self._suite_level = 0
        
    def start_suite(self, suite):
        self._suite_level += 1
        self._set_suite_link(suite)
        if self._suite_level == 1:
            self._writer.whole_element('h2', 'Test Details by Suite')
            self._start_table('tests_by_suite', 'Metadata&nbsp;/&nbsp;Tags')
        self._suite_row(suite)
        
    def end_suite(self, suite):
        self._suite_level -= 1
        if self._suite_level == 0:
            self._writer.end_element('table')    

    def start_test(self, test):
        self._set_test_link(test)
        self._test_row(test)
        
    def _set_suite_link(self, suite):
        # linkpath and linkname are also used when TagStats are serialized.
        # This is rather ugly and should be refactored at some point.
        suite.linkpath = self._loglink
        suite.linkname = suite.mediumname
        
    def _set_test_link(self, test):
        # Separate _set_test/suite_link methods are needed to allow overriding
        # them separately in SplitReportSuiteSerializer
        test.linkpath = self._loglink
        test.linkname = test.mediumname
            
    def _end_suite_row(self, suite):
        self._writer.start_element('td', {'class': 'col_tags'})
        for name, value in suite.get_metadata(html=True):
            self._writer.whole_element('span', '%s: ' % name, 
                                       {'class': 'meta_name'})
            self._writer.content(value, escape=False)
            self._writer.start_and_end_element('br')
        self._writer.end_element('td')
        self._writer.whole_element('td', 'N/A', {'class': 'col_crit not_available'})
        self._writer.whole_element('td', suite.status, 
                                   {'class': 'col_status %s' % suite.status.lower()})
        self._writer.whole_element('td', suite.get_full_message(html=True),
                                   {'class': 'col_msg'}, escape=False)
        self._writer.whole_element('td', self._get_times(suite),
                                   {'class': 'col_times'}, escape=False)
        self._writer.end_element('tr')

    
class SplitReportSuiteSerializer(ReportSuiteSerializer):
    
    def __init__(self, output, logpath, split_level):
        ReportSuiteSerializer.__init__(self, output, logpath)
        self._split_level = split_level
        self._namegen = utils.FileNameGenerator(self._loglink)
        
    def _set_suite_link(self, suite):
        if self._suite_level <= self._split_level:
            ReportSuiteSerializer._set_suite_link(self, suite)
        else:
            if self._suite_level == self._split_level + 1:
                self._split_loglink = self._namegen.get_name()
            self._set_split_link(suite)
        
    def _set_test_link(self, test):
        if self._suite_level <= self._split_level:
            ReportSuiteSerializer._set_test_link(self, test)
        else:
            self._set_split_link(test)

    def _set_split_link(self, item):
        item.linkpath = self._split_loglink
        tokens = item.mediumname.split('.')
        item.linkname = '.'.join(tokens[self._split_level:])

    
class ReportTagStatSerializer(_ReportTableHelper):
    
    def __init__(self, output):
        self._writer = utils.HtmlWriter(output)
    
    def start_tag_stats(self, stats):
        if stats.stats != {}:
            self._writer.whole_element('h2', 'Test Details by Tag')
            self._start_table('tests_by_tag', 'Tags')

    def end_tag_stats(self, stats):
        if stats.stats != {}:
            self._writer.end_element('table')

    def stat(self, stat):
        self._tag_row(stat)
        for test in stat.tests:
            self._test_row(test)

    def _tag_row(self, stat):
        self._writer.start_element('tr', {'class': 'tag_row'})
        self._writer.start_element('td', {'class': 'col_name'}, newline=False)
        self._writer.whole_element('a', None, {'name': 'tag_%s' % stat.name},
                                   newline=False)
        self._writer.content(stat.name)
        self._writer.end_element('td')
        doc = stat.doc is not None and utils.html_escape(stat.doc, True) or ''
        self._writer.whole_element('td', doc, {'class': 'col_doc'}, escape=False)
        self._writer.whole_element('td', 'N/A', {'class': 'col_tags not_available'})
        self._writer.whole_element('td', self._get_crit(stat), {'class': 'col_crit'})
        status = stat.failed == 0 and 'PASS' or 'FAIL'
        self._writer.whole_element('td', status, 
                                   {'class': 'col_status %s' % status.lower()})
        self._writer.whole_element('td', self._get_msg(stat.passed, stat.failed), 
                                   {'class': 'col_msg'}, escape=False)
        self._writer.whole_element('td', self._get_elapsed(stat.tests),
                                   {'class': 'col_times'})
        self._writer.end_element('tr')
        
    def _get_msg(self, passed, failed):
        total = passed + failed
        class_ = failed > 0 and ' class="fail"' or ''
        return '%d test%s, %d passed, <span%s>%d failed</span>' % (total,
                utils.plural_or_not(total), passed, class_, failed)
        
    def _get_elapsed(self, tests):
        millis = sum([test.elapsedmillis for test in tests])
        millis = round(millis, -3)  # millis not shown in report
        return utils.elapsed_millis_to_string(millis)[:-4]
        
    def _get_crit(self, stat):
        if stat.critical:
            return 'crit.'
        if stat.non_critical:
            return 'non-c.'
        return ''
