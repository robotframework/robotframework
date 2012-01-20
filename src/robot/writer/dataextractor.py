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


class DataExtractor(object):
    """The DataExtractor object. Transforms table of a parsed Robot Framework
    test data file into list of rows."""

    def __init__(self, want_name_on_first_content_row=False):
        self._want_names_on_first_content_row = want_name_on_first_content_row

    def rows_from_table(self, table):
        if table.type in ['setting', 'variable']:
            return self.rows_from_simple_table(table)
        return self.rows_from_indented_table(table)

    def rows_from_simple_table(self, table):
        """Return list of rows from a setting or variable table"""
        return self._rows_from_item(table)

    def rows_from_indented_table(self, table):
        """Return list of rows from a test case or user keyword table"""
        items = list(table)
        for index, item in enumerate(items):
            for row in self._rows_from_test_or_keyword(item):
                yield row
            if not self._last(items, index):
                yield []

    def _rows_from_test_or_keyword(self, test_or_keyword):
        rows = list(self._rows_from_item(test_or_keyword, 1)) or ['']
        first_row, rest = self._first_row(test_or_keyword.name, rows)
        yield first_row
        for r in rest:
            yield r

    def _first_row(self, name, rows):
        if self._want_names_on_first_content_row:
            return [name] + rows[0][1:], rows[1:]
        return [name], rows

    def _rows_from_item(self, item, indent=0):
        for child in (c for c in item if c.is_set()):
            yield [''] * indent + child.as_list()
            if child.is_for_loop():
                for row in self._rows_from_item(child, indent+1):
                    yield row

    def _last(self, items, index):
        return index >= len(items) -1
