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


class TsvFormatter(object):
    _padding = ''

    def __init__(self, cols=8):
        self._cols = cols
        self._formatter = RowSplitter(self._padding, self._cols)

    def setting_rows(self, settings):
        return self._rows_from_table(settings)

    def variable_rows(self, variables):
        return self._rows_from_table(variables)

    def test_rows(self, tests):
        return self._rows_from_steps(tests)

    def keyword_rows(self, keywords):
        return self._rows_from_steps(keywords)

    def empty_row(self):
        return self._pad([])

    def _rows_from_table(self, table):
        yield self._header_row(table)
        for row in self._rows_from_items(table):
            yield row
        yield self.empty_row()

    def _rows_from_steps(self, table):
        yield self._header_row(table)
        for item in table:
            yield self._pad([item.name])
            for row in self._rows_from_items(item, 1):
                yield row
        yield self.empty_row()

    def _header_row(self, table):
        return self._pad(['*%s*' % cell for cell in table.header])

    def _name_row(self, name):
        return self.format([name])

    def _rows_from_items(self, item, indent=0):
        for ch in (c for c in item if c.is_set()):
            for row in self.format(ch.as_list(), indent):
                yield row
            if ch.is_for_loop():
                for row in self._rows_from_items(ch, indent+1):
                    yield row

    def format(self, row, indent=0):
        return [self._pad(row) for row in self._formatter.format(row, indent)]

    def _pad(self, row):
        return row + [self._padding] * (self._cols - len(row))


class TxtFormatter(object):
    _padding = ''
    _FIRST_ROW_LENGTH = 18

    def __init__(self, cols=8):
        self._cols = cols
        self._formatter = RowSplitter(self._padding, self._cols)
        self._justifications = []

    def setting_rows(self, settings):
        yield self._header_row(settings)
        self._justifications = [14]
        for row in  self._rows_from_items(settings):
            yield row
        self._justifications = []
        yield self.empty_row()

    def variable_rows(self, variables):
        yield self._header_row(variables)
        for row in self._rows_from_items(variables):
            yield row
        yield self.empty_row()

    def test_rows(self, tests):
        return self._rows_from_steps(tests)

    def keyword_rows(self, keywords):
        return self._rows_from_steps(keywords)

    def _header_row(self, table):
        header = ['*** %s ***' % table.header[0]] + table.header[1:]
        self._justify_row(header)
        return header

    def empty_row(self):
        return []

    def _rows_from_steps(self, table):
        if table.header[1:]:
            self._justifications = self._count_justifications(table)
        yield self._header_row(table)
        if not table.header[1:]:
            for item in table:
                yield [item.name]
                for row in self._rows_from_items(item, 1):
                    yield row
        else:
            for item in table:
                rows = list(self._rows_from_items(item, 1))
                if len(item.name) > self._FIRST_ROW_LENGTH:
                    yield [item.name]
                else:
                    yield [item.name.ljust(self._justifications[0])] + rows[0][1:]
                    rows = rows[1:]
                for r in rows:
                    yield r
        self._justifications = []
        yield self.empty_row()

    def _rows_from_items(self, item, indent=0):
        for ch in (c for c in item if c.is_set()):
            for row in self.format(ch.as_list(), indent):
                yield row
            if ch.is_for_loop():
                for row in self._rows_from_items(ch, indent+1):
                    yield row

    def _count_justifications(self, table):
        result = [self._FIRST_ROW_LENGTH]+[len(header) for header in table.header[1:]]
        for element in [list(kw) for kw in list(table)]:
            for step in element:
                for index, col in enumerate(step.as_list()):
                    index += 1
                    if len(result) <= index:
                        result.append(0)
                    result[index] = max(len(col), result[index])
        return result

    def format(self, row, indent=0):
        rows = self._formatter.format(row, indent)
        return self._justify(self._escape(rows))

    def _escape(self, rows):
        for index, row in enumerate(rows):
            if len(row) >= 2 and row[0] == '' and row[1] == '':
                row[1] = '\\'
            rows[index] = [re.sub('\s\s+(?=[^\s])', lambda match: '\\'.join(match.group(0)), item) for item in row]
        return rows

    def _justify(self, rows):
        return [self._justify_row(r) for r in rows]

    def _justify_row(self, row):
        for index, col in enumerate(row[:-1]):
            if len(self._justifications) <= index:
                continue
            row[index] = row[index].ljust(self._justifications[index])
        return row


class PipeFormatter(TxtFormatter):
    _padding = '  '


class HtmlFormatter(object):

    def __init__(self):
        self._formatter = RowSplitter(cols=5)
        self._padding = ''
        self._cols = 5

    def format(self, row, indent, colspan):
        return [self._pad(row, colspan) for row in self._formatter.format(row, indent)]

    def _pad(self, row, colspan, indent=0):
        if colspan:
            return row
        return row + [self._padding] * (self._cols - len(row) - indent)

    def empty_row(self):
        return [NameCell('')] + [Cell('') for _ in range(self._cols-1)]

    def setting_rows(self, settings):
        return self._rows_from_table(settings)

    def variable_rows(self, variables):
        return self._rows_from_table(variables)

    def test_rows(self, tests):
        return self._rows_from_steps(tests, 'test')

    def keyword_rows(self, keywords):
        return self._rows_from_steps(keywords, 'keyword')

    def _rows_from_steps(self, table, type_):
        result = [[HeaderCell(table.header[0], self._cols)]]
        for item in table:
            children = [e for e in list(item) if e.is_set()]
            result.extend(self._first_row(item, type_, children[0]))
            for subitem in children[1:]:
                result.extend(self._rows_from_item(subitem, indent=1))
                if subitem.is_for_loop():
                    for sub in subitem:
                        result.extend(self._rows_from_item(sub, indent=2))
        result.append(self.empty_row())
        return result

    def _first_row(self, item, type_, elem):
        name = AnchorNameCell(item.name, type_)
        if isinstance(elem, Documentation):
            doc = elem.as_list()
            if len(doc) == 2:
                return [[name] + [Cell(elem.setting_name),
                                  DocumentationCell(elem.value, self._cols-2)]]
        rows = self.format(elem.as_list(), indent=1, colspan=False)
        rows = [[Cell(e) for e in row] for row in rows]
        rows[0][0] = name
        return rows

    def _rows_from_table(self, table):
        result = [[HeaderCell(table.header[0], self._cols)]]
        for item in table:
            if item.is_set():
                result.extend(self._rows_from_item(item))
        result.append(self.empty_row())
        return result

    def _rows_from_item(self, item, indent=0):
        if isinstance(item, Documentation):
            return [[NameCell(item.setting_name),
                    DocumentationCell(item.value, self._cols-1)]]
        rows = self.format(item.as_list(), indent, colspan=False)
        return [[NameCell(row[0])] + [Cell(c) for c in row[1:]] for row in rows]


class HtmlCell(object):
    _backslash_matcher = re.compile(r'(\\+)n ')

    def __init__(self, content='', attributes=None, tag='td'):
        self.content = content
        self.attributes = attributes or {}
        self.tag = tag

    def _replace_newlines(self, content):
        def replacer(match):
            backslash_count = len(match.group(1))
            if backslash_count % 2 == 1:
                return '%sn<br>\n' % match.group(1)
            return match.group()
        return self._backslash_matcher.sub(replacer, content)


class Cell(HtmlCell):

    def __init__(self, content, attributes=None):
        HtmlCell.__init__(self,
                          self._replace_newlines(utils.html_escape(content)),
                          attributes)


class NameCell(HtmlCell):

    def __init__(self, name, attributes=None):
        HtmlCell.__init__(self, self._replace_newlines(name), attributes)
        self.attributes.update({'class': 'name'})


class AnchorNameCell(HtmlCell):

    def __init__(self, name, type_):
        HtmlCell.__init__(self, self._link_from_name(name, type_),
                          {'class': 'name'})


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

    def __init__(self, padding='', cols=8):
        self._cols = cols
        self._padding = padding

    def format(self, row, indent):
        # TODO: encoding does not belong here
        return [self._encode(r) for r in self._split_to_rows(row, indent)]

    def _encode(self, row):
        return [cell.encode('UTF-8').replace('\n', ' ') for cell in row]

    def _split_to_rows(self, data, indent=0):
        if not data:
            return [[]]
        rows = []
        while data:
            current, data = self._split(data, indent)
            rows.append(self._escape_last_empty_cell(current))
            data = self._add_line_continuation(data)
        return rows

    def _split(self, data, indent):
        data = self._indent(data, indent)
        return data[:self._cols], data[self._cols:]

    def _escape_last_empty_cell(self, row):
        if not row[-1].strip():
            row[-1] = '${EMPTY}'
        return row

    def _add_line_continuation(self, data):
        if data:
            data = ['...'] + data
        return data

    def _indent(self, row, indent):
        return [self._padding]*indent + row
