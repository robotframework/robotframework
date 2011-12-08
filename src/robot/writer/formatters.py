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

    def format(self, row, indent):
        return [self._pad(row) for row in self._formatter.format(row, indent)]

    def _pad(self, row):
        return row + [self._padding] * (self._cols - len(row))


class TxtFormatter(object):
    _padding = ''

    def __init__(self, cols=8):
        self._cols = cols
        self._formatter = RowSplitter(self._padding, self._cols)

    def format(self, row, indent=0, justifications=[]):
        rows = self._formatter.format(row, indent)
        return self._justify(self._escape(rows), justifications)

    def _escape(self, rows):
        for index, row in enumerate(rows):
            if len(row) >= 2 and row[0] == '' and row[1] == '':
                row[1] = '\\'
            rows[index] = [re.sub('\s\s+(?=[^\s])', lambda match: '\\'.join(match.group(0)), item) for item in row]
        return rows

    def _justify(self, rows, justifications):
        for row in rows:
            for index, col in enumerate(row[:-1]):
                if len(justifications) <= index:
                    continue
                row[index] = row[index].ljust(justifications[index])
        return rows


class PipeFormatter(TxtFormatter):
    _padding = '  '


class HtmlFormatter(object):

    def __init__(self):
        self._formatter = RowSplitter(cols=5)
        self._padding = ''
        self._cols = 5

    def format(self, row, indent, colspan):
        return [self._pad(row, colspan) for row in self._formatter.format(row, indent)]

    def _pad(self, row, colspan):
        if colspan:
            return row
        return row + [self._padding] * (self._cols - len(row))

    def header_row(self, header):
        return [NameCell(header, {'colspan': '%d' % self._cols})]

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
        # TODO: Cleanup
        result = []
        for item in table:
            elems = [e for e in list(item) if e.is_set()]
            result.append(self._firstrow(item, type_, elems[0]))
            for subitem in elems[1:]:
                if subitem.is_set():
                    result.extend(self._create_cell(subitem, indent=1))
                if subitem.is_for_loop():
                    for sub in subitem:
                        result.extend(self._create_cell(sub, indent=2))
        return result

    def _firstrow(self, item, type_, elem):
        # FIXME: first row is not wrapped properly.
        result = [AnchorNameCell(item.name, type_)]
        if isinstance(elem, Documentation):
            # TODO: remove this ugly hack for doc comments
            if elem.comment:
                return result + [Cell(elem.setting_name), Cell(elem.value),
                          Cell(elem.comment.as_list()[0], {'class': 'colspan2', 'colspan': '%d' % (self._cols - 3)})]
            return result + [Cell(elem.setting_name),
                             Cell(elem.value, {'class': 'colspan3',
                                               'colspan': '%d' % (self._cols-2)})]
        return result + [Cell(e) for e in elem.as_list()]

    def _rows_from_table(self, table):
        result = []
        for item in table:
            if item.is_set():
                result.extend(self._create_cell(item))
        return result

    def _create_cell(self, item, indent=0):
        if isinstance(item, Documentation):
            return [NameCell(item.setting_name, ),
                    Cell(item.value, {'colspan': '%d' % (self._cols-1)})]
        rows = self.format(item.as_list(), indent, colspan=False)
        return [[NameCell(row[0])] + [Cell(c) for c in row[1:]] for row in rows]


class HtmlCell(object):
    _backslash_matcher = re.compile(r'(\\+)n ')

    def _replace_newlines(self, content):
        def replacer(match):
            backslash_count = len(match.group(1))
            if backslash_count % 2 == 1:
                return '%sn<br>\n' % match.group(1)
            return match.group()
        return self._backslash_matcher.sub(replacer, content)


class Cell(HtmlCell):

    def __init__(self, content, attributes=None):
        self.content = self._replace_newlines(utils.html_escape(content))
        self.attributes = attributes or {}


class NameCell(HtmlCell):

    def __init__(self, name, attributes=None):
        self.content = self._replace_newlines(name)
        self.attributes = {'class': 'name'}
        if attributes:
            self.attributes.update(attributes)


class AnchorNameCell(object):

    def __init__(self, name, type_):
        self.content = self._link_from_name(name, type_)
        self.attributes = {'class': 'name'}

    def _link_from_name(self, name, type_):
        return '<a name="%s_%s">%s</a>' % (type_, utils.html_attr_escape(name),
                                           utils.html_escape(name))


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
