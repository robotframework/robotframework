#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from robot.utils import attribute_escape, html_escape

from .formatters import _DataFileFormatter


class HtmlFormatter(_DataFileFormatter):
    _split_multiline_doc = False

    def _format_row(self, row, table=None):
        row = self._pad(self._escape_consecutive_whitespace(row), table)
        if self._is_documentation_row(row):
            return self._create_documentation_row(row)
        first_cell = self._create_first_cell(row[0], table)
        if self._is_indented_documentation_row(row[1:], table):
            return self._create_indented_documentation_row(first_cell, row[1:])
        return [first_cell] + [HtmlCell(c) for c in row[1:]]

    def _is_documentation_row(self, row):
        return row[0] == 'Documentation'

    def _create_documentation_row(self, row):
        return [NameCell(row[0]), DocumentationCell(row[1], span=self._column_count-1)]

    def _is_indented_documentation_row(self, cells, table):
        return self._is_indented_table(table) and cells and \
                    cells[0] == '[Documentation]'

    def _create_indented_documentation_row(self, first_cell, cells):
        start = [first_cell, HtmlCell(cells[0])]
        if any(c.startswith('#') for c in cells):
            return start + [HtmlCell(c) for c in cells[1:]]
        return start + [DocumentationCell(cells[1], self._column_count-2)]

    def _create_first_cell(self, cell, table):
        if self._is_indented_table(table) and cell:
            return AnchorNameCell(cell, 'keyword' if table.type == 'keyword'
                                                  else 'test')
        return NameCell(cell)

    def format_header(self, table):
        if not self._should_align_columns(table) or len(table.header) == 1:
            return [HeaderCell(table.header[0], self._column_count)]
        headers = self._pad_header(table)
        return [HeaderCell(hdr) for hdr in headers]

    def _pad_header(self, table):
        header = table.header
        return header + [''] * (self._get_column_count(table) - len(header))

    def _pad(self, row, table):
        return row + [''] * (self._get_column_count(table) - len(row))

    def _get_column_count(self, table):
        if table is None or len(table.header) == 1 \
                or not self._is_indented_table(table):
            return self._column_count
        return max(self._max_column_count(table), len(table.header))

    def _max_column_count(self, table):
        count = 0
        for item in table:
            for child in item:
                count = max(count, len(child.as_list()) + 1)
        return count


class HtmlCell(object):
    _backslash_matcher = re.compile(r'(\\+)n ?')

    def __init__(self, content='', attributes=None, tag='td', escape=True):
        if escape:
            content = html_escape(content)
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
        HtmlCell.__init__(self, name, {'class': 'name'})


class AnchorNameCell(HtmlCell):

    def __init__(self, name, type_):
        HtmlCell.__init__(self, self._link_from_name(name, type_),
                          {'class': 'name'}, escape=False)

    def _link_from_name(self, name, type_):
        return '<a name="%s_%s">%s</a>' % (type_, attribute_escape(name),
                                           html_escape(name))


class DocumentationCell(HtmlCell):

    def __init__(self, content, span):
        HtmlCell.__init__(self, content, {'class': 'colspan%d' % span,
                                          'colspan': '%d' % span})


class HeaderCell(HtmlCell):

    def __init__(self, name, span=1):
        HtmlCell.__init__(self, name, {'class': 'name', 'colspan': '%d' % span},
                          tag='th')
