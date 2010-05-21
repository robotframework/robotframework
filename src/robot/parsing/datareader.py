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

import os
import re

from robot import utils
from robot.output import LOGGER
from robot.errors import DataError

from populator import (SettingTablePopulator, VariableTablePopulator,
                       TestTablePopulator, KeywordTablePopulator, NullPopulator)
from htmlreader import HtmlReader
from tsvreader import TsvReader
from txtreader import TxtReader
try:
    from restreader import RestReader
except ImportError:
    def RestReader():
        raise DataError("Using reStructuredText test data requires having "
                        "'docutils' module installed.")


READERS = {'html': HtmlReader, 'htm': HtmlReader, 'xhtml': HtmlReader,
           'tsv': TsvReader , 'rst': RestReader, 'rest': RestReader,
           'txt': TxtReader}

# Hook for external tools for altering ${CURDIR} processing
PROCESS_CURDIR = True


class FromFilePopulator(object):
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
        self._curdir = datafile.directory

    def populate(self, path):
        LOGGER.info("Parsing test case file '%s'." % path)
        source = self._open(path)
        try:
            self._get_reader(path).read(source, self)
        finally:
            source.close()

    def _open(self, path):
        if not os.path.isfile(path):
            raise DataError("Data source '%s' does not exist." % path)
        try:
            return open(path, 'rb')
        except:
            raise DataError(utils.get_error_message())

    def _get_reader(self, path):
        extension = path.lower().split('.')[-1]
        try:
            return READERS[extension]()
        except KeyError:
            raise DataError("No reader found for extension '%s'." % extension)

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
        data = [ cell if cell != '\\' else '' for cell in data]
        data = [ self._collapse_whitespace(cell) for cell in data]
        while data and not data[-1]:
            data.pop()
        return data

    def __nonzero__(self):
        return bool(self.cells or self.comments)


class FromDirectoryPopulator(object):
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def populate(self, path, datadir):
        LOGGER.info("Parsing test data directory '%s'" % path)
        initfile, children = self._get_children(path)
        datadir.initfile = initfile
        if initfile:
            try:
                FromFilePopulator(datadir).populate(initfile)
            except DataError, err:
                # TODO: Reverse control?
                LOGGER.error(unicode(err))
        for child in children:
            try:
                datadir.add_child(child)
            except DataError, err:
                LOGGER.info("Parsing data source '%s' failed: %s"
                            % (path, unicode(err)))

    def _get_children(self, dirpath):
        initfile = None
        children = []
        for name, path in self._list_dir(dirpath):
            if self._is_init_file(name, path):
                if not initfile:
                    initfile = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'." % path)
            elif self._is_ignored(name, path):
                LOGGER.info("Ignoring file or directory '%s'." % name)
            else:
                children.append(path)
        return initfile, children

    def _list_dir(self, path):
        # os.listdir returns Unicode entries when path is Unicode
        names = os.listdir(utils.unic(path))
        # http://bugs.jython.org/issue1593
        if utils.is_jython:
            from java.lang import String
            names = [utils.unic(String(n)) for n in names]
        for name in sorted(names, key=unicode.lower):
            yield name, os.path.join(path, name)

    def _is_init_file(self, name, path):
        if not os.path.isfile(path):
            return False
        base, extension = name.lower().rsplit('.', 1)
        return base == '__init__' and extension in READERS

    def _is_ignored(self, name, path):
        if name.startswith(self.ignored_prefixes):
            return True
        if os.path.isdir(path):
            return name in self.ignored_dirs
        extension = path.lower().split('.')[-1]
        return extension not in READERS

