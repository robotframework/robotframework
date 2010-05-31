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


class _StatSerializer:

    def __init__(self, output, split_level=-1):
        self._writer = utils.HtmlWriter(output)
        self._split_level = split_level

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
        doc = stat.get_doc(self._split_level)
        if doc:
            attrs['title'] = doc
        self._writer.start(elem, attrs, newline=False)
        return elem

    def _write_stat_name(self, stat):
        self._writer.content(stat.name)

    def _write_suite_stat_name(self, stat):
        tokens = stat.get_long_name(self._split_level, separator=None)
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
        percents = _Percents(stat.passed, stat.failed)
        pass_attrs = {'class': 'pass_bar',
                      'title': '%.1f%%' % percents.pass_percent,
                      'style': 'width: %.2f%%;' % percents.pass_width}
        fail_attrs = {'class': 'fail_bar',
                      'title': '%.1f%%' % percents.fail_percent,
                      'style': 'width: %.2f%%;' % percents.fail_width}
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


class LogStatSerializer(_StatSerializer):

    def _get_element_name_and_attrs(self, stat):
        if stat.type == 'suite':
            return 'a', self._get_link_attributes(stat)
        return 'span', {}

    def _get_link_attributes(self, stat):
        target = 'suite_%s' % stat.get_link(self._split_level)
        return {'href': '#' + target,
                'onclick': "set_element_visible('%s')" % target}


class SplitLogStatSerializer(LogStatSerializer):

    def __init__(self, output, split_level):
        LogStatSerializer.__init__(self, output, split_level=-1)
        self._split_border = split_level
        self._link_target = None
        self._namegen = utils.FileNameGenerator(os.path.basename(output.name))

    def _get_link_attributes(self, stat):
        border = self._before_after_or_on_split_border(stat)
        if border < 0:
            return LogStatSerializer._get_link_attributes(self, stat)
        if border == 0:
            self._link_target = self._namegen.get_name()
        return {'href': '%s#suite_%s' % (self._link_target,
                                         stat.get_link(self._split_border))}

    def _before_after_or_on_split_border(self, stat):
        tokens = stat.get_long_name(separator=None)
        return cmp(len(tokens), self._split_border+1)


class ReportStatSerializer(_StatSerializer):

    def _get_element_name_and_attrs(self, stat):
        if stat.type in ['suite', 'tag']:
            return 'a', {'href': '#%s_%s' % (stat.type, stat.get_link())}
        return 'span', {}


class SummaryStatSerializer(_StatSerializer):

    def _get_element_name_and_attrs(self, stat):
        return 'span', {}


class _Percents(object):

    def __init__(self, passed, failed):
        self.pass_percent, self.fail_percent \
            = self._calculate_percents(passed, failed)
        self.pass_width, self.fail_width \
            = self._calculate_widths(self.pass_percent, self.fail_percent)

    def _calculate_percents(self, passed, failed):
        total = passed + failed
        if total == 0:
            return 0.0, 0.0
        pass_percent = 100.0 * passed / total
        fail_percent = 100.0 * failed / total
        if 0 < pass_percent < 0.1:
            return 0.1, 99.9
        if 0 < fail_percent < 0.1:
            return 99.9, 0.1
        return round(pass_percent, 1), round(fail_percent, 1)

    def _calculate_widths(self, num1, num2):
        if num1 + num2 == 0:
            return 0.0, 0.0
        # Make small percentages better visible
        if 0 < num1 < 1:
            num1, num2= 1.0, 99.0
        if 0 < num2 < 1:
            num1, num2= 99.0, 1.0
        # Handle situation where both are rounded up
        while num1 + num2 > 100:
            num1, num2 = self._subtract_from_larger(num1, num2, 0.1)
        # Make sure both pass and fail bar fit into 100% also in IE
        num1, num2 = self._subtract_from_larger(num1, num2, 0.01)
        return num1, num2

    def _subtract_from_larger(self, num1, num2, subtr):
        if num1 > num2:
            return num1-subtr, num2
        return num1, num2-subtr
