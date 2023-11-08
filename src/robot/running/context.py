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

import inspect
import asyncio
from contextlib import contextmanager

from robot.errors import DataError


class Asynchronous:

    def __init__(self):
        self._loop_ref = None

    @property
    def event_loop(self):
        if self._loop_ref is None:
            self._loop_ref = asyncio.new_event_loop()
        return self._loop_ref

    def close_loop(self):
        if self._loop_ref:
            self._loop_ref.close()

    def run_until_complete(self, coroutine):
        return self.event_loop.run_until_complete(coroutine)

    def is_loop_required(self, obj):
        return inspect.iscoroutine(obj) and not self._is_loop_running()

    def _is_loop_running(self):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return False
        else:
            return True


class ExecutionContexts:

    def __init__(self):
        self._contexts = []
        self._asynchronous = Asynchronous()

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

    def start_suite(self, suite, namespace, output, dry_run=False):
        ctx = _ExecutionContext(suite, namespace, output, dry_run, self._asynchronous)
        self._contexts.append(ctx)
        return ctx

    def end_suite(self):
        self._contexts.pop()
        if not self._contexts:
            self._asynchronous.close_loop()


# This is ugly but currently needed e.g. by BuiltIn
EXECUTION_CONTEXTS = ExecutionContexts()


class _ExecutionContext:
    _started_keywords_threshold = 100

    def __init__(self, suite, namespace, output, dry_run=False, asynchronous=None):
        self.suite = suite
        self.test = None
        self.timeouts = set()
        self.namespace = namespace
        self.output = output
        self.dry_run = dry_run
        self.in_suite_teardown = False
        self.in_test_teardown = False
        self.in_keyword_teardown = 0
        self.timeout_occurred = False
        self.steps = []
        self.user_keywords = []
        self.asynchronous = asynchronous

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
        self._remove_timeout(test.timeout)
        try:
            yield
        finally:
            self.in_test_teardown = False

    @contextmanager
    def keyword_teardown(self, error):
        self.variables.set_keyword('${KEYWORD_STATUS}', 'FAIL' if error else 'PASS')
        self.variables.set_keyword('${KEYWORD_MESSAGE}', str(error or ''))
        self.in_keyword_teardown += 1
        try:
            yield
        finally:
            self.in_keyword_teardown -= 1

    @contextmanager
    def user_keyword(self, handler):
        self.user_keywords.append(handler)
        self.namespace.start_user_keyword()
        try:
            yield
        finally:
            self.namespace.end_user_keyword()
            self.user_keywords.pop()

    def warn_on_invalid_private_call(self, handler):
        parent = self.user_keywords[-1] if self.user_keywords else None
        if not parent or parent.source != handler.source:
            self.warn(f"Keyword '{handler.full_name}' is private and should only "
                      f"be called by keywords in the same file.")

    @contextmanager
    def timeout(self, timeout):
        self._add_timeout(timeout)
        try:
            yield
        finally:
            self._remove_timeout(timeout)

    @property
    def in_teardown(self):
        return bool(self.in_suite_teardown or
                    self.in_test_teardown or
                    self.in_keyword_teardown)

    @property
    def variables(self):
        return self.namespace.variables

    def continue_on_failure(self, default=False):
        parents = ([self.test] if self.test else []) + self.user_keywords
        for index, parent in enumerate(reversed(parents)):
            if (parent.tags.robot('recursive-stop-on-failure')
                    or index == 0 and parent.tags.robot('stop-on-failure')):
                return False
            if (parent.tags.robot('recursive-continue-on-failure')
                    or index == 0 and parent.tags.robot('continue-on-failure')):
                return True
        return default or self.in_teardown

    @property
    def allow_loop_control(self):
        for _, step in reversed(self.steps):
            if step.type == 'ITERATION':
                return True
            if step.type == 'KEYWORD' and step.owner != 'BuiltIn':
                return False
        return False

    def end_suite(self, data, result):
        for name in ['${PREV_TEST_NAME}',
                     '${PREV_TEST_STATUS}',
                     '${PREV_TEST_MESSAGE}']:
            self.variables.set_global(name, self.variables[name])
        self.output.end_suite(data, result)
        self.namespace.end_suite(data)
        EXECUTION_CONTEXTS.end_suite()

    def set_suite_variables(self, suite):
        self.variables['${SUITE_NAME}'] = suite.full_name
        self.variables['${SUITE_SOURCE}'] = str(suite.source or '')
        self.variables['${SUITE_DOCUMENTATION}'] = suite.doc
        self.variables['${SUITE_METADATA}'] = suite.metadata.copy()

    def report_suite_status(self, status, message):
        self.variables['${SUITE_STATUS}'] = status
        self.variables['${SUITE_MESSAGE}'] = message

    def start_test(self, data, result):
        self.test = result
        self._add_timeout(result.timeout)
        self.namespace.start_test()
        self.variables.set_test('${TEST_NAME}', result.name)
        self.variables.set_test('${TEST_DOCUMENTATION}', result.doc)
        self.variables.set_test('@{TEST_TAGS}', list(result.tags))
        self.output.start_test(data, result)

    def _add_timeout(self, timeout):
        if timeout:
            timeout.start()
            self.timeouts.add(timeout)

    def _remove_timeout(self, timeout):
        if timeout in self.timeouts:
            self.timeouts.remove(timeout)

    def end_test(self, test):
        self.test = None
        self._remove_timeout(test.timeout)
        self.namespace.end_test()
        self.variables.set_suite('${PREV_TEST_NAME}', test.name)
        self.variables.set_suite('${PREV_TEST_STATUS}', test.status)
        self.variables.set_suite('${PREV_TEST_MESSAGE}', test.message)
        self.timeout_occurred = False

    def start_body_item(self, data, result):
        self.steps.append((data, result))
        if len(self.steps) > self._started_keywords_threshold:
            raise DataError('Maximum limit of started keywords and control '
                            'structures exceeded.')
        output = self.output
        if result.type in (result.ELSE, result.ITERATION):
            method = {
                result.IF_ELSE_ROOT: output.start_if_branch,
                result.TRY_EXCEPT_ROOT: output.start_try_branch,
                result.FOR: output.start_for_iteration,
                result.WHILE: output.start_while_iteration,
            }[result.parent.type]
        else:
            method = {
                result.KEYWORD: output.start_keyword,
                result.SETUP: output.start_keyword,
                result.TEARDOWN: output.start_keyword,
                result.FOR: output.start_for,
                result.WHILE: output.start_while,
                result.IF_ELSE_ROOT: output.start_if,
                result.IF: output.start_if_branch,
                result.ELSE: output.start_if_branch,
                result.ELSE_IF: output.start_if_branch,
                result.TRY_EXCEPT_ROOT: output.start_try,
                result.TRY: output.start_try_branch,
                result.EXCEPT: output.start_try_branch,
                result.FINALLY: output.start_try_branch,
                result.VAR: output.start_var,
                result.BREAK: output.start_break,
                result.CONTINUE: output.start_continue,
                result.RETURN: output.start_return,
                result.ERROR: output.start_error,
            }[result.type]
        method(data, result)

    def end_body_item(self, data, result):
        output = self.output
        if result.type in (result.ELSE, result.ITERATION):
            method = {
                result.IF_ELSE_ROOT: output.end_if_branch,
                result.TRY_EXCEPT_ROOT: output.end_try_branch,
                result.FOR: output.end_for_iteration,
                result.WHILE: output.end_while_iteration,
            }[result.parent.type]
        else:
            method = {
                result.KEYWORD: output.end_keyword,
                result.SETUP: output.end_keyword,
                result.TEARDOWN: output.end_keyword,
                result.FOR: output.end_for,
                result.WHILE: output.end_while,
                result.IF_ELSE_ROOT: output.end_if,
                result.IF: output.end_if_branch,
                result.ELSE: output.end_if_branch,
                result.ELSE_IF: output.end_if_branch,
                result.TRY_EXCEPT_ROOT: output.end_try,
                result.TRY: output.end_try_branch,
                result.EXCEPT: output.end_try_branch,
                result.FINALLY: output.end_try_branch,
                result.VAR: output.end_var,
                result.BREAK: output.end_break,
                result.CONTINUE: output.end_continue,
                result.RETURN: output.end_return,
                result.ERROR: output.end_error,
            }[result.type]
        method(data, result)
        self.steps.pop()

    def get_runner(self, name, recommend_on_failure=True):
        return self.namespace.get_runner(name, recommend_on_failure)

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

    def skip(self, message):
        self.output.skip(message)
