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


class Populator(object):
    """Explicit interface for all populators."""
    def add(self, row): raise NotImplementedError()
    def populate(self): raise NotImplementedError()


class _TablePopulator(Populator):

    def __init__(self, datafile):
        self._table = self._get_table(datafile)
        self._populator = None

    def add(self, row):
        if not self._is_continuing(row):
            self.populate()
            self._populator = self._get_populator(row)
        self._populator.add(row)

    def _is_continuing(self, row):
        return row[0].strip() == self.row_continuation_marker

    def populate(self):
        if self._populator:
            self._populator.populate()


class SettingTablePopulator(_TablePopulator):
    row_continuation_marker = '...'
    olde_metadata_prefix = 'meta:'
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
    name_value_setters = utils.NormalizedDict({'Library': 'add_library',
                                               'Resource': 'add_resource',
                                               'Variables': 'add_variables',
                                               'Metadata': 'add_metadata'})

    def _get_table(self, datafile):
        return datafile.setting_table

    def _get_populator(self, row):
        first_cell = row[0]
        if self._is_metadata_with_olde_prefix(first_cell):
            return OldStyleMetadataPopulator(self._table.add_metadata)
        if self._is_import_or_metadata(first_cell):
            return SettingTableNameValuePopulator(self._table_attr_setter(first_cell))
        return SettingPopulator(self._setting_setter(first_cell))

    def _is_metadata_with_olde_prefix(self, setting_name):
        return setting_name.lower().startswith(self.olde_metadata_prefix)

    def _is_import_or_metadata(self, setting_name):
        return setting_name in self.name_value_setters

    def _table_attr_setter(self, first_cell):
        attr_name = self.name_value_setters[first_cell]
        return getattr(self._table, attr_name)

    def _setting_setter(self, first_cell):
        attr_name = self.attrs_by_name[first_cell]
        return getattr(self._table, attr_name).set


class VariableTablePopulator(_TablePopulator):
    row_continuation_marker = '...'

    def _get_table(self, datafile):
        return datafile.variable_table

    def _get_populator(self, row):
        return NameAndValuePropertyPopulator(self._table.add)


class TestTablePopulator(_TablePopulator):
    row_continuation_marker = ''

    def _get_table(self, datafile):
        return datafile.testcase_table

    def _get_populator(self, row):
        return TestCasePopulator(self._table.add)


class KeywordTablePopulator(_TablePopulator):
    row_continuation_marker = ''

    def _get_table(self, datafile):
        return datafile.keyword_table

    def _get_populator(self, row):
        return UserKeywordPopulator(self._table.add)


class _TestCaseUserKeywordPopulator(Populator):
    row_continuation_marker = ('', '...')

    def __init__(self, test_or_uk_creator):
        self._test_or_uk_creator = test_or_uk_creator
        self._test_or_uk = None

    def add(self, row):
        if not self._test_or_uk:
            self._test_or_uk = self._test_or_uk_creator(row[0])
            self._populator = self._get_populator(row)
        elif not self._is_continuing_step(row):
            self._populator.populate()
            self._populator = self._get_populator(row)
        self._populator.add(row[1:])

    def populate(self):
        if self._populator:
            self._populator.populate()

    def _is_continuing_step(self, row):
        return (row[0].strip(), row[1].strip()) == self.row_continuation_marker

    def _get_populator(self, row):
        first_cell = self._first_cell_value(row)
        if self._is_setting(first_cell):
            return SettingPopulator(self._setting_setter(first_cell))
        return StepPopulator(self._test_or_uk.add_step)

    def _first_cell_value(self, row):
        return row[1].strip() if len(row) > 1 else ''

    def _is_setting(self, cell):
        return cell and cell[0] == '[' and cell[-1] == ']'

    def _setting_setter(self, cell):
        attr_name = self.attrs_by_name[self._setting_name(cell)]
        return getattr(self._test_or_uk, attr_name).set

    def _setting_name(self, cell):
        return cell[1:-1].strip()


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


class _PropertyPopulator(Populator):

    def __init__(self, setter):
        self._setter = setter
        self._value = []


class NameAndValuePropertyPopulator(_PropertyPopulator):

    def add(self, row):
        self._value.extend(row)

    def populate(self):
        name, value = self._value[0], self._value[1:]
        self._setter(name, value)


class SettingPopulator(_PropertyPopulator):

    def add(self, row):
        self._value.extend(row[1:])

    def populate(self):
        self._setter(self._value)


class SettingTableNameValuePopulator(NameAndValuePropertyPopulator):

    def add(self, row):
        self._value.extend(row[1:])


class OldStyleMetadataPopulator(NameAndValuePropertyPopulator):
    olde_metadata_prefix = 'meta:'

    def add(self, row):
        if self._is_metadata_with_olde_prefix(row[0]):
            values = self._extract_name_from_olde_style_meta_cell(row[0]) + row[1:]
        else:
            values = row[1:]
        self._value.extend(values)

    def _extract_name_from_olde_style_meta_cell(self, first_cell):
        return [first_cell.split(':', 1)[1].strip()]

    def _is_metadata_with_olde_prefix(self, first_cell):
        return first_cell.lower().startswith(self.olde_metadata_prefix)


class StepPopulator(_PropertyPopulator):

    def add(self, row):
        self._value.extend(row)

    def populate(self):
        if self._value:
            self._setter(self._value)


class TestCaseFilePopulator(Populator):
    _whitespace_regexp = re.compile('\s+')
    _null_populator = type('NullTablePopulator', (Populator, ),
                           {'add': lambda self, row: None,
                            'populate': lambda self: None})()
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

    def populate(self):
        self._current_populator.populate()

    def add(self, row):
        cells = self._data_cells(row)
        if cells:
            self._current_populator.add(cells)

    def _data_cells(self, row):
        cells = [ self._collapse_whitespace(cell)
                  for cell in self._cells_without_comments(row) ]
        while cells and not cells[-1]:
            cells.pop()
        return cells

    def _collapse_whitespace(self, value):
        return self._whitespace_regexp.sub(' ', value).strip()

    def _cells_without_comments(self, row):
        filtered = []
        for c in row:
            if c.startswith('#'):
                return filtered
            filtered.append(c)
        return filtered
