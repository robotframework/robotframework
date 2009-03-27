#  Copyright 2008 Nokia Siemens Networks Oyj
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
from metadata import TestSuiteMetadata, TestCaseMetadata
from keywords import KeywordList
from userkeyword import UserHandlerList


def TestSuiteData(datasources, settings):
    datasources = [ utils.normpath(path) for path in datasources ]
    if not datasources:
        raise DataError("No data sources given.")
    elif len(datasources) > 1:
        return MultiSourceSuite(datasources, settings['SuiteNames'])
    elif os.path.isdir(datasources[0]):
        return DirectorySuite(datasources[0], settings['SuiteNames'])
    else:
        return FileSuite(datasources[0])


class _BaseSuite(BaseTestSuite):

    def __init__(self, rawdata):
        name, source = self._get_name_and_source(rawdata.source)
        BaseTestSuite.__init__(self, name, source)
        metadata = TestSuiteMetadata(rawdata)   
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

        
class FileSuite(_BaseSuite):
    
    def __init__(self, path):
        LOGGER.info("Parsing test case file '%s'" % path)
        rawdata = self._get_rawdata(path)
        _BaseSuite.__init__(self, rawdata)
        self.tests = self._process_testcases(rawdata)

    def _get_source(self, path):
        return path
        
    def _get_rawdata(self, path):
        rawdata = RawData(path)
        if rawdata.get_type() == rawdata.TESTCASE:
            return rawdata
        raise DataError("Test case file '%s' contains no test cases."  % path)

    def _process_testcases(self, rawdata):
        tests = []
        for rawtest in rawdata.testcases:
            try:
                tests.append(TestCase(rawtest))
            except:
                rawtest.report_invalid_syntax()
        return tests

            
class DirectorySuite(_BaseSuite):

    _ignored_prefixes = ['_', '.']
    _ignored_dirs = ['CVS']
    
    def __init__(self, path, suitenames):
        LOGGER.info("Parsing test suite directory '%s'" % path)
        # If we are included also all our children are
        if self._is_in_incl_suites(os.path.basename(os.path.normpath(path)),
                                   suitenames):
            suitenames = []  
        subitems, self.initfile = self._get_suite_items(path, suitenames)
        rawdata = self._get_rawdata(path)
        _BaseSuite.__init__(self, rawdata)
        self._process_subsuites(subitems, suitenames)
        if self.get_test_count() == 0 and len(suitenames) == 0:
            raise DataError("Test suite directory '%s' contains no test cases." 
                            % path)
        
    def _get_source(self, path):
        # 'path' points either to directory or __init__ file inside it
        return utils.get_directory(path)
        
    def _get_suite_items(self, dirpath, suitenames):
        names = os.listdir(dirpath)
        names.sort(lambda x,y: cmp(x.lower(), y.lower()))
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
            
    def _process_subsuites(self, paths, suitenames):
        for path in paths:
            try:
                if os.path.isdir(path):
                    suite = DirectorySuite(path, suitenames)
                else:
                    suite = FileSuite(path)
            except:
                msg = "Parsing data source '%s' failed: %s"
                LOGGER.info(msg % (path, utils.get_error_message()))
            else:
                self.suites.append(suite)

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
        for path in paths:
            try:
                if os.path.isdir(path):
                    suite = DirectorySuite(path, suitenames)
                else:
                    suite = FileSuite(path)
            except DataError, err:
                LOGGER.error("Parsing data source '%s' failed: %s" % (path, err))
            else:
                self.suites.append(suite)
        if self.get_test_count() == 0 and len(suitenames) == 0:
            # The latter check is to get a more informative exception in 
            # suite.filter_by_names later if --suite option was used.
            raise DataError('Data sources %s contain no test cases.' % 
                            (utils.seq2str(paths)))

    def _get_name_and_source(self, path):
        return '', None
        
    def set_names(self, name):
        if name is None:
            name = ' & '.join([suite.name for suite in self.suites])
        return BaseTestSuite.set_names(self, name)

    
class TestCase(BaseTestCase):
    
    def __init__(self, rawdata):
        BaseTestCase.__init__(self, utils.printable_name(rawdata.name))
        metadata = TestCaseMetadata(rawdata.metadata)
        self.doc = metadata['Documentation']
        self.tags = metadata['Tags']
        self.setup = metadata['Setup']
        self.teardown = metadata['Teardown']
        self.timeout = metadata['Timeout'] 
        self.keywords = KeywordList(rawdata.keywords)
