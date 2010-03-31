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
from robot.errors import DataError

from rawdatatables import SimpleTable, ComplexTable
from htmlreader import HtmlReader
from tsvreader import TsvReader
from txtreader import TxtReader
try:
    from restreader import RestReader
except ImportError:
    def RestReader():
        raise DataError("Using reStructuredText test data requires having "
                        "'docutils' module installed.")


# Hook for external tools for altering ${CURDIR} processing
PROCESS_CURDIR = True

READERS = { '.html': HtmlReader, '.htm': HtmlReader, '.xhtml': HtmlReader,
            '.tsv': TsvReader , '.rst': RestReader, '.rest': RestReader,
            '.txt': TxtReader }

SETTING_TABLES = ['Setting','Settings','Metadata']
VARIABLE_TABLES = ['Variable','Variables']
TESTCASE_TABLES = ['Test Case','Test Cases']
KEYWORD_TABLES = ['Keyword','Keywords','User Keyword','User Keywords']
TABLE_NAMES = SETTING_TABLES + VARIABLE_TABLES + TESTCASE_TABLES + KEYWORD_TABLES


# TODO: is strip_comments needed?
def RawData(path, strip_comments=True):
    if path is None or os.path.isdir(path):
        return EmptyRawData(path)
    if not os.path.isfile(path):
        raise DataError("Data source '%s' does not exist." % path)
    try:
        datafile = open(path, 'rb')
    except:
        raise DataError(utils.get_error_message())
    try:
        return _read_data(datafile, path, strip_comments)
    finally:
        datafile.close()


def _read_data(datafile, path, strip_comments):
    ext = os.path.splitext(path)[1].lower()
    try:
        reader = READERS[ext]()
    except KeyError:
        raise DataError("Unsupported file format '%s'" % ext)
    rawdata = TabularRawData(path, strip_comments)
    try:
        reader.read(datafile, rawdata)
    except:
        raise DataError("Parsing '%s' failed: %s" % (path, utils.get_error_message()))
    return rawdata


class _BaseRawData:
    """Represents all unprocessed test data in one target file/directory."""

    EMPTY = 1
    RESOURCE = 2
    INITFILE = 3
    TESTCASE = 4

    def __init__(self, source):
        self.source = source
        self.settings = []
        self.variables = []
        self.keywords = []
        self.testcases = []
        self._type = None

    def is_empty(self):
        return self.get_type() == self.EMPTY

    def get_type(self):
        if self._type is None:
            self._type = self._get_type()
        return self._type

    def _get_type(self):
        if len(self.testcases) > 0:
            return self.TESTCASE
        if len(self.settings) + len(self.variables) + len(self.keywords) == 0:
            return self.EMPTY
        if os.path.splitext(os.path.basename(self.source))[0].lower() == '__init__':
            return self.INITFILE
        return self.RESOURCE


class EmptyRawData(_BaseRawData):
    pass


class TabularRawData(_BaseRawData):
    """Populates RawData from tabular test data"""

    _whitespace_regexp = re.compile('\s+')

    def __init__(self, path, strip_comments=True):
        _BaseRawData.__init__(self, path)
        self._table = None
        self._strip_comments = strip_comments
        # ${CURDIR} is replaced the data and thus must be escaped
        self._curdir = utils.get_directory(path).replace('\\','\\\\')

    def start_table(self, name):
        """Makes rawdata instance ready to receive new data

        This method should be called with table's name before adding table's
        data with 'add_row'.
        Returns False if data from specified table will not be processed.
        Client should thus check the return value and only call 'add_row' if
        it is True.
        """
        name = self._collapse_whitespace(name)
        table, data = self._get_table_and_data(name)
        if table is not None:
            self._table = table(name, self.source, data)
        else:
            self._table = None
        return self._table is not None

    def _get_table_and_data(self, name):
        if utils.eq_any(name, SETTING_TABLES):
            return SimpleTable, self.settings
        if utils.eq_any(name, VARIABLE_TABLES):
            return SimpleTable, self.variables
        if utils.eq_any(name, TESTCASE_TABLES):
            return ComplexTable, self.testcases
        if utils.eq_any(name, KEYWORD_TABLES):
            return ComplexTable, self.keywords
        return None, None

    def add_row(self, cells, repeat=1):
        """Processes cells from given row.

        Client can use 'repeat' to tell that it has that many similar rows
        instead of calling add_row that many times.
        """
        if self._table is not None:
            self._table.add_row(self._process_cells(cells), repeat)

    def _process_cells(self, cells):
        """Trims cells and process ${CURDIR}.

        Trimming means collapsing whitespace, removing trailing empty cells and
        removing comments.
        """
        temp = []
        for cell in cells:
            cell = self._collapse_whitespace(cell)
            if self._strip_comments and cell.startswith('#'):
                break
            if PROCESS_CURDIR:
                cell = cell.replace('${CURDIR}', self._curdir)
            temp.append(cell)
        # Strip trailing empty cells
        for i in range(len(temp), 0, -1):
            if temp[i-1] != '':
                break
            else:
                temp.pop()
        return temp

    def _collapse_whitespace(self, cell):
        # Remove leading and trailing whitespace and collapse internal
        return self._whitespace_regexp.sub(' ', cell).strip()
