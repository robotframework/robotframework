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
from .robotreader import RobotReader
from .restreader import RestReader


READERS = {'html': HtmlReader, 'htm': HtmlReader, 'xhtml': HtmlReader,
           'tsv': TsvReader , 'rst': RestReader, 'rest': RestReader,
           'txt': RobotReader, 'robot': RobotReader}

# Hook for external tools for altering ${CURDIR} processing
PROCESS_CURDIR = True


class NoTestsFound(DataError):
    pass


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

    def populate(self, path, resource=False):
        LOGGER.info("Parsing file '%s'." % path)
        source = self._open(path)
        try:
            self._get_reader(path, resource).read(source, self)
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

    def _get_reader(self, path, resource=False):
        file_format = os.path.splitext(path.lower())[-1][1:]
        if resource and file_format == 'resource':
            file_format = 'robot'
        try:
            return READERS[file_format]()
        except KeyError:
            raise DataError("Unsupported file format '%s'." % file_format)

    def start_table(self, header):
        self._populator.populate()
        table = self._datafile.start_table(DataRow(header).all)
        self._populator = self._populators[table.type](table) \
                if table is not None else NullPopulator()
        return bool(self._populator)

    def eof(self):
        self._populator.populate()
        self._populator = NullPopulator()
        return bool(self._datafile)

    def add(self, row):
        if PROCESS_CURDIR and self._curdir:
            row = self._replace_curdirs_in(row)
        data = DataRow(row)
        if data:
            self._populator.add(data)

    def _replace_curdirs_in(self, row):
        old, new = '${CURDIR}', self._curdir
        return [cell if old not in cell else cell.replace(old, new)
                for cell in row]


class FromDirectoryPopulator(object):
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def populate(self, path, datadir, include_suites=None,
                 include_extensions=None, recurse=True):
        LOGGER.info("Parsing directory '%s'." % path)
        include_suites = self._get_include_suites(path, include_suites)
        init_file, children = self._get_children(path, include_extensions,
                                                 include_suites)
        if init_file:
            self._populate_init_file(datadir, init_file)
        if recurse:
            self._populate_children(datadir, children, include_extensions,
                                    include_suites)

    def _populate_init_file(self, datadir, init_file):
        datadir.initfile = init_file
        try:
            FromFilePopulator(datadir).populate(init_file)
        except DataError as err:
            LOGGER.error(err.message)

    def _populate_children(self, datadir, children, include_extensions,
                           include_suites):
        for child in children:
            try:
                datadir.add_child(child, include_suites, include_extensions)
            except NoTestsFound:
                LOGGER.info("Data source '%s' has no tests or tasks." % child)
            except DataError as err:
                LOGGER.error("Parsing '%s' failed: %s" % (child, err.message))

    def _get_include_suites(self, path, incl_suites):
        if not incl_suites:
            return None
        if not isinstance(incl_suites, SuiteNamePatterns):
            incl_suites = SuiteNamePatterns(
                    self._create_included_suites(incl_suites))
        # If a directory is included, also all its children should be included.
        if self._is_in_included_suites(os.path.basename(path), incl_suites):
            return None
        return incl_suites

    def _create_included_suites(self, incl_suites):
        for suite in incl_suites:
            yield suite
            while '.' in suite:
                suite = suite.split('.', 1)[1]
                yield suite

    def _get_children(self, dirpath, incl_extensions, incl_suites):
        init_file = None
        children = []
        for path, is_init_file in self._list_dir(dirpath, incl_extensions,
                                                 incl_suites):
            if is_init_file:
                if not init_file:
                    init_file = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'." % path)
            else:
                children.append(path)
        return init_file, children

    def _list_dir(self, dir_path, incl_extensions, incl_suites):
        # os.listdir returns Unicode entries when path is Unicode
        dir_path = unic(dir_path)
        names = os.listdir(dir_path)
        for name in sorted(names, key=lambda item: item.lower()):
            name = unic(name)  # needed to handle nfc/nfd normalization on OSX
            path = os.path.join(dir_path, name)
            base, ext = os.path.splitext(name)
            ext = ext[1:].lower()
            if self._is_init_file(path, base, ext, incl_extensions):
                yield path, True
            elif self._is_included(path, base, ext, incl_extensions, incl_suites):
                yield path, False
            else:
                LOGGER.info("Ignoring file or directory '%s'." % path)

    def _is_init_file(self, path, base, ext, incl_extensions):
        return (base.lower() == '__init__' and
                self._extension_is_accepted(ext, incl_extensions) and
                os.path.isfile(path))

    def _extension_is_accepted(self, ext, incl_extensions):
        if incl_extensions:
            return ext in incl_extensions
        return ext in READERS

    def _is_included(self, path, base, ext, incl_extensions, incl_suites):
        if base.startswith(self.ignored_prefixes):
            return False
        if os.path.isdir(path):
            return base not in self.ignored_dirs or ext
        if not self._extension_is_accepted(ext, incl_extensions):
            return False
        return self._is_in_included_suites(base, incl_suites)

    def _is_in_included_suites(self, name, incl_suites):
        if not incl_suites:
            return True
        return incl_suites.match(self._split_prefix(name))

    def _split_prefix(self, name):
        return name.split('__', 1)[-1]
