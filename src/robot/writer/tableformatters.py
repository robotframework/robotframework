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

import re

from robot.parsing.settings import Documentation
from robot import utils


class _Formatter(object):

    def _rows_from_simple_table(self, item, indent=0):
        return self._rows_from_item(item, indent)

    def _rows_from_indented_table(self, table):
        for item in table:
            yield self._format_name(item)
            for row in self._rows_from_item(item, 1):
                yield row

    def _rows_from_item(self, item, indent=0):
        for child in (c for c in item if c.is_set()):
            for row in self._format_model_item(child, indent):
                yield row
            if child.is_for_loop():
                for row in self._rows_from_simple_table(child, indent+1):
                    yield row

    def _format_name(self, item):
        return  [item.name]

    def _format_model_item(self, item, indent):
        return item.as_list()


class RowSplittingFormatter(_Formatter):

    def __init__(self, cols):
        self._cols = cols
        self._row_splitter = RowSplitter(cols)

    def format_simple_table(self, table):
        for row in self._rows_from_simple_table(table):
            yield row

    def format_indented_table(self, table):
        for row in self._rows_from_indented_table(table):
            yield row

    def _format_model_item(self, item, indent):
        return self._row_splitter.split(item.as_list(), indent)


class _Aligner(_Formatter):
    def align_rows(self, rows):
        return [self.align_row(r) for r in rows]

    def align_row(self, row):
        for index, col in enumerate(row[:-1]):
            if len(self._widths) <= index:
                continue
            row[index] = row[index].ljust(self._widths[index])
        return row


class SettingTableAligner(_Aligner):

    def __init__(self, cols, first_column_width):
        self._row_splitter = RowSplitter(cols)
        self._widths = [first_column_width]

    def format_simple_table(self, table):
        return self.align_rows(self._rows_from_simple_table(table))

    def _format_model_item(self, item, indent):
        return self._row_splitter.split(item.as_list(), indent)


class ColumnAligner(_Aligner):

    def __init__(self, max_name_length, table):
        self._max_name_length = max_name_length
        self._widths = self._count_justifications(table)

    def _count_justifications(self, table):
        result = [18] + [len(header) for header in table.header]
        for element in [list(kw) for kw in list(table)]:
            for step in element:
                for index, col in enumerate(step.as_list()):
                    index += 1
                    if len(result) <= index:
                        result.append(0)
                    result[index] = max(len(col), result[index])
        return result

    def format_indented_table(self, table):
        for item in table:
            rows = list(self._rows_from_item(item, 1))
            if len(item.name) > self._max_name_length:
                yield [item.name]
            else:
                first_row = [item.name] + rows[0][1:]
                yield self.align_row(first_row)
                rows = rows[1:]
            for r in rows:
                yield self.align_row(r)

    def _format_model_item(self, item, indent):
        return [self._escape(['']*indent + item.as_list())]

    def _escape(self, row):
        if len(row) >= 2 and row[0] == '' and row[1] == '':
            row[1] = '\\'
        return [re.sub('\s\s+(?=[^\s])', lambda match: '\\'.join(match.group(0)), item) for item in row]


class SplittingHtmlFormatter(RowSplittingFormatter):

    def format_indented_table(self, table):
        for item in table:
            rows = list(self._rows_from_item(item, 1))
            yield self._first_row(item, rows[0])
            for row in rows[1:]:
                yield row

    def _first_row(self, item, row):
        return [self._format_name(item)] + row[1:]

    def _format_name(self, item):
        from robot.parsing.model import UserKeyword
        type_ = 'keyword' if isinstance(item, UserKeyword) else 'test'
        return AnchorNameCell(item.name, type_)

    def _format_model_item(self, item, indent):
        if isinstance(item, Documentation):
            return self._format_documentation(item, indent)
        rows = self._row_splitter.split(item.as_list(), indent)
        return [self._pad([NameCell(row[0])] + [HtmlCell(c) for c in row[1:]]) for row in rows]

    def _format_documentation(self, doc, indent):
        if indent:
            start = [NameCell(), HtmlCell(doc.setting_name)]
            value = doc.as_list()[1:]
            if len(value) == 1:
                return [start + [DocumentationCell(doc.value, self._cols-1-indent)]]
            return [self._pad(start + [HtmlCell(v) for v in value])]
        return [[NameCell(doc.setting_name),
                DocumentationCell(doc.value, self._cols-1)]]

    def _format_row(self, row):
        if row and not isinstance(row[0], basestring):
            return row
        return self._pad([NameCell(row[0])] + [HtmlCell(c) for c in row[1:]])

    def _pad(self, row, colspan=False, indent=0):
        if colspan:
            return row
        return row + [HtmlCell()] * (self._cols - len(row) - indent)


class HtmlCell(object):
    _backslash_matcher = re.compile(r'(\\+)n ')

    def __init__(self, content='', attributes=None, tag='td', escape=True):
        if escape:
            content = utils.html_escape(content)
        self.content = self._replace_newlines(content)
        self.attributes = attributes or {}
        self.tag = tag

    def _replace_newlines(self, content):
        def replacer(match):
            backslash_count = len(match.group(1))
            if backslash_count % 2 == 1:
                return '%sn<br>\n' % match.group(1)
            return match.group()
        return self._backslash_matcher.sub(replacer, content)


class NameCell(HtmlCell):

    def __init__(self, name='', attributes=None):
        HtmlCell.__init__(self, name, attributes)
        self.attributes.update({'class': 'name'})


class AnchorNameCell(HtmlCell):

    def __init__(self, name, type_):
        HtmlCell.__init__(self, self._link_from_name(name, type_),
                          {'class': 'name'}, escape=False)

    def _link_from_name(self, name, type_):
        return '<a name="%s_%s">%s</a>' % (type_, utils.html_attr_escape(name),
                                           utils.html_escape(name))


class DocumentationCell(HtmlCell):

    def __init__(self, content, span):
        HtmlCell.__init__(self, content)
        self.attributes = {'class': 'colspan%d' % span, 'colspan': '%d' % span}


class HeaderCell(HtmlCell):

    def __init__(self, name, span):
        HtmlCell.__init__(self, name, {'class': 'name', 'colspan': '%d' % span},
                          tag='th')


class RowSplitter(object):
    _comment_mark = '#'
    _empty_cell_escape = '${EMPTY}'
    _line_continuation = '...'

    def __init__(self, cols=8):
        self._cols = cols

    def split(self, row, indent):
        self._in_comment = False
        return self._split_to_rows(row, indent)

    def _split_to_rows(self, data, indent=0):
        if not data:
            return [[]]
        rows = []
        while data:
            current, data = self._split(self._indent(data, indent))
            rows.append(self._escape_last_empty_cell(current))
        return rows

    def _split(self, data):
        row, rest = data[:self._cols], data[self._cols:]
        self._in_comment = any(c for c in row if
                               c.startswith(self._comment_mark))
        rest = self._add_line_continuation(rest)
        return row, rest

    def _escape_last_empty_cell(self, row):
        if not row[-1].strip():
            row[-1] = self._empty_cell_escape
        return row

    def _add_line_continuation(self, data):
        if data:
            if self._in_comment:
                data[0] = self._comment_mark + data[0]
            data = [self._line_continuation] + data
        return data

    def _indent(self, row, indent):
        return [''] * indent + row
