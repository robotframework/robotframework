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


from robot import utils


class _TableHelper:

    def _start_table(self, name, tag_column_name):
        self._writer.start('table', {'class': name})
        self._writer.start('tr')
        self._writer.element('th', 'Name', {'class': 'col_name'})
        self._writer.element('th', 'Documentation', {'class': 'col_doc'})
        self._writer.element('th', tag_column_name,
                             {'class': 'col_tags'}, escape=False)
        self._writer.element('th', 'Crit.', {'class': 'col_crit'})
        self._writer.element('th', 'Status', {'class': 'col_status'})
        self._writer.element('th', 'Message', {'class': 'col_msg'})
        self._writer.element('th', 'Start&nbsp;/&nbsp;Elapsed',
                             {'class': 'col_times'}, escape=False)
        self._writer.end('tr')

    def _test_row(self, test):
        self._start_suite_or_test_row(test, 'test')
        self._end_test_row(test)

    def _suite_row(self, suite):
        self._start_suite_or_test_row(suite, 'suite')
        self._end_suite_row(suite)

    def _start_suite_or_test_row(self, item, type_):
        self._writer.start('tr', {'class': '%s_row' % type_})
        self._writer.start('td', {'class': 'col_name'}, newline=False)
        self._write_name(item, type_)
        self._writer.end('td')
        self._writer.element('td', item.htmldoc, {'class': 'col_doc'},
                             escape=False)

    def _write_name(self, item, type_):
        attrs = {'id': '%s_%s' % (type_,item.longname), 'title': item.longname}
        if item.linkpath:
            elem = 'a'
            attrs['href'] = '%s#%s_%s' % (item.linkpath, type_, item.linkname)
        else:
            elem = 'span'
        self._writer.start(elem, attrs, newline=False)
        self._write_item_name(item, type_)
        self._writer.end(elem, newline=False)

    def _write_item_name(self, item, type_):
        name = type_ == 'suite' and item.longname or item.name
        return self._writer.content(name)

    def _end_test_row(self, test):
        self._writer.element('td', ', '.join(test.tags), {'class': 'col_tags'})
        self._writer.element('td', test.critical, {'class': 'col_crit'})
        self._writer.element('td', test.status,
                             {'class': 'col_status %s' % test.status.lower()})
        self._writer.element('td', test.message, {'class': 'col_msg'})
        self._writer.element('td', self._get_times(test),
                             {'class': 'col_times'}, escape=False)
        self._writer.end('tr')

    def _get_times(self, item):
        """Return start and elapsed time in html format without millis.

        Millis are stripped from start time but elapsed is rounded to closest
        second.
        """
        if item.starttime == 'N/A':
            start = 'N/A'
        else:
            start = item.starttime[:-4].replace(' ', '&nbsp;')
        if item.elapsedtime < 0:   # --CombinedTime NONE
            elapsed = '&nbsp;'
        else:
            rounded_millis = round(item.elapsedtime, -3)
            elapsed = utils.elapsed_time_to_string(rounded_millis)[:-4]
        return '%s<br />%s' % (start, elapsed)


class ReportSerializer(_TableHelper):
    end_test = start_keyword = end_keyword = message = lambda self, arg: None

    def __init__(self, output, logpath=None):
        self._writer = utils.HtmlWriter(output)
        self._loglink = logpath and \
                utils.get_link_path(logpath, output.name) or None
        self._suite_level = 0

    def start_suite(self, suite):
        self._suite_level += 1
        self._set_suite_link(suite)
        if self._suite_level == 1:
            self._writer.element('h2', 'Test Details by Suite')
            self._start_table('tests_by_suite', 'Metadata&nbsp;/&nbsp;Tags')
        self._suite_row(suite)

    def end_suite(self, suite):
        self._suite_level -= 1
        if self._suite_level == 0:
            self._writer.end('table')

    def start_test(self, test):
        self._set_test_link(test)
        self._test_row(test)

    def _set_suite_link(self, suite):
        # linkpath and linkname are also used when TagStats are serialized.
        # This is rather ugly and should be refactored at some point.
        suite.linkpath = self._loglink
        suite.linkname = suite.longname

    def _set_test_link(self, test):
        # Separate _set_test/suite_link methods are needed to allow overriding
        # them separately in SplitReportSerializer
        test.linkpath = self._loglink
        test.linkname = test.longname

    def _end_suite_row(self, suite):
        self._writer.start('td', {'class': 'col_tags'})
        for name, value in suite.get_metadata(html=True):
            self._writer.element('span', '%s: ' % name, {'class': 'meta_name'})
            self._writer.content(value, escape=False)
            self._writer.start_and_end('br')
        self._writer.end('td')
        self._writer.element('td', 'N/A', {'class': 'col_crit not_available'})
        self._writer.element('td', suite.status,
                             {'class': 'col_status %s' % suite.status.lower()})
        self._writer.element('td', suite.get_full_message(html=True),
                             {'class': 'col_msg'}, escape=False)
        self._writer.element('td', self._get_times(suite),
                             {'class': 'col_times'}, escape=False)
        self._writer.end('tr')


class SplitReportSerializer(ReportSerializer):

    def __init__(self, output, logpath, split_level):
        ReportSerializer.__init__(self, output, logpath)
        self._split_level = split_level
        self._namegen = utils.FileNameGenerator(self._loglink)

    def _set_suite_link(self, suite):
        if self._suite_level <= self._split_level:
            ReportSerializer._set_suite_link(self, suite)
        else:
            if self._suite_level == self._split_level + 1:
                self._split_loglink = self._namegen.get_name()
            self._set_split_link(suite)

    def _set_test_link(self, test):
        if self._suite_level <= self._split_level:
            ReportSerializer._set_test_link(self, test)
        else:
            self._set_split_link(test)

    def _set_split_link(self, item):
        item.linkpath = self._split_loglink
        item.linkname = item.get_long_name(self._split_level)


class TagDetailsSerializer(_TableHelper):

    def __init__(self, output):
        self._writer = utils.HtmlWriter(output)

    def start_tag_stats(self, stats):
        if stats.stats:
            self._writer.element('h2', 'Test Details by Tag')
            self._start_table('tests_by_tag', 'Tags')

    def end_tag_stats(self, stats):
        if stats.stats:
            self._writer.end('table')

    def tag_stat(self, stat):
        self._tag_row(stat)
        for test in stat.tests:
            self._test_row(test)

    def _write_item_name(self, stat, type_is_ignored):
        tokens = stat.get_long_name(separator=None)
        self._writer.element('span', ' . '.join(tokens[:-1]+['']),
                             {'class': 'parent_name'}, newline=False)
        self._writer.content(tokens[-1])

    def _tag_row(self, stat):
        self._writer.start('tr', {'class': 'tag_row'})
        self._writer.start('td', {'class': 'col_name'}, newline=False)
        self._writer.element('a', None, {'name': 'tag_%s' % stat.name},
                             newline=False)
        self._writer.content(stat.name)
        self._writer.end('td')
        doc = utils.html_escape(stat.get_doc() or '', formatting=True)
        self._writer.element('td', doc, {'class': 'col_doc'}, escape=False)
        self._writer.element('td', 'N/A', {'class': 'col_tags not_available'})
        self._writer.element('td', self._get_crit(stat), {'class': 'col_crit'})
        status = stat.failed == 0 and 'PASS' or 'FAIL'
        self._writer.element('td', status,
                             {'class': 'col_status %s' % status.lower()})
        self._writer.element('td', self._get_msg(stat.passed, stat.failed),
                             {'class': 'col_msg'}, escape=False)
        self._writer.element('td', self._get_elapsed(stat.tests),
                             {'class': 'col_times'})
        self._writer.end('tr')

    def _get_msg(self, passed, failed):
        total = passed + failed
        class_ = failed > 0 and ' class="fail"' or ''
        return '%d test%s, %d passed, <span%s>%d failed</span>' \
               % (total, utils.plural_or_not(total), passed, class_, failed)

    def _get_elapsed(self, tests):
        millis = sum([test.elapsedtime for test in tests])
        millis = round(millis, -3)  # millis not shown in report
        return utils.elapsed_time_to_string(millis)[:-4]

    def _get_crit(self, stat):
        if stat.critical:
            return 'crit.'
        if stat.non_critical:
            return 'non-c.'
        return ''
