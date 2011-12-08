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

import csv
import re
from StringIO import StringIO

from robot.parsing.settings import Documentation
from robot import utils

from .formatters import TsvFormatter, TxtFormatter, PipeFormatter, HtmlFormatter
from .htmltemplate import TEMPLATE


def FileWriter(serialization_context):
    """Creates and returns a FileWriter object.

    :param serialization_context: Type of returned
        FileWriter is determined based on `serialization_context.format`.
        Is also passed along to created writer for further configuration.
    :type serialization_context: :py:class:`SerializationContext`
    """
    Writer = {
        'tsv': TsvFileWriter,
        'txt': TxtFileWriter,
        'html': HtmlFileWriter
    }[serialization_context.format]
    return Writer(serialization_context)

def TxtFileWriter(context):
    Writer = PipeSeparatedTxtWriter if context.pipe_separated else SpaceSeparatedTxtWriter
    return Writer(context)


class TsvFileWriter(object):

    def __init__(self, context):
        self._context = context
        self._writer = csv.writer(context.output, dialect='excel-tab',
                                  lineterminator=context.line_separator)
        self._formatter = TsvFormatter(8)

    def write(self, datafile):
        for table in datafile:
            if table:
                {'setting': self._write_table,
                 'variable': self._write_table,
                 'keyword': self._write_indented_table,
                 'testcase': self._write_indented_table}[table.type](table)
            self._write([])

    def close(self):
        pass

    def _write_table(self, table):
        self._write_header(table.header)
        for setting in table:
            self._write_item(setting)

    def _write_indented_table(self, table):
        self._write_header(table.header)
        for keyword in table:
            self._write([keyword.name])
            for item in keyword:
                self._write_item(item, indent=1)
                self._write_for_loop(item)

    def _write_header(self, header):
        self._writer.writerow(['*%s*' % cell for cell in header])

    def _write_item(self, item, indent=0):
        if item.is_set():
            self._write(item.as_list(), indent)

    def _write_for_loop(self, item):
        if item.is_for_loop():
            for sub_step in item:
                self._write_item(sub_step, indent=2)

    def _write(self, row, indent=0):
        for row in self._formatter.format(row, indent):
            self._writer.writerow(row)


class SpaceSeparatedTxtWriter(object):
    _separator = ' '*4
    _FIRST_ROW_LENGTH = 18

    def __init__(self, context):
        self._output = context.output
        self._line_separator = context.line_separator
        self._formatter = TxtFormatter()

    def close(self):
        pass

    def write(self, datafile):
        for table in datafile:
            if table:
                {'setting': self._write_settings,
                 'variable': self._write_table,
                 'keyword': self._write_indented_table,
                 'testcase': self._write_indented_table}[table.type](table)
            self._write([])

    def _write_settings(self, settings):
        self._write_header(settings.header)
        for setting in settings:
            self._write_item(setting, justifications=[14])

    def _write_table(self, table):
        self._write_header(table.header)
        for setting in table:
            self._write_item(setting)

    def _write_indented_table(self, table):
        if table.header[1:]:
            self._write_aligned_intended_table(table)
        else:
            self._write_unaligned_intended_table(table)

    def _write_aligned_intended_table(self, table):
        justifications = self._count_justifications(table)
        self._write_header(table.header, justifications)
        for keyword in table:
            self._write_keyword(justifications, keyword)

    def _write_keyword(self, justifications, keyword):
        # TODO: refactor
        elements = self._write_name_row(keyword, justifications)
        for item in elements:
            self._write_item(item, indent=1, justifications=justifications)
            self._write_for_loop(item)

    def _write_name_row(self, keyword, justifications):
        if len(keyword.name) > self._FIRST_ROW_LENGTH:
            self._write([keyword.name])
            return list(keyword)
        else:
            for index, step in enumerate(keyword):
                if step.is_set():
                    self._write([keyword.name]+step.as_list(), justifications=justifications)
                    return list(keyword)[index+1:]
            self._write([keyword.name])
            return []

    def _count_justifications(self, table):
        result = [self._FIRST_ROW_LENGTH]+[len(header) for header in table.header[1:]]
        for element in [list(kw) for kw in list(table)]:
            for step in element:
                for index, col in enumerate(step.as_list()):
                    index=index+1
                    if len(result) <= index:
                        result.append(0)
                    result[index] = max(len(col), result[index])
        return result

    def _write_unaligned_intended_table(self, table):
        self._write_header(table.header)
        for keyword in table:
            self._write([keyword.name])
            for item in keyword:
                self._write_item(item, indent=1)
                self._write_for_loop(item)

    def _write_item(self, item, indent=0, justifications=[]):
        if item.is_set():
            self._write(item.as_list(), indent, justifications)

    def _write_header(self, header, justifications=[]):
        self._write(['*** %s ***' % header[0]] + header[1:], justifications=justifications)

    def _write_for_loop(self, item):
        if item.is_for_loop():
            for sub_step in item:
               self._write_item(sub_step, indent=2)

    def _write(self, row, indent=0, justifications=[]):
        for row in self._formatter.format(row, indent, justifications):
            self._write_row(row)

    def _write_row(self, row):
        self._output.write(self._separator.join(row) + self._line_separator)


class PipeSeparatedTxtWriter(object):
    _separator = ' | '
    _FIRST_ROW_LENGTH = 18

    def __init__(self, context):
        self._output = context.output
        self._line_separator = context.line_separator
        self._formatter = PipeFormatter()

    def close(self):
        pass

    def write(self, datafile):
        for table in datafile:
            if table:
                {'setting': self._write_settings,
                 'variable': self._write_table,
                 'keyword': self._write_indented_table,
                 'testcase': self._write_indented_table}[table.type](table)
            self._write([])

    def _write_settings(self, settings):
        self._write_header(settings.header)
        for setting in settings:
            self._write_item(setting, justifications=[14])

    def _write_table(self, table):
        self._write_header(table.header)
        for setting in table:
            self._write_item(setting)

    def _write_indented_table(self, table):
        if table.header[1:]:
            self._write_aligned_intended_table(table)
        else:
            self._write_unaligned_intended_table(table)

    def _write_aligned_intended_table(self, table):
        justifications = self._count_justifications(table)
        self._write_header(table.header, justifications)
        for keyword in table:
            self._write_keyword(justifications, keyword)

    def _write_keyword(self, justifications, keyword):
        # TODO: refactor
        elements = self._write_name_row(keyword, justifications)
        for item in elements:
            self._write_item(item, indent=1, justifications=justifications)
            self._write_for_loop(item)

    def _write_name_row(self, keyword, justifications):
        if len(keyword.name) > self._FIRST_ROW_LENGTH:
            self._write([keyword.name])
            return list(keyword)
        else:
            for index, step in enumerate(keyword):
                if step.is_set():
                    self._write([keyword.name]+step.as_list(), justifications=justifications)
                    return list(keyword)[index+1:]
            self._write([keyword.name])
            return []

    def _count_justifications(self, table):
        result = [self._FIRST_ROW_LENGTH]+[len(header) for header in table.header[1:]]
        for element in [list(kw) for kw in list(table)]:
            for step in element:
                for index, col in enumerate(step.as_list()):
                    index=index+1
                    if len(result) <= index:
                        result.append(0)
                    result[index] = max(len(col), result[index])
        return result

    def _write_unaligned_intended_table(self, table):
        self._write_header(table.header)
        for keyword in table:
            self._write([keyword.name])
            for item in keyword:
                self._write_item(item, indent=1)
                self._write_for_loop(item)

    def _write_item(self, item, indent=0, justifications=[]):
        if item.is_set():
            self._write(item.as_list(), indent, justifications)

    def _write_header(self, header, justifications=[]):
        self._write(['*** %s ***' % header[0]] + header[1:], justifications=justifications)

    def _write_for_loop(self, item):
        if item.is_for_loop():
            for sub_step in item:
               self._write_item(sub_step, indent=2)

    def _write(self, row, indent=0, justifications=[]):
        for row in self._formatter.format(row, indent, justifications):
            self._write_row(row)

    def _write_row(self, row):
        row = self._separator.join(row)
        if row:
            row = '| ' + row + ' |'

        self._output.write(row + self._line_separator)


class HtmlFileWriter(object):
    _backslash_matcher = re.compile(r'(\\+)n ')

    def __init__(self, context):
        self._content = TEMPLATE % {'NAME': context.datafile.name}
        self._writer = utils.HtmlWriter(StringIO())
        self._output = context.output
        self._table_replacer = HtmlTableReplacer()
        self._formatter = HtmlFormatter()

    def close(self):
        self._output.write(self._content.encode('UTF-8'))

    def write(self, datafile):
        for table in datafile:
            if table:
                {'setting': self._write_settings,
                 'variable': self._write_variables,
                 'keyword': self._write_keywords,
                 'testcase': self._write_tests}[table.type](table)

    def _write_settings(self, settings):
        self._write_header('Settings')
        for row in self._formatter.setting_table(settings):
            self._write_row(row)
        self._end_table(self._table_replacer.settings_table)

    def _write_variables(self, variables):
        self._write_header('Variables')
        for v in variables:
            self.element(v)
        self._end_table(self._table_replacer.variables_table)

    def _write_tests(self, tests):
        self._write_header('Test Cases')
        self._write_steps(tests, 'test')
        self._end_table(self._table_replacer.testcases_table)

    def _write_keywords(self, keywords):
        self._write_header('Keywords')
        self._write_steps(keywords, 'keyword')
        self._end_table(self._table_replacer.keywords_table)

    def _write_steps(self, table, type_):
        for item in table:
            elems = [e for e in list(item) if e.is_set()]
            self._write_data([self._link_from_name(item.name, type_)] + elems[0].as_list(),
                              colspan=isinstance(elems[0], Documentation))
            for subitem in elems[1:]:
                self.element(subitem, indent=1)
                if subitem.is_for_loop():
                    for sub in subitem:
                        self._write_data(sub.as_list(), indent=2)

    def element(self, element, indent=0):
        if not element.is_set():
            return
        colspan = isinstance(element, Documentation)
        content = element.as_list()
        self._write_data(content, indent=indent, colspan=colspan)

    def _end_table(self, table_replacer):
        self._write_data([])
        table = self._writer.output.getvalue().decode('UTF-8')
        self._content = table_replacer(table, self._content)
        self._writer = utils.HtmlWriter(StringIO())

    def _write_header(self, header):
        self._writer.start('tr')
        attrs = {'class': 'name', 'colspan': '5'}
        self._writer.element('th', header, attrs)
        self._writer.end('tr')

    def _write_row(self, row):
        self._writer.start('tr')
        for cell in row:
            self._writer.element('td', cell.content, cell.attributes)
        self._writer.end('tr')

    def _write_data(self, data, indent=0, colspan=False):
        for row in self._formatter.format(data, indent, colspan):
            self._writer.start('tr', newline=True)
            for i, cell in enumerate(row):
                if i != 0:
                    cell = utils.html_escape(cell)
                cell = self._add_br_to_newlines(cell)
                attrs = self._get_attrs(i, len(row), colspan)
                self._writer.element('td', cell, attrs, escape=False)
            self._writer.end('tr')

    def _add_br_to_newlines(self, input):
        def replacer(match):
            backslash_count = len(match.group(1))
            if backslash_count % 2 == 1:
                return '%sn<br>\n' % match.group(1)
            return match.group()
        return self._backslash_matcher.sub(replacer, input)

    def _get_attrs(self, index, rowlength, colspan=True):
        if index == 0:
            return {'class': 'name'}
        if colspan and index == rowlength-1:
            num_cols = 5-index
            return {'colspan': str(num_cols),
                    'class': 'colspan%d' % num_cols}
        return {}

    def _link_from_name(self, name, type_):
        return '<a name="%s_%s">%s</a>' % (type_, utils.html_attr_escape(name),
                                           utils.html_escape(name))

class HtmlTableReplacer(object):
    _table_re = '(<table\s[^>]*id=["\']?%s["\']?[^>]*>).*?(</table>)'
    _settings_re = re.compile(_table_re % 'settings', re.IGNORECASE | re.DOTALL)
    _variables_re = re.compile(_table_re % 'variables', re.IGNORECASE | re.DOTALL)
    _testcases_re = re.compile(_table_re % 'testcases', re.IGNORECASE | re.DOTALL)
    _keywords_re = re.compile(_table_re % 'keywords', re.IGNORECASE | re.DOTALL)

    def settings_table(self, table, content):
        return self._table(self._settings_re, table, content)

    def variables_table(self, table, content):
        return self._table(self._variables_re, table, content)

    def testcases_table(self, table, content):
        return self._table(self._testcases_re, table, content)

    def keywords_table(self, table, content):
        return self._table(self._keywords_re, table, content)

    def _table(self, table_re, table, content):
        replaced = self._table_replacer(table)
        return table_re.sub(replaced, content)

    def _table_replacer(self, content):
        content = content.strip()
        def replace(match):
            start, end = match.groups()
            parts = content and [start, content, end] or [start, end]
            return '\n'.join(parts)
        return replace
