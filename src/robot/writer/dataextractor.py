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


class DataExtractor(object):
    """Transforms table of a parsed test data file into a list of rows."""

    def __init__(self, want_name_on_first_row=None):
        self._want_name_on_first_row = want_name_on_first_row or \
                                       (lambda t,n: False)

    def rows_from_table(self, table):
        if table.type in ['setting', 'variable']:
            return self._rows_from_item(table)
        return self._rows_from_indented_table(table)

    def _rows_from_indented_table(self, table):
        items = list(table)
        for index, item in enumerate(items):
            for row in self._rows_from_test_or_keyword(item, table):
                yield row
            if not self._last(items, index):
                yield []

    def _rows_from_test_or_keyword(self, test_or_keyword, table):
        rows = list(self._rows_from_item(test_or_keyword, 1))
        for r in self._add_name(test_or_keyword.name, rows, table):
            yield r

    def _add_name(self, name, rows, table):
        if rows and self._want_name_on_first_row(table, name):
            rows[0][0] = name
            return rows
        return [[name]] + rows

    def _rows_from_item(self, item, indent=0):
        for child in item:
            if child.is_set():
                yield [''] * indent + child.as_list()
            if child.is_for_loop():
                for row in self._rows_from_item(child, indent+1):
                    yield row
                yield ['', 'END']

    def _last(self, items, index):
        return index >= len(items) -1
