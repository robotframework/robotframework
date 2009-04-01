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


from robot import utils
from robot.common import BaseTestSuite, BaseTestCase
from robot.parsing import TestSuiteData
from robot.errors import ExecutionFailed
from robot.variables import GLOBAL_VARIABLES

from fixture import Setup, Teardown
from timeouts import TestTimeout
from keywords import KeywordFactory
from namespace import Namespace
from userkeyword import UserLibrary


def TestSuite(datasources, settings):
    suitedata = TestSuiteData(datasources, settings['SuiteNames'])
    suite = RunnableTestSuite(suitedata)
    suite.set_options(settings)
    return suite
    
    
class RunnableTestSuite(BaseTestSuite):
    
    def __init__(self, data, testdefaults=None, parent=None):
        BaseTestSuite.__init__(self, data.name, data.source, parent)
        self.variables = GLOBAL_VARIABLES.copy()
        self.variables.set_from_variable_table(data.variables)
        self.source = data.source
        self.doc = data.doc or ''
        self.metadata = data.metadata
        self.imports = data.imports
        self.user_keywords = UserLibrary(data.user_keywords)
        self.setup = data.suite_setup or []
        self.teardown = data.suite_teardown or []
        if not testdefaults:
            testdefaults = _TestCaseDefaults()
        testdefaults.add_defaults(data)
        for suite in data.suites:
            RunnableTestSuite(suite, testdefaults.copy(), parent=self) 
        for test in data.tests:
            RunnableTestCase(test, testdefaults, parent=self) 
        self._exit_on_failure = False
        
    def run(self, output, parent=None, error=None):
        self.starttime = utils.get_timestamp()
        self.namespace = Namespace(self, parent)
        self.namespace.variables['${SUITE_NAME}'] = self.longname
        init_err = self._init_suite(self.namespace.variables)
        output.start_suite(self)
        self.status = 'RUNNING'
        setup_err = self._run_fixture(self.setup, output, self.namespace, error, init_err)
        child_err = self._get_child_error(error, init_err, setup_err)
        for suite in self.suites:
            suite.run(output, self, child_err)
            if self._exit_on_failure and not child_err and suite.critical_stats.failed:
                child_err = 'Critical failure occurred and ExitOnFailure option is in use'
        for test in self.tests:
            test.run(output, self.namespace, child_err)
            if self._exit_on_failure and not child_err and \
                    test.status == 'FAIL' and test.critical == 'yes':
                child_err = 'Critical failure occurred and ExitOnFailure option is in use'
            self._set_prev_test_variables(self.namespace.variables, test)
        self.set_status()
        self.message = self._get_my_error(error, init_err, setup_err)
        self.namespace.variables['${SUITE_STATUS}'] = self.status
        self.namespace.variables['${SUITE_MESSAGE}'] = self.get_full_message()
        teardown_err = self._run_fixture(self.teardown, output, self.namespace, 
                                         error, init_err)
        if teardown_err is not None:
            err_msg = 'Suite teardown failed:\n%s' % teardown_err
            self.suite_teardown_failed(err_msg)
        self.endtime = utils.get_timestamp()
        self.elapsedmillis = utils.get_elapsed_millis(self.starttime, self.endtime)
        self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)
        self._set_prev_test_variables(GLOBAL_VARIABLES, varz=self.namespace.variables)
        output.end_suite(self)
        self.namespace.end_suite()
        
    def _init_suite(self, varz):
        errs = []
        self.doc = varz.replace_from_meta('Documentation', self.doc, errs)
        self.setup = Setup(varz.replace_from_meta('Setup', self.setup, errs))
        self.teardown = Teardown(varz.replace_from_meta('Teardown', self.teardown, errs))
        for name, value in self.metadata.items():
            self.metadata[name] = varz.replace_from_meta(name, value, errs)
        if errs:
            return '\n'.join(errs)
        return None
        
    def _get_child_error(self, error, init_error, setup_error):
        if error is not None:
            return error
        if init_error is not None:
            return 'Initialization of the parent suite failed.'
        if setup_error is not None:
            return 'Setup of the parent suite failed.'
        return None

    def _get_my_error(self, error, init_error, setup_error):
        if error is not None:
            return error
        if init_error is not None:
            return 'Suite initialization failed:\n%s' % init_error
        if setup_error is not None:
            return 'Suite setup failed:\n%s' % setup_error
        return ''

    def _run_fixture(self, fixture, output, namespace, error, init_error):   
        if fixture is None or error is not None or init_error is not None:
            return None
        try:
            fixture.run(output, namespace)
        except ExecutionFailed:
            return utils.get_error_message()
    
    def _set_prev_test_variables(self, destination, test=None, varz=None):
        if test is not None:
            name, status, message = test.name, test.status, test.message
        else:
            name, status, message = varz['${PREV_TEST_NAME}'], \
                    varz['${PREV_TEST_STATUS}'], varz['${PREV_TEST_MESSAGE}']
        destination['${PREV_TEST_NAME}'] = name
        destination['${PREV_TEST_STATUS}'] = status
        destination['${PREV_TEST_MESSAGE}'] = message
    

class RunnableTestCase(BaseTestCase):
    
    def __init__(self, data, defaults, parent):
        BaseTestCase.__init__(self, data.name, parent)
        self.doc = data.doc or ''
        self.setup = utils.get_not_none(data.setup, defaults.test_setup)
        self.teardown = utils.get_not_none(data.teardown,
                                           defaults.test_teardown)
        self.tags = defaults.force_tags \
                    + utils.get_not_none(data.tags, defaults.default_tags)
        self.timeout = utils.get_not_none(data.timeout, defaults.test_timeout)
        self.keywords = [ KeywordFactory(kw) for kw in data.keywords ]
        
    def run(self, output, namespace, error=None):
        self.starttime = utils.get_timestamp()
        init_err = self._init_test(namespace.variables)
        if error is None:
            error = init_err
        if error is None and len(self.keywords) == 0:
            error = 'Test case contains no keywords'
        namespace.start_test(self)
        output.start_test(self)
        if error is None:
            self._run(output, namespace)
        else:
            self.status = 'FAIL'
            self.message = error
        self.endtime = utils.get_timestamp()
        self.elapsedmillis = utils.get_elapsed_millis(self.starttime, self.endtime)
        self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)
        output.end_test(self)
        namespace.end_test()

    def _init_test(self, varz):
        errs = []
        self.doc = varz.replace_from_meta('Documentation', self.doc, errs)
        self.setup = Setup(varz.replace_from_meta('Setup', self.setup, errs))
        self.teardown = Teardown(varz.replace_from_meta('Teardown', self.teardown, errs))
        self.tags = utils.normalize_list(varz.replace_from_meta('Tags', self.tags, errs))
        self.timeout = TestTimeout(*varz.replace_from_meta('Timeout', self.timeout, errs))
        if errs:
            return 'Test case initialization failed:\n%s' % '\n'.join(errs)
        return None
        
    def _run(self, output, namespace):
        namespace.variables['${TEST_NAME}'] = self.name
        namespace.variables['@{TEST_TAGS}'] = self.tags
        self.status = 'RUNNING'
        self.timeout.start()
        setup_err = self._run_fixture(self.setup, output, namespace)
        kw_err = self._run_keywords(output, namespace, setup_err)
        self.message = self._get_message(setup_err, kw_err)
        self.status = self.message == '' and 'PASS' or 'FAIL'
        namespace.variables['${TEST_STATUS}'] = self.status
        namespace.variables['${TEST_MESSAGE}'] = self.message
        teardown_err = self._run_fixture(self.teardown, output, namespace)
        if teardown_err is not None:
            self.message = self._get_message_with_teardown_err(self.message, 
                                                               teardown_err)
            self.status = 'FAIL' 
        if self.status == 'PASS' and self.timeout.timed_out():
            self.status = 'FAIL' 
            self.message = self.timeout.get_message()

    def _run_fixture(self, fixture, output, namespace):
        if fixture is None:
            return None
        try:
            fixture.run(output, namespace)
        except ExecutionFailed:
            return utils.get_error_message()

    def _run_keywords(self, output, namespace, setup_err):
        if setup_err is None:
            for kw in self.keywords:
                try:
                    kw.run(output, namespace)
                except ExecutionFailed:
                    return utils.get_error_message()
        return None

    def _get_message(self, setup_err, kw_err):
        if setup_err is None and kw_err is None:
            return ''
        if setup_err is not None:
            return 'Setup failed:\n%s' % setup_err
        return kw_err
    
    def _get_message_with_teardown_err(self, message, teardown_err):
        if message == '':
            return 'Teardown failed:\n%s' % teardown_err
        return '%s\n\nAlso teardown failed:\n%s' % (message, teardown_err)
            

class _TestCaseDefaults:

    def __init__(self):
        self.force_tags = []
        self.default_tags = []
        self.test_setup = []
        self.test_teardown = []
        self.test_timeout = []

    def add_defaults(self, suite):
        if suite.force_tags:
            self.force_tags.extend(suite.force_tags)
        if suite.default_tags:
            self.default_tags = suite.default_tags
        if suite.test_setup:
            self.test_setup = suite.test_setup
        if suite.test_teardown:
            self.test_teardown = suite.test_teardown
        if suite.test_timeout:
            self.test_timeout = suite.test_timeout

    def copy(self):
        copy = _TestCaseDefaults()
        copy.force_tags = self.force_tags[:]
        copy.default_tags = self.default_tags[:]
        copy.test_setup = self.test_setup[:]
        copy.test_teardown = self.test_teardown[:]
        copy.test_timeout = self.test_timeout[:]
        return copy
