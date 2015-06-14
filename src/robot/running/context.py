#  Copyright 2008-2015 Nokia Solutions and Networks
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

from contextlib import contextmanager

from robot.errors import DataError


class ExecutionContexts(object):

    def __init__(self):
        self._contexts = []

    @property
    def current(self):
        return self._contexts[-1] if self._contexts else None

    @property
    def top(self):
        return self._contexts[0] if self._contexts else None

    def __iter__(self):
        return iter(self._contexts)

    @property
    def namespaces(self):
        return (context.namespace for context in self)

    def start_suite(self, namespace, output, dry_run=False):
        self._contexts.append(_ExecutionContext(namespace, output, dry_run))
        return self.current

    def end_suite(self):
        self._contexts.pop()


# This is ugly but currently needed e.g. by BuiltIn
EXECUTION_CONTEXTS = ExecutionContexts()


class _ExecutionContext(object):
    _started_keywords_threshold = 42  # Jython on Windows don't work with higher

    def __init__(self, namespace, output, dry_run=False):
        self.namespace = namespace
        self.output = output
        self.dry_run = dry_run
        self.in_suite_teardown = False
        self.in_test_teardown = False
        self.in_keyword_teardown = 0
        self._started_keywords = 0
        self.timeout_occurred = False
        self.failure_in_test_teardown = False

    # TODO: namespace should not have suite, test, or uk_handlers.

    @property
    def suite(self):
        return self.namespace.suite

    @property
    def test(self):
        return self.namespace.test

    @property
    def keywords(self):
        return self.namespace.uk_handlers

    @contextmanager
    def suite_teardown(self):
        self.in_suite_teardown = True
        try:
            yield
        finally:
            self.in_suite_teardown = False

    @contextmanager
    def test_teardown(self, test):
        self.variables.set_test('${TEST_STATUS}', test.status)
        self.variables.set_test('${TEST_MESSAGE}', test.message)
        self.in_test_teardown = True
        try:
            yield
        finally:
            self.in_test_teardown = False
            self.failure_in_test_teardown = False

    @contextmanager
    def keyword_teardown(self, error):
        self.variables.set_keyword('${KEYWORD_STATUS}', 'FAIL' if error else 'PASS')
        self.variables.set_keyword('${KEYWORD_MESSAGE}', unicode(error or ''))
        self.in_keyword_teardown += 1
        try:
            yield
        finally:
            self.in_keyword_teardown -= 1

    @contextmanager
    def user_keyword(self, kw):
        self.namespace.start_user_keyword(kw)
        try:
            yield
        finally:
            self.namespace.end_user_keyword()

    @property
    def in_teardown(self):
        return bool(self.in_suite_teardown or
                    self.in_test_teardown or
                    self.in_keyword_teardown)

    @property
    def variables(self):
        return self.namespace.variables

    # TODO: Move start_suite here from EXECUTION_CONTEXT

    def end_suite(self, suite):
        for name in ['${PREV_TEST_NAME}',
                     '${PREV_TEST_STATUS}',
                     '${PREV_TEST_MESSAGE}']:
            self.variables.set_global(name, self.variables[name])
        self.output.end_suite(suite)
        self.namespace.end_suite()
        EXECUTION_CONTEXTS.end_suite()

    def set_suite_variables(self, suite):
        self.variables['${SUITE_NAME}'] = suite.longname
        self.variables['${SUITE_SOURCE}'] = suite.source or ''
        self.variables['${SUITE_DOCUMENTATION}'] = suite.doc
        self.variables['${SUITE_METADATA}'] = suite.metadata.copy()

    def report_suite_status(self, status, message):
        self.variables['${SUITE_STATUS}'] = status
        self.variables['${SUITE_MESSAGE}'] = message

    def start_test(self, test):
        self.namespace.start_test(test)
        self.variables.set_test('${TEST_NAME}', test.name)
        self.variables.set_test('${TEST_DOCUMENTATION}', test.doc)
        self.variables.set_test('@{TEST_TAGS}', list(test.tags))

    def end_test(self, test):
        self.namespace.end_test()
        self.variables.set_suite('${PREV_TEST_NAME}', test.name)
        self.variables.set_suite('${PREV_TEST_STATUS}', test.status)
        self.variables.set_suite('${PREV_TEST_MESSAGE}', test.message)
        self.timeout_occurred = False

    # Should not need separate start/end_keyword and start/end_user_keyword

    def start_keyword(self, keyword):
        self._started_keywords += 1
        if self._started_keywords > self._started_keywords_threshold:
            raise DataError('Maximum limit of started keywords exceeded.')
        self.output.start_keyword(keyword)

    def end_keyword(self, keyword):
        self.output.end_keyword(keyword)
        self._started_keywords -= 1
        if self.in_test_teardown and not keyword.passed:
            self.failure_in_test_teardown = True

    def get_handler(self, name):
        return self.namespace.get_handler(name)

    def trace(self, message):
        self.output.trace(message)

    def debug(self, message):
        self.output.debug(message)

    def info(self, message):
        self.output.info(message)

    def warn(self, message):
        self.output.warn(message)

    def fail(self, message):
        self.output.fail(message)
