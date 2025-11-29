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

import asyncio
import inspect
import sys
from contextlib import contextmanager

from robot.errors import DataError, ExecutionFailed


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
            self._loop_ref = None

    def run_until_complete(self, coroutine):
        task = self.event_loop.create_task(coroutine)
        try:
            return self.event_loop.run_until_complete(task)
        except ExecutionFailed as err:
            if err.dont_continue:
                task.cancel()
                # Wait for task and its children to cancel.
                self.event_loop.run_until_complete(
                    asyncio.gather(task, return_exceptions=True)
                )
            raise err

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

    def __init__(self, suite, namespace, output, dry_run=False, asynchronous=None):
        self.suite = suite
        self.test = None
        self.timeouts = []
        self.active_timeouts = []
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

    @property
    def languages(self):
        return self.namespace.languages

    @contextmanager
    def suite_teardown(self):
        self.in_suite_teardown = True
        try:
            yield
        finally:
            self.in_suite_teardown = False

    @contextmanager
    def test_teardown(self, test):
        self.variables.set_test("${TEST_STATUS}", test.status)
        self.variables.set_test("${TEST_MESSAGE}", test.message)
        self.in_test_teardown = True
        self.timeouts = []  # Clear current timeouts.
        try:
            yield
        finally:
            self.in_test_teardown = False

    @contextmanager
    def keyword_teardown(self, error):
        self.variables.set_keyword("${KEYWORD_STATUS}", "FAIL" if error else "PASS")
        self.variables.set_keyword("${KEYWORD_MESSAGE}", str(error or ""))
        self.in_keyword_teardown += 1
        self.timeouts, timeouts = [], self.timeouts  # Disable current timeouts.
        try:
            yield
        finally:
            self.in_keyword_teardown -= 1
            self.timeouts = timeouts

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
            self.warn(
                f"Keyword '{handler.full_name}' is private and should only "
                f"be called by keywords in the same file."
            )

    @contextmanager
    def keyword_timeout(self, timeout):
        self._add_timeout(timeout)
        try:
            yield
        finally:
            self._remove_timeout(timeout)

    @contextmanager
    def timeout(self, timeout):
        runner = timeout.get_runner()
        self.active_timeouts.append(runner)
        with self.output.delayed_logging:
            self.output.debug(timeout.get_message)
            try:
                yield runner
            finally:
                self.active_timeouts.pop()

    @property
    @contextmanager
    def paused_timeouts(self):
        if not self.active_timeouts:
            yield
            return
        for runner in self.active_timeouts:
            runner.pause()
        with self.output.delayed_logging_paused:
            try:
                yield
            finally:
                for runner in self.active_timeouts:
                    runner.resume()

    @property
    def in_teardown(self):
        return bool(
            self.in_suite_teardown or self.in_test_teardown or self.in_keyword_teardown
        )

    @property
    def variables(self):
        return self.namespace.variables

    def continue_on_failure(self, default=False):
        parents = [
            result
            for _, result, implementation in reversed(self.steps)
            if implementation and implementation.type == "USER KEYWORD"
        ]
        if self.test:
            parents.append(self.test)
        for index, parent in enumerate(parents):
            robot = parent.tags.robot
            if index == 0 and robot("stop-on-failure"):
                return False
            if index == 0 and robot("continue-on-failure"):
                return True
            if robot("recursive-stop-on-failure"):
                return False
            if robot("recursive-continue-on-failure"):
                return True
        return default or self.in_teardown

    @property
    def allow_loop_control(self):
        for _, result, _ in reversed(self.steps):
            if result.type == "ITERATION":
                return True
            if result.type == "KEYWORD" and result.owner != "BuiltIn":
                return False
        return False

    def end_suite(self, data, result):
        for name in [
            "${PREV_TEST_NAME}",
            "${PREV_TEST_STATUS}",
            "${PREV_TEST_MESSAGE}",
        ]:
            self.variables.set_global(name, self.variables[name])
        self.output.end_suite(data, result)
        self.namespace.end_suite(data)
        EXECUTION_CONTEXTS.end_suite()

    def set_suite_variables(self, suite):
        self.variables["${SUITE_NAME}"] = suite.full_name
        self.variables["${SUITE_SOURCE}"] = str(suite.source or "")
        self.variables["${SUITE_DOCUMENTATION}"] = suite.doc
        self.variables["${SUITE_METADATA}"] = suite.metadata.copy()

    def report_suite_status(self, status, message):
        self.variables["${SUITE_STATUS}"] = status
        self.variables["${SUITE_MESSAGE}"] = message

    def start_test(self, data, result):
        self.test = result
        self._add_timeout(result.timeout)
        self.namespace.start_test()
        self.variables.set_test("${TEST_NAME}", result.name)
        self.variables.set_test("${TEST_DOCUMENTATION}", result.doc)
        self.variables.set_test("@{TEST_TAGS}", list(result.tags))
        self.output.start_test(data, result)

    def _add_timeout(self, timeout):
        if timeout:
            timeout.start()
            self.timeouts.append(timeout)

    def _remove_timeout(self, timeout):
        if timeout in self.timeouts:
            self.timeouts.remove(timeout)

    def end_test(self, test):
        self.test = None
        self.timeouts = []
        self.namespace.end_test()
        self.variables.set_suite("${PREV_TEST_NAME}", test.name)
        self.variables.set_suite("${PREV_TEST_STATUS}", test.status)
        self.variables.set_suite("${PREV_TEST_MESSAGE}", test.message)
        self.timeout_occurred = False

    def start_body_item(self, data, result, implementation=None):
        self._prevent_execution_close_to_recursion_limit()
        self.steps.append((data, result, implementation))
        output = self.output
        args = (data, result)
        if implementation:
            if implementation.error:
                method = output.start_invalid_keyword
            elif implementation.type == implementation.LIBRARY_KEYWORD:
                method = output.start_library_keyword
            else:
                method = output.start_user_keyword
            args = (data, implementation, result)
        elif result.type in (result.ELSE, result.ITERATION):
            method = {
                result.IF_ELSE_ROOT: output.start_if_branch,
                result.TRY_EXCEPT_ROOT: output.start_try_branch,
                result.FOR: output.start_for_iteration,
                result.WHILE: output.start_while_iteration,
            }[result.parent.type]
        else:
            method = {
                result.FOR: output.start_for,
                result.WHILE: output.start_while,
                result.GROUP: output.start_group,
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
        method(*args)

    def _prevent_execution_close_to_recursion_limit(self):
        try:
            sys._getframe(sys.getrecursionlimit() - 100)
        except (ValueError, AttributeError):
            pass
        else:
            raise DataError("Recursive execution stopped.")

    def end_body_item(self, data, result, implementation=None):
        output = self.output
        args = (data, result)
        if implementation:
            if implementation.error:
                method = output.end_invalid_keyword
            elif implementation.type == implementation.LIBRARY_KEYWORD:
                method = output.end_library_keyword
            else:
                method = output.end_user_keyword
            args = (data, implementation, result)
        elif result.type in (result.ELSE, result.ITERATION):
            method = {
                result.IF_ELSE_ROOT: output.end_if_branch,
                result.TRY_EXCEPT_ROOT: output.end_try_branch,
                result.FOR: output.end_for_iteration,
                result.WHILE: output.end_while_iteration,
            }[result.parent.type]
        else:
            method = {
                result.FOR: output.end_for,
                result.WHILE: output.end_while,
                result.GROUP: output.end_group,
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
        method(*args)
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
