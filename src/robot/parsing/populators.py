#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
                  'testcase': TestTablePopulator,
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

    def populate(self, path, datadir, include_suites):
        LOGGER.info("Parsing test data directory '%s'" % path)
        include_sub_suites = self._get_include_suites(path, include_suites)
        initfile, children = self._get_children(path, include_sub_suites)
        datadir.initfile = initfile
        if initfile:
            try:
                FromFilePopulator(datadir).populate(initfile)
            except DataError, err:
                LOGGER.error(unicode(err))
        for child in children:
            try:
                datadir.add_child(child, include_sub_suites)
            except DataError, err:
                LOGGER.info("Parsing data source '%s' failed: %s"
                            % (child, unicode(err)))

    def _get_include_suites(self, path, include_suites):
        # If directory is included also all it children should be included
        if self._is_in_incl_suites(os.path.basename(os.path.normpath(path)),
                                   include_suites):
            return []
        return include_suites

    def _get_children(self, dirpath, include_suites):
        initfile = None
        children = []
        for name, path in self._list_dir(dirpath):
            if self._is_init_file(name, path):
                if not initfile:
                    initfile = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'." % path)
            elif self._is_included(name, path, include_suites):
                children.append(path)
            else:
                LOGGER.info("Ignoring file or directory '%s'." % name)
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
        base, extension = os.path.splitext(name.lower())
        return base == '__init__' and extension[1:] in READERS

    def _is_included(self, name, path, include_suites):
        if name.startswith(self.ignored_prefixes):
            return False
        if os.path.isdir(path):
            return name not in self.ignored_dirs
        base, extension = os.path.splitext(name.lower())
        return (extension[1:] in READERS and
                self._is_in_incl_suites(base, include_suites))

    def _is_in_incl_suites(self, name, include_suites):
        if include_suites == []:
            return True
        # Match only to the last part of name given like '--suite parent.child'
        include_suites = [ incl.split('.')[-1] for incl in include_suites ]
        name = name.split('__', 1)[-1]  # Strip possible prefix
        return utils.matches_any(name, include_suites, ignore=['_'])

