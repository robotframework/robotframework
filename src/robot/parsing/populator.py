#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

from robot import utils


class _TablePopulator(object):

    def __init__(self, datafile):
        self._table = self._get_table(datafile)
        self._populator = None

    def add(self, row):
        if self._is_continuing(row):
            self._populator.add(self._values_from(row))
        else:
            self.populate()
            self._populator = self._get_populator(row)

    def _values_from(self, row):
        return row

    def _is_continuing(self, row):
        return row[0].strip() == self.row_continuation_marker

    def populate(self):
        if self._populator:
            self._populator.populate()


class SettingTablePopulator(_TablePopulator):
    row_continuation_marker = '...'
    attrs_by_name = utils.NormalizedDict({'Documentation': 'doc',
                                          'Document': 'doc',
                                          'Suite Setup': 'suite_setup',
                                          'Suite Precondition': 'suite_setup',
                                          'Suite Teardown': 'suite_teardown',
                                          'Suite Postcondition': 'suite_teardown',
                                          'Test Setup': 'test_setup',
                                          'Test Precondition': 'test_setup',
                                          'Test Teardown': 'test_teardown',
                                          'Test Postcondition': 'test_teardown',
                                          'Force Tags': 'force_tags',
                                          'Default Tags': 'default_tags',
                                          'Test Timeout': 'test_timeout'})

    import_setters_by_name = utils.NormalizedDict({'Library': 'add_library',
                                                   'Resource': 'add_resource',
                                                   'Variables': 'add_variables'})

    def _get_table(self, datafile):
        return datafile.setting_table

    def _values_from(self, row):
        return row[1:]

    def _get_populator(self, row):
        return PropertyPopulator(self._get_setter(row[0]), row[1:])

    def _get_setter(self, setting_name):
        if setting_name in self.import_setters_by_name:
            attr_name = self.import_setters_by_name[setting_name]
            return getattr(self._table, attr_name)
        attr_name = self.attrs_by_name[setting_name]
        return getattr(self._table, attr_name).set


class VariableTablePopulator(_TablePopulator):
    row_continuation_marker = '...'

    def _get_table(self, datafile):
        return datafile.variable_table

    def _get_populator(self, row):
        return VariablePopulator(self._table.add, row)


class TestTablePopulator(_TablePopulator):
    row_continuation_marker = ''

    def _get_table(self, datafile):
        return datafile.testcase_table

    def _get_populator(self, row):
        return TestCasePopulator(self._table.add, row)


class KeywordTablePopulator(_TablePopulator):
    row_continuation_marker = ''

    def _get_table(self, datafile):
        return datafile.keyword_table

    def _get_populator(self, row):
        return UserKeywordPopulator(self._table.add, row)


class _TestCaseUserKeywordPopulator(object):
    row_continuation_marker = ('', '...')

    def __init__(self, setter, row):
        self._test_or_uk = setter(row[0])
        self._populator = self._get_populator(row)

    def add(self, row):
        if self._is_continuing_step(row):
            self._populator.add(row[2:])
        else:
            self._populator.populate()
            self._populator = self._get_populator(row)

    def _get_populator(self, row):
        first_cell = self._first_cell_value(row)
        if self._is_setting(first_cell):
            return PropertyPopulator(self._setting_setter(first_cell), row[2:])
        return StepPopulator(self._test_or_uk.add_step, row[1:])

    def _first_cell_value(self, row):
        return row[1].strip() if len(row) > 1 else ''

    def _is_setting(self, cell):
        return cell and cell[0] == '[' and cell[-1] == ']'

    def _setting_setter(self, cell):
        attr_name = self.attrs_by_name[self._setting_name(cell)]
        return getattr(self._test_or_uk, attr_name).set

    def _setting_name(self, cell):
        return cell[1:-1].strip()

    def _is_continuing_step(self, row):
        return (row[0].strip(), row[1].strip()) == self.row_continuation_marker

    def populate(self):
        if self._populator:
            self._populator.populate()


class TestCasePopulator(_TestCaseUserKeywordPopulator):
    attrs_by_name = utils.NormalizedDict({'Documentation': 'doc',
                                          'Document': 'doc',
                                          'Setup': 'setup',
                                          'Precondition': 'setup',
                                          'Teardown': 'teardown',
                                          'Postcondition': 'teardown',
                                          'Tags': 'tags',
                                          'Timeout': 'timeout'})



class UserKeywordPopulator(_TestCaseUserKeywordPopulator):
    attrs_by_name = utils.NormalizedDict({'Documentation': 'doc',
                                          'Document': 'doc',
                                          'Arguments': 'args',
                                          'Return': 'return_',
                                          'Timeout': 'timeout'})


class PropertyPopulator(object):

    def __init__(self, setter, initial_value):
        self._setter = setter
        self._value = initial_value

    def add(self, row):
        self._value.extend(row)

    def populate(self):
        self._setter(self._value)


class VariablePopulator(PropertyPopulator):
    def populate(self):
        self._setter(self._value[0], self._value[1:])


class StepPopulator(object):

    def __init__(self, setter, row):
        self._setter = setter
        self._current_row = row

    def add(self, row):
        self._current_row.extend(row)

    def populate(self):
        if self._current_row:
            self._setter(self._current_row)


class Populator(object):
    _whitespace_regexp = re.compile('\s+')
    _null_populator = type('NullTablePopulator', (), 
                           {'add': lambda self, row: None,
                            'eof': lambda self: None})()
    populators = utils.NormalizedDict({'Setting':       SettingTablePopulator,
                                       'Settings':      SettingTablePopulator,
                                       'Metadata':      SettingTablePopulator,
                                       'Variable':      VariableTablePopulator,
                                       'Variables':     VariableTablePopulator,
                                       'Test Case':     TestTablePopulator,
                                       'Test Cases':    TestTablePopulator,
                                       'Keyword':       KeywordTablePopulator,
                                       'Keywords':      KeywordTablePopulator,
                                       'User Keyword':  KeywordTablePopulator,
                                       'User Keywords': KeywordTablePopulator})

    def __init__(self, datafile, path):
        self._datafile = datafile
        self._datafile.source = path
        self._current_populator = self._null_populator

    def start_table(self, name):
        try:
            self._current_populator = self.populators[name](self._datafile)
        except KeyError:
            self._current_populator = self._null_populator
        return self._current_populator is not self._null_populator

    def add(self, row):
        cells = self._data_cells(row)
        if cells:
            self._current_populator.add(cells)

    def _data_cells(self, row):
        cells = [ c.strip() for c in row ]
        while cells and not cells[-1]:
            cells.pop()
        return cells

    def eof(self):
        self._current_populator.populate()

    def _collapse_whitespace(self, value):
        return self._whitespace_regexp.sub(' ', value).strip()
