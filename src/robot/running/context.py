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

from robot.variables import GLOBAL_VARIABLES


class ExecutionContext(object):

    def __init__(self, namespace, output, dry_run=False):
        self.namespace = namespace
        self.output = output
        self.dry_run = dry_run

    @property
    def teardown(self):
        test_or_suite = self.namespace.test or self.namespace.suite
        return test_or_suite.status != 'RUNNING'

    def get_current_vars(self):
        return self.namespace.variables

    def end_test(self, test):
        self.output.end_test(test)
        self.namespace.end_test()

    def end_suite(self, suite):
        self.output.end_suite(suite)
        self.namespace.end_suite()

    def output_file_changed(self, filename):
        self._set_global_variable('${OUTPUT_FILE}', filename)

    def replace_vars_from_setting(self, name, value, errors):
        return self.namespace.variables.replace_meta(name, value, errors)

    def log_file_changed(self, filename):
        self._set_global_variable('${LOG_FILE}', filename)

    def set_prev_test_variables(self, test):
        self._set_prev_test_variables(self.get_current_vars(), test.name,
                                      test.status, test.message)

    def copy_prev_test_vars_to_global(self):
        varz = self.get_current_vars()
        name, status, message = varz['${PREV_TEST_NAME}'], \
                    varz['${PREV_TEST_STATUS}'], varz['${PREV_TEST_MESSAGE}']
        self._set_prev_test_variables(GLOBAL_VARIABLES, name, status, message)

    def _set_prev_test_variables(self, destination, name, status, message):
        destination['${PREV_TEST_NAME}'] = name
        destination['${PREV_TEST_STATUS}'] = status
        destination['${PREV_TEST_MESSAGE}'] = message

    def _set_global_variable(self, name, value):
        self.namespace.variables.set_global(name, value)

    def report_suite_status(self, status, message):
        self.get_current_vars()['${SUITE_STATUS}'] = status
        self.get_current_vars()['${SUITE_MESSAGE}'] = message

    def start_test(self, test):
        self.namespace.start_test(test)
        self.output.start_test(test)

    def set_test_status_before_teardown(self, message, status):
        self.namespace.set_test_status_before_teardown(message, status)

    def get_handler(self, name):
        return self.namespace.get_handler(name)

    def start_keyword(self, keyword):
        self.output.start_keyword(keyword)

    def end_keyword(self, keyword):
        self.output.end_keyword(keyword)

    def warn(self, message):
        self.output.warn(message)

    def trace(self, message):
        self.output.trace(message)
