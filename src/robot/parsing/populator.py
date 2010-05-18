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
import os

from robot import utils
from robot.output import LOGGER

# Hook for external tools for altering ${CURDIR} processing
PROCESS_CURDIR = True


def report_invalid_setting(msg):
    LOGGER.error("Invalid setting %s." % msg)


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

    def populate(self):
        if self._populator:
            self._populator.populate()

    def _is_continuing(self, row):
        return row.is_continuing()


class SettingTablePopulator(_TablePopulator):
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
        first_cell = row.head()
        if self._is_metadata_with_olde_prefix(first_cell):
            return OldStyleMetadataPopulator(self._table.add_metadata)
        if self._is_import_or_metadata(first_cell):
            return SettingTableNameValuePopulator(self._table_attr_setter(first_cell))
        if self._is_setting(first_cell):
            return SettingPopulator(self._setting_setter(first_cell))
        report_invalid_setting("'%s' in setting table" % (first_cell))
        return NullPopulator()

    def _is_metadata_with_olde_prefix(self, value):
        return value.lower().startswith(self.olde_metadata_prefix)

    def _is_import_or_metadata(self, value):
        return value in self.name_value_setters

    def _is_setting(self, value):
        return value in self.attrs_by_name

    def _table_attr_setter(self, first_cell):
        attr_name = self.name_value_setters[first_cell]
        return getattr(self._table, attr_name)

    def _setting_setter(self, first_cell):
        attr_name = self.attrs_by_name[first_cell]
        return getattr(self._table, attr_name).set


class VariableTablePopulator(_TablePopulator):

    def _get_table(self, datafile):
        return datafile.variable_table

    def _get_populator(self, row):
        return NameAndValuePropertyPopulator(self._table.add)


class TestTablePopulator(_TablePopulator):

    def _get_table(self, datafile):
        return datafile.testcase_table

    def _get_populator(self, row):
        return TestCasePopulator(self._table.add)

    def _is_continuing(self, row):
        return row.is_indented()

class KeywordTablePopulator(_TablePopulator):

    def _get_table(self, datafile):
        return datafile.keyword_table

    def _get_populator(self, row):
        return UserKeywordPopulator(self._table.add)

    def _is_continuing(self, row):
        return row.is_indented()


class ForLoopPopulator(Populator):

    def __init__(self, for_loop_creator):
        self._for_loop_creator = for_loop_creator
        self._loop = None
        self._populator = NullPopulator()
        self._declaration = []

    def add(self, row):
        dedented_row = row.dedent()
        if not self._loop:
            declaration_ready = self._populate_declaration(row)
            if not declaration_ready:
                return
            self._loop = self._for_loop_creator(self._declaration)
        if not (row.is_continuing() or dedented_row.is_continuing()):
            self._populator.populate()
            self._populator = StepPopulator(self._loop.add_step)
        self._populator.add(dedented_row)

    def _populate_declaration(self, row):
        if row.starts_for_loop() or row.is_continuing():
            self._declaration.extend(row.tail())
            return False
        return True

    def populate(self):
        self._populator.populate()


class _TestCaseUserKeywordPopulator(Populator):

    def __init__(self, test_or_uk_creator):
        self._test_or_uk_creator = test_or_uk_creator
        self._test_or_uk = None
        self._populator = NullPopulator()

    def add(self, row):
        if not self._test_or_uk:
            self._test_or_uk = self._test_or_uk_creator(row.head())
        dedented_row = row.dedent()
        if dedented_row:
            if not self._continues(dedented_row):
                self._populator.populate()
                self._populator = self._get_populator(dedented_row)
            self._populator.add(dedented_row)

    def populate(self):
        self._populator.populate()

    def _get_populator(self, row):
        if row.starts_test_or_user_keyword_setting():
            setter = self._setting_setter(row.head())
            return SettingPopulator(setter) if setter else NullPopulator()
        if row.starts_for_loop():
            return ForLoopPopulator(self._test_or_uk.add_for_loop)
        return StepPopulator(self._test_or_uk.add_step)

    def _continues(self, row):
        return row.is_continuing() or \
            (isinstance(self._populator, ForLoopPopulator) and row.is_indented())

    def _setting_setter(self, cell):
        if self._setting_name(cell) in self.attrs_by_name:
            attr_name = self.attrs_by_name[self._setting_name(cell)]
            return getattr(self._test_or_uk, attr_name).set
        self._log_invalid_setting(cell)
        return None

    def _setting_name(self, cell):
        return cell[1:-1].strip()

    def _log_invalid_setting(self, value):
        report_invalid_setting("'%s' in %s '%s'" % (value, self._item_type,
                                                    self._test_or_uk.name))


class TestCasePopulator(_TestCaseUserKeywordPopulator):
    _item_type = 'test case'
    attrs_by_name = utils.NormalizedDict({'Documentation': 'doc',
                                          'Document': 'doc',
                                          'Setup': 'setup',
                                          'Precondition': 'setup',
                                          'Teardown': 'teardown',
                                          'Postcondition': 'teardown',
                                          'Tags': 'tags',
                                          'Timeout': 'timeout'})


class UserKeywordPopulator(_TestCaseUserKeywordPopulator):
    _item_type = 'keyword'
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
        self._value.extend(row.all())

    def populate(self):
        name, value = self._value[0], self._value[1:]
        self._setter(name, value)


class SettingPopulator(_PropertyPopulator):

    def add(self, row):
        self._value.extend(row.tail())

    def populate(self):
        self._setter(self._value)


class SettingTableNameValuePopulator(NameAndValuePropertyPopulator):

    def add(self, row):
        self._value.extend(row.tail())


class OldStyleMetadataPopulator(NameAndValuePropertyPopulator):
    olde_metadata_prefix = 'meta:'

    def add(self, row):
        if self._is_metadata_with_olde_prefix(row.head()):
            values = self._extract_name_from_olde_style_meta_cell(row.head()) + row.tail()
        else:
            values = row.tail()
        self._value.extend(values)

    def _extract_name_from_olde_style_meta_cell(self, first_cell):
        return [first_cell.split(':', 1)[1].strip()]

    def _is_metadata_with_olde_prefix(self, first_cell):
        return first_cell.lower().startswith(self.olde_metadata_prefix)


class StepPopulator(_PropertyPopulator):

    def add(self, row):
        self._value.extend(row.all())

    def populate(self):
        if self._value:
            self._setter(self._value)


class NullPopulator(Populator):
    def add(self, row): pass
    def populate(self): pass


class TestDataPopulator(Populator):
    _null_populator = NullPopulator()
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

    def __init__(self, datafile):
        self._datafile = datafile
        self._current_populator = self._null_populator
        self._curdir = self._determine_curdir(datafile)

    def _determine_curdir(self, datafile):
        if datafile.source:
            return os.path.dirname(datafile.source)
        return None

    def start_table(self, name):
        self._current_populator.populate()
        try:
            self._current_populator = self.populators[name](self._datafile)
        except KeyError:
            self._current_populator = self._null_populator
        return self._current_populator is not self._null_populator

    def eof(self):
        self._current_populator.populate()

    def add(self, row):
        if PROCESS_CURDIR:
            row = self._replace_curdirs_in(row)
        data = DataRow(row)
        if data:
            self._current_populator.add(data)

    def _replace_curdirs_in(self, row):
        return [cell.replace('${CURDIR}', self._curdir) for cell in row]


class DataRow(object):
    _row_continuation_marker = '...'
    _whitespace_regexp = re.compile('\s+')

    def __init__(self, cells):
        self.cells = self._data_cells(cells)

    def head(self):
        return self.cells[0]

    def tail(self):
        return self.cells[1:]

    def all(self):
        return self.cells

    def dedent(self):
        return DataRow(self.tail())

    def startswith(self, value):
        return self.head() == value

    def starts_for_loop(self):
        if not self.head().startswith(':'):
            return False
        return self.head().replace(':', '').upper().strip() == 'FOR'

    def starts_test_or_user_keyword_setting(self):
        head = self.head()
        return head and head[0] == '[' and head[-1] == ']'

    def is_indented(self):
        return self.head() == ''

    def is_continuing(self):
        return self.head() == self._row_continuation_marker

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

    def __nonzero__(self):
        return self.cells != []
