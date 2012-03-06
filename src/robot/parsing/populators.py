#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from robot import utils
from robot.output import LOGGER
from robot.errors import DataError
from robot.model import SuiteNamePatterns

from datarow import DataRow
from tablepopulators import (SettingTablePopulator, VariableTablePopulator,
                             TestTablePopulator, KeywordTablePopulator,
                             NullPopulator)
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
    _populators = {'setting': SettingTablePopulator,
                   'variable': VariableTablePopulator,
                   'test case': TestTablePopulator,
                   'keyword': KeywordTablePopulator}

    def __init__(self, datafile):
        self._datafile = datafile
        self._current_populator = NullPopulator()
        self._curdir = self._get_curdir(datafile.directory)

    def _get_curdir(self, path):
        return path.replace('\\','\\\\') if path else None

    def populate(self, path):
        LOGGER.info("Parsing file '%s'." % path)
        source = self._open(path)
        try:
            self._get_reader(path).read(source, self)
        except:
            raise DataError(utils.get_error_message())
        finally:
            source.close()

    def _open(self, path):
        if not os.path.isfile(path):
            raise DataError("Data source does not exist.")
        try:
            return open(path, 'rb')
        except:
            raise DataError(utils.get_error_message())

    def _get_reader(self, path):
        extension = os.path.splitext(path.lower())[-1][1:]
        try:
            return READERS[extension]()
        except KeyError:
            raise DataError("Unsupported file format '%s'." % extension)

    def start_table(self, header):
        self._current_populator.populate()
        table = self._datafile.start_table(DataRow(header).all)
        self._current_populator = self._populators[table.type](table) \
                                    if table is not None else NullPopulator()
        return bool(self._current_populator)

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


class FromDirectoryPopulator(object):
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def populate(self, path, datadir, include_suites, warn_on_skipped,
                 recurse=True):
        LOGGER.info("Parsing test data directory '%s'" % path)
        include_suites = self._get_include_suites(path, include_suites)
        init_file, children = self._get_children(path, include_suites)
        if init_file:
            self._populate_init_file(datadir, init_file)
        if recurse:
            self._populate_chidren(datadir, children, include_suites,
                                   warn_on_skipped)

    def _populate_init_file(self, datadir, init_file):
        datadir.initfile = init_file
        try:
            FromFilePopulator(datadir).populate(init_file)
        except DataError, err:
            LOGGER.error(unicode(err))

    def _populate_chidren(self, datadir, children, include_suites, warn_on_skipped):
        for child in children:
            try:
                datadir.add_child(child, include_suites)
            except DataError, err:
                self._log_failed_parsing("Parsing data source '%s' failed: %s"
                            % (child, unicode(err)), warn_on_skipped)

    def _log_failed_parsing(self, message, warn):
        if warn:
            LOGGER.warn(message)
        else:
            LOGGER.info(message)

    def _get_include_suites(self, path, incl_suites):
        if not isinstance(incl_suites, SuiteNamePatterns):
            # Use only the last part of names given like '--suite parent.child'
            incl_suites = SuiteNamePatterns(i.split('.')[-1] for i in incl_suites)
        if not incl_suites:
            return incl_suites
        # If a directory is included, also all its children should be included.
        if self._directory_is_included(path, incl_suites):
            return SuiteNamePatterns()
        return incl_suites

    def _directory_is_included(self, path, incl_suites):
        name = os.path.basename(os.path.normpath(path))
        return self._is_in_included_suites(name, incl_suites)

    def _get_children(self, dirpath, incl_suites):
        init_file = None
        children = []
        for name, path in self._list_dir(dirpath):
            if self._is_init_file(name, path):
                if not init_file:
                    init_file = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'." % path)
            elif self._is_included(name, path, incl_suites):
                children.append(path)
            else:
                LOGGER.info("Ignoring file or directory '%s'." % name)
        return init_file, children

    def _list_dir(self, path):
        # os.listdir returns Unicode entries when path is Unicode
        names = os.listdir(utils.unic(path))
        for name in sorted(names, key=unicode.lower):
            # utils.unic needed to handle nfc/nfd normalization on OSX
            yield utils.unic(name), utils.unic(os.path.join(path, name))

    def _is_init_file(self, name, path):
        if not os.path.isfile(path):
            return False
        base, extension = os.path.splitext(name.lower())
        return base == '__init__' and extension[1:] in READERS

    def _is_included(self, name, path, incl_suites):
        if name.startswith(self.ignored_prefixes):
            return False
        if os.path.isdir(path):
            return name not in self.ignored_dirs
        base, extension = os.path.splitext(name.lower())
        return (extension[1:] in READERS and
                self._is_in_included_suites(base, incl_suites))

    def _is_in_included_suites(self, name, incl_suites):
        return not incl_suites or incl_suites.match(self._split_prefix(name))

    def _split_prefix(self, name):
        return name.split('__', 1)[-1]
