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

import os

from robot.errors import DataError
from robot.model import SuiteNamePatterns
from robot.output import LOGGER
from robot.utils import get_error_message, unic

from .datarow import DataRow
from .tablepopulators import (SettingTablePopulator, VariableTablePopulator,
                              TestTablePopulator, KeywordTablePopulator,
                              NullPopulator)
from .htmlreader import HtmlReader
from .tsvreader import TsvReader
from .txtreader import TxtReader
from .restreader import RestReader


READERS = {'html': HtmlReader, 'htm': HtmlReader, 'xhtml': HtmlReader,
           'tsv': TsvReader , 'rst': RestReader, 'rest': RestReader,
           'txt': TxtReader, 'robot': TxtReader}

# Hook for external tools for altering ${CURDIR} processing
PROCESS_CURDIR = True


class FromFilePopulator(object):
    _populators = {'setting': SettingTablePopulator,
                   'variable': VariableTablePopulator,
                   'test case': TestTablePopulator,
                   'keyword': KeywordTablePopulator}

    def __init__(self, datafile):
        self._datafile = datafile
        self._populator = NullPopulator()
        self._curdir = self._get_curdir(datafile.directory)

    def _get_curdir(self, path):
        return path.replace('\\','\\\\') if path else None

    def populate(self, path):
        LOGGER.info("Parsing file '%s'." % path)
        source = self._open(path)
        try:
            self._get_reader(path).read(source, self)
        except:
            raise DataError(get_error_message())
        finally:
            source.close()

    def _open(self, path):
        if not os.path.isfile(path):
            raise DataError("Data source does not exist.")
        try:
            # IronPython handles BOM incorrectly if not using binary mode:
            # https://ironpython.codeplex.com/workitem/34655
            return open(path, 'rb')
        except:
            raise DataError(get_error_message())

    def _get_reader(self, path):
        extension = os.path.splitext(path.lower())[-1][1:]
        try:
            return READERS[extension]()
        except KeyError:
            raise DataError("Unsupported file format '%s'." % extension)

    def start_table(self, header):
        self._populator.populate()
        table = self._datafile.start_table(DataRow(header).all)
        self._populator = self._populators[table.type](table) \
                if table is not None else NullPopulator()
        return bool(self._populator)

    def eof(self):
        self._populator.populate()

    def add(self, row):
        if PROCESS_CURDIR and self._curdir:
            row = self._replace_curdirs_in(row)
        data = DataRow(row)
        if data:
            self._populator.add(data)

    def _replace_curdirs_in(self, row):
        return [cell.replace('${CURDIR}', self._curdir) for cell in row]


class FromDirectoryPopulator(object):
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def populate(self, path, datadir, include_suites=None,
                 warn_on_skipped=False, extensions=None, recurse=True):
        LOGGER.info("Parsing test data directory '%s'" % path)
        include_suites = self._get_include_suites(path, include_suites or [])
        init_file, children = self._get_children(path, extensions, include_suites)
        if init_file:
            self._populate_init_file(datadir, init_file)
        if recurse:
            self._populate_children(datadir, children, include_suites,
                                    extensions, warn_on_skipped)

    def _populate_init_file(self, datadir, init_file):
        datadir.initfile = init_file
        try:
            FromFilePopulator(datadir).populate(init_file)
        except DataError as err:
            LOGGER.error(err.message)

    def _populate_children(self, datadir, children, include_suites, extensions,
                           warn_on_skipped):
        for child in children:
            try:
                datadir.add_child(child, include_suites, extensions,
                                  warn_on_skipped)
            except DataError as err:
                self._log_failed_parsing("Parsing data source '%s' failed: %s"
                                         % (child, err.message), warn_on_skipped)

    def _log_failed_parsing(self, message, warn):
        if warn:
            LOGGER.warn(message)
        else:
            LOGGER.info(message)

    def _get_include_suites(self, path, incl_suites):
        if not isinstance(incl_suites, SuiteNamePatterns):
            incl_suites = SuiteNamePatterns(self._create_included_suites(incl_suites))
        if not incl_suites:
            return incl_suites
        # If a directory is included, also all its children should be included.
        if self._directory_is_included(path, incl_suites):
            return SuiteNamePatterns()
        return incl_suites

    def _create_included_suites(self, incl_suites):
        for suite in incl_suites:
            yield suite
            while '.' in suite:
                suite = suite.split('.', 1)[1]
                yield suite

    def _directory_is_included(self, path, incl_suites):
        name = os.path.basename(os.path.normpath(path))
        return self._is_in_included_suites(name, incl_suites)

    def _get_children(self, dirpath, extensions, incl_suites):
        init_file = None
        children = []
        for path, base in self._list_dir(dirpath, extensions, incl_suites):
            if self._is_init_file(path, base):
                if not init_file:
                    init_file = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'." % path)
            else:
                children.append(path)
        return init_file, children

    def _list_dir(self, dir_path, extensions, incl_suites):
        # os.listdir returns Unicode entries when path is Unicode
        names = os.listdir(unic(dir_path))
        for name in sorted(names, key=lambda item: item.lower()):
            name = unic(name)  # needed to handle nfc/nfd normalization on OSX
            base, ext = os.path.splitext(name)
            ext = ext[1:].lower()
            path = os.path.join(dir_path, name)
            if self._is_included(path, base, ext, extensions, incl_suites):
                yield path, base
            else:
                LOGGER.info("Ignoring file or directory '%s'." % name)

    def _is_included(self, path, base, ext, extensions, incl_suites):
        if base.startswith(self.ignored_prefixes) and base.lower() != '__init__':
            return False
        if os.path.isdir(path):
            return base not in self.ignored_dirs or ext
        if extensions and ext not in extensions:
            return False
        if ext not in READERS:
            return False
        return self._is_in_included_suites(base, incl_suites)

    def _is_in_included_suites(self, name, incl_suites):
        return not incl_suites or incl_suites.match(self._split_prefix(name))

    def _is_init_file(self, path, base):
        # TODO: Should only support `__init__`, not `__INIT__`.
        return os.path.isfile(path) and base.lower() == '__init__'

    def _split_prefix(self, name):
        return name.split('__', 1)[-1]
