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
        self._populator = NullPopulator()
        self._comments = []

    def add(self, row):
        if self._is_cacheable_comment_row(row):
            self._comments.append(row)
            return
        if not self._is_continuing(row):
            self._populator.populate()
            self._populator = self._get_populator(row)
        self._add_cached_comments_to(self._populator)
        self._populator.add(row)

    def _add_cached_comments_to(self, populator):
        for crow in self._comments:
            populator.add(crow)
        self._comments = []

    def populate(self):
        self._add_cached_comments_to(self._populator)
        self._populator.populate()

    def _is_continuing(self, row):
        return row.is_continuing()

    def _is_cacheable_comment_row(self, row):
        return row.is_commented()


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
        first_cell = row.head
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
        return VariablePopulator(self._table.add)


class TestTablePopulator(_TablePopulator):

    def _get_table(self, datafile):
        return datafile.testcase_table

    def _get_populator(self, row):
        return TestCasePopulator(self._table.add)

    def _is_continuing(self, row):
        return row.is_indented() or row.is_commented()

    def _is_cacheable_comment_row(self, row):
        return row.is_commented() and isinstance(self._populator, NullPopulator)

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
            self._declaration.extend(row.tail)
            return False
        return True

    def populate(self):
        self._populator.populate()


class _TestCaseUserKeywordPopulator(Populator):

    def __init__(self, test_or_uk_creator):
        self._test_or_uk_creator = test_or_uk_creator
        self._test_or_uk = None
        self._populator = NullPopulator()
        self._comments = []

    def add(self, row):
        if row.is_commented():
            self._comments.append(row)
            return
        if not self._test_or_uk:
            self._test_or_uk = self._test_or_uk_creator(row.head)
        dedented_row = row.dedent()
        if dedented_row:
            if not self._continues(dedented_row):
                self._populator.populate()
                self._populator = self._get_populator(dedented_row)
                self._populate_cached_comments()
            else:
                for crow in self._comments:
                    self._populator.add(crow)
                self._comments = []
            self._populator.add(dedented_row)

    def _populate_cached_comments(self):
        for crow in self._comments:
            populator = StepPopulator(self._test_or_uk.add_step)
            populator.add(crow)
            populator.populate()
        self._comments = []

    def populate(self):
        self._populator.populate()
        self._populate_cached_comments()

    def _get_populator(self, row):
        if row.starts_test_or_user_keyword_setting():
            setter = self._setting_setter(row.head)
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


class Comments(object):

    def __init__(self):
        self._crows = []

    def add(self, row):
        if row.comments:
            self._crows.append(row.comments)

    def formatted_value(self):
        return '\n'.join(' | '.join(row) for row in self._crows)


class _PropertyPopulator(Populator):

    def __init__(self, setter):
        self._setter = setter
        self._value = []
        self._comments = Comments()

    def add(self, row):
        if not row.is_commented():
            self._add(row)
        self._comments.add(row)


class NameAndValuePropertyPopulator(_PropertyPopulator):

    def _add(self, row):
        self._value.extend(row.all)

    def populate(self):
        name, value = self._value[0], self._value[1:]
        self._setter(name, value, self._comments.formatted_value())


class VariablePopulator(NameAndValuePropertyPopulator):

    def _add(self, row):
        if row.is_continuing():
            row = row.dedent()
        self._value.extend(row.all)


class SettingPopulator(_PropertyPopulator):

    def _add(self, row):
        self._value.extend(row.tail)

    def populate(self):
        self._setter(self._value, self._comments.formatted_value())


class SettingTableNameValuePopulator(NameAndValuePropertyPopulator):

    def _add(self, row):
        self._value.extend(row.tail)


class OldStyleMetadataPopulator(NameAndValuePropertyPopulator):
    olde_metadata_prefix = 'meta:'

    def _add(self, row):
        if self._is_metadata_with_olde_prefix(row.head):
            values = self._extract_name_from_olde_style_meta_cell(row.head) + row.tail
        else:
            values = row.tail
        self._value.extend(values)

    def _extract_name_from_olde_style_meta_cell(self, first_cell):
        return [first_cell.split(':', 1)[1].strip()]

    def _is_metadata_with_olde_prefix(self, first_cell):
        return first_cell.lower().startswith(self.olde_metadata_prefix)


class StepPopulator(_PropertyPopulator):

    def _add(self, row):
        if row.is_continuing():
            row = row.dedent()
        self._value.extend(row.all)

    def populate(self):
        if self._value or self._comments:
            self._setter(self._value, self._comments.formatted_value())


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
            if os.path.isdir(datafile.source):
                return datafile.source
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
        if PROCESS_CURDIR and self._curdir:
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
        self.cells, self.comments = self._parse(cells)
        self.head = self.cells[0] if self.cells else None
        self.tail = self.cells[1:] if self.cells else None
        self.all = self.cells

    def dedent(self):
        dedented = DataRow(self.tail)
        dedented.comments = self.comments
        return dedented

    def startswith(self, value):
        return self.head() == value

    def starts_for_loop(self):
        if self.head and self.head.startswith(':'):
            return self.head.replace(':', '').upper().strip() == 'FOR'
        return False

    def starts_test_or_user_keyword_setting(self):
        head = self.head
        return head and head[0] == '[' and head[-1] == ']'

    def is_indented(self):
        return self.head == ''

    def is_continuing(self):
        return self.head == self._row_continuation_marker

    def is_commented(self):
        return bool(not self.cells and self.comments)

    def _parse(self, row):
        return self._purge_empty_cells(self._extract_data(row)), \
            self._extract_comments(row)

    def _collapse_whitespace(self, value):
        return self._whitespace_regexp.sub(' ', value).strip()

    def _extract_comments(self, row):
        if not row:
            return []
        comments = []
        for c in row:
            if c.startswith('#') and not comments:
                comments.append(c[1:])
            elif comments:
                comments.append(c)
        return comments

    def _extract_data(self, row):
        if not row:
            return []
        data = []
        for c in row:
            if c.startswith('#'):
                return data
            data.append(c)
        return data

    def _purge_empty_cells(self, data):
        data = [ self._collapse_whitespace(cell) for cell in data]
        while data and not data[-1]:
            data.pop()
        return data

    def __nonzero__(self):
        return bool(self.cells or self.comments)
