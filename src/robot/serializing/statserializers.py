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


class _StatSerializer:

    def __init__(self, output):
        self._writer = utils.HtmlWriter(output)

    def start_statistics(self, statistics):
        self._writer.element('h2', 'Test Statistics')

    def end_statistics(self, statistics):
        pass

    def start_total_stats(self, total_stats):
        self._statistics_table(total_stats, 'Total Statistics')

    def start_tag_stats(self, tag_stats):
        self._statistics_table(tag_stats, 'Statistics by Tag')

    def start_suite_stats(self, suite_stats):
        self._statistics_table(suite_stats, 'Statistics by Suite')

    def end_total_stats(self, total_stats):
        self._writer.end('table')

    end_tag_stats = end_suite_stats = end_total_stats

    def total_stat(self, stat):
        elem = self._start_stat_name(stat)
        self._write_stat_name(stat)
        self._end_stat_name(elem)
        self._write_numbers_and_graph(stat)

    def suite_stat(self, stat):
        elem = self._start_stat_name(stat)
        self._write_suite_stat_name(stat)
        self._end_stat_name(elem)
        self._write_numbers_and_graph(stat)

    def tag_stat(self, stat):
        elem = self._start_stat_name(stat)
        self._write_stat_name(stat)
        self._end_tag_stat_name(elem, stat)
        self._write_numbers_and_graph(stat)

    def _start_stat_name(self, stat):
        self._writer.start('tr')
        self._writer.start('td', {'class': 'col_stat_name'})
        self._writer.start('div', {'class': 'stat_name'}, newline=False)
        elem, attrs = self._get_element_name_and_attrs(stat)
        doc = self._get_doc(stat)
        if doc:
            attrs['title'] = doc
        self._writer.start(elem, attrs, newline=False)
        return elem

    def _write_stat_name(self, stat):
        self._writer.content(self._get_name(stat))

    def _write_suite_stat_name(self, stat):
        # TODO:
        # 1) Should handle also split levels
        # 2) Can _get_name be removed?
        # 3) Can mediumname be removed altogether??
        tokens = stat._suite.get_long_name(separator=None)
        if len(tokens) > 1:
            self._writer.element('span', ' . '.join(tokens[:-1]+['']),
                                 {'class': 'parent_name'}, newline=False)
        self._writer.content(tokens[-1])

    def _end_stat_name(self, elem):
        self._writer.end(elem, newline=False)
        self._writer.end('div')
        self._writer.end('td')

    def _end_tag_stat_name(self, elem, stat):
        self._writer.end(elem, newline=False)
        self._write_tag_criticality(stat)
        self._writer.end('div')
        self._write_tag_stat_link(stat)
        self._writer.end('td')

    def _write_numbers_and_graph(self, stat):
        self._writer.element('td', stat.passed + stat.failed,
                             {'class': 'col_stat'})
        self._writer.element('td', stat.passed, {'class': 'col_stat'})
        self._writer.element('td', stat.failed, {'class': 'col_stat'})
        self._writer.start('td', {'class': 'col_graph'})
        self._writer.start('div', {'class': 'graph'})
        self._write_graph(stat)
        self._writer.end_many(['div', 'td', 'tr'])
        
    def _write_graph(self, stat):
        # See utils.percents_to_widths to understand why different percent and 
        # width values are needed 
        percents = utils.calc_percents(stat.passed, stat.failed)
        widths = utils.percents_to_widths(*percents)
        pass_attrs = {'class': 'pass_bar', 'title': '%.1f%%' % percents[0],
                      'style': 'width: %.2f%%;' % widths[0]}
        fail_attrs = {'class': 'fail_bar', 'title': '%.1f%%' % percents[1],
                      'style': 'width: %.2f%%;' % widths[1]}
        self._writer.element('b', None, pass_attrs)
        self._writer.element('b', None, fail_attrs)

    def _statistics_table(self, statistics, title):
        self._writer.start('table', {'class': 'statistics'})
        self._writer.start('tr')
        self._writer.element('th', title, {'class': 'col_stat_name'})
        self._writer.element('th', 'Total', {'class': 'col_stat'})
        self._writer.element('th', 'Pass', {'class': 'col_stat'})
        self._writer.element('th', 'Fail', {'class': 'col_stat'})
        self._writer.element('th', 'Graph', {'class': 'col_graph'})
        self._writer.end('tr')
        # processing tag stats but no tags specified
        if hasattr(statistics, 'stats') and statistics.stats == {}:
            self._no_tag_statistics()

    def _no_tag_statistics(self):
        self._writer.start('tr')
        self._writer.element('td', 'No Tags', {'class': 'col_stat_name'})
        self._writer.element('td', None, {'class': 'col_stat'})
        self._writer.element('td', None, {'class': 'col_stat'})
        self._writer.element('td', None, {'class': 'col_stat'})
        self._writer.start('td', {'class': 'col_graph'})
        self._writer.start('div', {'class': 'graph'})
        self._writer.element('b', None, {'class': 'no_tags_bar', 
                                         'style': 'width: 100%;'})
        self._writer.end_many(['div', 'td', 'tr'])

    def _get_doc(self, stat):
        return stat.get_doc()

    def _get_name(self, stat):
        return stat.get_name()
            
    def _write_tag_criticality(self, stat):
        if stat.critical:
            self._writer.content(' (critical)')
        if stat.non_critical:
            self._writer.content(' (non-critical)')

    def _write_tag_stat_link(self, stat):
        self._writer.start('div', {'class': 'tag_links'})
        for link, title in stat.links:
            self._writer.start('span', newline=False)
            self._writer.content('[')
            self._writer.element('a', title, {'href': link}, newline=False)
            self._writer.content(']')
            self._writer.end('span')
        self._writer.end('div')


class _BaseLogStatSerializer(_StatSerializer):

    def __init__(self, output, split_level=-1):
        _StatSerializer.__init__(self, output)
        self._split_level = split_level

    def _get_element_name_and_attrs(self, stat):
        if stat.type == 'suite':
            return 'a', self._get_link_attributes(stat)
        return 'span', {}

    def _get_link_attributes(self, stat):
        target = '%s_%s' % (stat.type, stat.get_link(self._split_level))
        return {'href': '#' + target,
                'onclick': "set_element_visible('%s')" % target}
        

class LogStatSerializer(_BaseLogStatSerializer):

    def _get_doc(self, stat):
        return stat.get_doc(self._split_level)

    def _get_name(self, stat):
        return stat.get_name(self._split_level)


class SplitLogStatSerializer(_BaseLogStatSerializer):
    
    def __init__(self, output, split_level):
        _BaseLogStatSerializer.__init__(self, output, split_level)
        self._namegen = utils.FileNameGenerator(os.path.basename(output.name))
                
    def _get_link_attributes(self, stat):        
        if stat.should_link_to_sub_log(self._split_level):
            return {'href': '%s#%s_%s' % (self._namegen.get_name(), stat.type, 
                                          stat.get_link(self._split_level))}
        return _BaseLogStatSerializer._get_link_attributes(self, stat)


class ReportStatSerializer(_StatSerializer):

    def _get_element_name_and_attrs(self, stat):
        if stat.type in ['suite', 'tag']:
            return 'a', {'href': '#%s_%s' % (stat.type, stat.get_link())}
        return 'span', {}


class SummaryStatSerializer(_StatSerializer):

    def _get_element_name_and_attrs(self, stat):
        return 'span', {}
