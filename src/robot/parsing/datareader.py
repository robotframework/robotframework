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

from robot import utils
from robot.output import LOGGER
from robot.errors import DataError

from populator import TestDataPopulator
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


class FileReader(object):

    def read(self, path, datafile):
        LOGGER.info("Parsing test case file '%s'" % path)
        source = self._open(path)
        try:
            self._get_reader(path).read(source, TestDataPopulator(datafile))
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
            raise DataError("No reader found for extension '%s'" % extension)


class DirectoryReader(object):
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def read(self, path, datadir):
        LOGGER.info("Parsing test data directory '%s'" % path)
        init, children = self._get_children(path)
        if init:
            try:
                FileReader().read(init, datadir)
            except DataError, err:
                LOGGER.error(unicode(err))
        for child in children:
            try:
                datadir.add_child(child)
            except DataError, err:
                LOGGER.info("Parsing data source '%s' failed: %s"
                            % (path, unicode(err)))

    def _get_children(self, dirpath):
        init = None
        children = []
        for name, path in self._list_dir(dirpath):
            if self._is_init_file(name, path):
                if not init:
                    init = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'" % path)
            elif self._is_ignored(name, path):
                LOGGER.info("Ignoring file or directory '%s'" % name)
            else:
                children.append(path)
        return init, children

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

