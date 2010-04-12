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
from robot.errors import DataError
from robot.common import BaseTestSuite, BaseTestCase
from robot.output import LOGGER

from rawdata import RawData, READERS
from metadata import TestCaseFileMetadata, TestSuiteInitFileMetadata, TestCaseMetadata
from keywords import KeywordList
from userkeyword import UserHandlerList


def TestSuiteData(datasources, suitenames=[]):
    datasources = [ utils.normpath(path) for path in datasources ]
    if not datasources:
        raise DataError("No data sources given.")
    elif len(datasources) > 1:
        return MultiSourceSuite(datasources, suitenames)
    elif os.path.isdir(datasources[0]):
        return DirectorySuite(datasources[0], suitenames)
    else:
        return FileSuite(datasources[0])


class _BaseSuite(BaseTestSuite):

    def __init__(self, rawdata, parent=None):
        name, source = self._get_name_and_source(rawdata.source)
        BaseTestSuite.__init__(self, name, source, parent)
        metadata = self._get_metadata(rawdata)
        self.doc = metadata['Documentation']
        self.suite_setup = metadata['SuiteSetup']
        self.suite_teardown = metadata['SuiteTeardown']
        self.test_setup = metadata['TestSetup']
        self.test_teardown = metadata['TestTeardown']
        self.default_tags = metadata['DefaultTags']
        self.force_tags = metadata['ForceTags']
        self.test_timeout = metadata['TestTimeout']
        self.metadata = metadata.user_metadata
        self.imports = metadata.imports
        self.variables = rawdata.variables
        self.user_keywords = UserHandlerList(rawdata.keywords)

    def _get_name_and_source(self, path):
        source = self._get_source(path)
        return self._get_name(source), source

    def _get_name(self, source):
        return utils.printable_name_from_path(source)

    def _create_subsuites(self, paths, suitenames, error):
        for path in paths:
            try:
                if os.path.isdir(path):
                    DirectorySuite(path, suitenames, parent=self)
                else:
                    FileSuite(path, parent=self)
            except DataError:
                LOGGER.info("Parsing data source '%s' failed: %s"
                            % (path, utils.get_error_message()))
        # The latter check is to get a more informative exception in
        # suite.filter_by_names later if --suite option was used.
        if self.get_test_count() == 0 and len(suitenames) == 0:
            if self.parent is not None:
                self.parent.suites.pop()
            raise DataError(error)


class FileSuite(_BaseSuite):

    def __init__(self, path, parent=None):
        LOGGER.info("Parsing test case file '%s'" % path)
        rawdata = self._get_rawdata(path)
        _BaseSuite.__init__(self, rawdata, parent)
        self._create_testcases(rawdata)

    def _get_metadata(self, rawdata):
        return TestCaseFileMetadata(rawdata)

    def _get_source(self, path):
        return path

    def _get_rawdata(self, path):
        rawdata = RawData(path)
        if rawdata.get_type() == rawdata.TESTCASE:
            return rawdata
        raise DataError("Test case file '%s' contains no test cases."  % path)

    def _create_testcases(self, rawdata):
        for rawtest in rawdata.testcases:
            try:
                TestCase(rawtest, self)
            except:
                rawtest.report_invalid_syntax()


class DirectorySuite(_BaseSuite):

    _ignored_prefixes = ['_', '.']
    _ignored_dirs = ['CVS']

    def __init__(self, path, suitenames, parent=None):
        LOGGER.info("Parsing test suite directory '%s'" % path)
        # If we are included also all our children are
        if self._is_in_incl_suites(os.path.basename(os.path.normpath(path)),
                                   suitenames):
            suitenames = []
        subitems, self.initfile = self._get_suite_items(path, suitenames)
        rawdata = self._get_rawdata(path)
        _BaseSuite.__init__(self, rawdata, parent)
        error = "Test suite directory '%s' contains no test cases." % path
        self._create_subsuites(subitems, suitenames, error)

    def _get_metadata(self, rawdata):
        return TestSuiteInitFileMetadata(rawdata)

    def _get_source(self, path):
        # 'path' points either to directory or __init__ file inside it
        return utils.get_directory(path)

    def _get_suite_items(self, dirpath, suitenames):
        names = self._list_dir(dirpath)
        files = []
        initfile = None
        for name in names:
            path = os.path.join(dirpath, name)
            if self._is_suite_init_file(name, path):
                if initfile is None:
                    initfile = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'" % path)
            elif self._is_ignored(name, path, suitenames):
                LOGGER.info("Ignoring file or directory '%s'" % name)
            else:
                files.append(path)
        return files, initfile

    def _list_dir(self, path):
        # Want to make sure path is Unicode because then os.listdir also
        # returns entries as Unicode...
        names = os.listdir(utils.unic(path))
        # ... except on Jython: http://bugs.jython.org/issue1593
        if utils.is_jython:
            from java.lang import String
            names = [ utils.unic(String(n)) for n in names ]
        return sorted(names, key=unicode.lower)

    def _get_rawdata(self, path):
        if self.initfile is None:
            LOGGER.info("No test suite directory init file")
            return RawData(path)
        LOGGER.info("Parsing test suite directory init file '%s'" % self.initfile)
        rawdata = RawData(self.initfile)
        if rawdata.get_type() in [rawdata.INITFILE, rawdata.EMPTY]:
            return rawdata
        LOGGER.error("Test suite directory initialization file '%s' "
                     "contains test cases and is ignored." % self.initfile)
        return RawData(path)

    def _is_ignored(self, name, path, incl_suites):
        if name[0] in self._ignored_prefixes:
            return True
        if os.path.isdir(path):
            return name in self._ignored_dirs
        root, ext = os.path.splitext(name.lower())
        if not READERS.has_key(ext):
            return True
        return not self._is_in_incl_suites(root, incl_suites)

    def _is_in_incl_suites(self, name, incl_suites):
        if incl_suites == []:
            return True
        # Match only to the last part of name given like '--suite parent.child'
        incl_suites = [ incl.split('.')[-1] for incl in incl_suites ]
        name = name.split('__', 1)[-1]  # Strip possible prefix
        return utils.matches_any(name, incl_suites, ignore=['_'])

    def _is_suite_init_file(self, name, path):
        if not os.path.isfile(path):
            return False
        root, ext = os.path.splitext(name.lower())
        return root == '__init__' and READERS.has_key(ext)


class MultiSourceSuite(_BaseSuite):

    def __init__(self, paths, suitenames):
        LOGGER.info("Parsing multiple data sources %s" % utils.seq2str(paths))
        _BaseSuite.__init__(self, RawData(None))
        error = 'Data sources %s contain no test cases.' % (utils.seq2str(paths))
        self._create_subsuites(paths, suitenames, error)

    def _get_metadata(self, rawdata):
        return TestCaseFileMetadata(rawdata)

    def _get_name_and_source(self, path):
        return '', None


class TestCase(BaseTestCase):

    def __init__(self, rawdata, parent):
        BaseTestCase.__init__(self, utils.printable_name(rawdata.name), parent)
        metadata = TestCaseMetadata(rawdata.metadata)
        self.doc = metadata['Documentation']
        self.tags = metadata['Tags']
        self.setup = metadata['Setup']
        self.teardown = metadata['Teardown']
        self.timeout = metadata['Timeout']
        self.keywords = KeywordList(rawdata.keywords)
