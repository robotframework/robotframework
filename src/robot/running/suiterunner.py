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

from datetime import datetime

from robot.errors import ExecutionFailed, ExecutionStatus, DataError, PassExecution
from robot.model import SuiteVisitor, TagPatterns
from robot.result import (Keyword as KeywordResult, TestCase as TestResult,
                          TestSuite as SuiteResult, Result)
from robot.utils import (is_list_like, NormalizedDict, plural_or_not as s, seq2str,
                         test_or_task)
from robot.variables import VariableScopes

from .bodyrunner import BodyRunner, KeywordRunner
from .context import EXECUTION_CONTEXTS
from .model import Keyword as KeywordData, TestCase as TestData, TestSuite as SuiteData
from .namespace import Namespace
from .status import SuiteStatus, TestStatus
from .timeouts import TestTimeout


class SuiteRunner(SuiteVisitor):

    def __init__(self, output, settings):
        self.result = None
        self.output = output
        self.settings = settings
        self.variables = VariableScopes(settings)
        self.suite_result = None
        self.suite_status = None
        self.executed = [NormalizedDict(ignore='_')]
        self.skipped_tags = TagPatterns(settings.skip)

    @property
    def context(self):
        return EXECUTION_CONTEXTS.current

    def start_suite(self, data: SuiteData):
        if data.name in self.executed[-1] and data.parent.source:
            self.output.warn(f"Multiple suites with name '{data.name}' executed in "
                              f"suite '{data.parent.full_name}'.")
        self.executed[-1][data.name] = True
        self.executed.append(NormalizedDict(ignore='_'))
        self.output.library_listeners.new_suite_scope()
        result = SuiteResult(source=data.source,
                             name=data.name,
                             doc=data.doc,
                             metadata=data.metadata,
                             start_time=datetime.now(),
                             rpa=self.settings.rpa)
        if not self.result:
            self.result = Result(suite=result, rpa=self.settings.rpa)
            self.result.configure(status_rc=self.settings.status_rc,
                                  stat_config=self.settings.statistics_config)
        else:
            self.suite_result.suites.append(result)
        self.suite_result = result
        self.suite_status = SuiteStatus(self.suite_status,
                                        self.settings.exit_on_failure,
                                        self.settings.exit_on_error,
                                        self.settings.skip_teardown_on_exit)
        ns = Namespace(self.variables, result, data.resource, self.settings.languages)
        ns.start_suite()
        ns.variables.set_from_variable_section(data.resource.variables)
        EXECUTION_CONTEXTS.start_suite(result, ns, self.output,
                                       self.settings.dry_run)
        self.context.set_suite_variables(result)
        if not self.suite_status.failed:
            ns.handle_imports()
            ns.variables.resolve_delayed()
        result.doc = self._resolve_setting(result.doc)
        result.metadata = [(self._resolve_setting(n), self._resolve_setting(v))
                           for n, v in result.metadata.items()]
        self.context.set_suite_variables(result)
        self.output.start_suite(data, result)
        self.output.register_error_listener(self.suite_status.error_occurred)
        self._run_setup(data, self.suite_status, self.suite_result,
                        run=self._any_test_run(data))

    def _any_test_run(self, suite: SuiteData):
        skipped_tags = self.skipped_tags
        for test in suite.all_tests:
            tags = test.tags
            if not (skipped_tags.match(tags)
                    or tags.robot('skip')
                    or tags.robot('exclude')):
                return True
        return False

    def _resolve_setting(self, value):
        if is_list_like(value):
            return self.variables.replace_list(value, ignore_errors=True)
        return self.variables.replace_string(value, ignore_errors=True)

    def end_suite(self, suite: SuiteData):
        self.suite_result.message = self.suite_status.message
        self.context.report_suite_status(self.suite_result.status,
                                         self.suite_result.full_message)
        with self.context.suite_teardown():
            failure = self._run_teardown(suite, self.suite_status, self.suite_result)
            if failure:
                if failure.skip:
                    self.suite_result.suite_teardown_skipped(str(failure))
                else:
                    self.suite_result.suite_teardown_failed(str(failure))
        self.suite_result.end_time = datetime.now()
        self.suite_result.message = self.suite_status.message
        self.context.end_suite(suite, self.suite_result)
        self._clear_result(self.suite_result)
        self.executed.pop()
        self.suite_result = self.suite_result.parent
        self.suite_status = self.suite_status.parent
        self.output.library_listeners.discard_suite_scope()

    def visit_test(self, data: TestData):
        settings = self.settings
        result = self.suite_result.tests.create(self._resolve_setting(data.name),
                                                self._resolve_setting(data.doc),
                                                self._resolve_setting(data.tags),
                                                self._get_timeout(data),
                                                data.lineno,
                                                start_time=datetime.now())
        if result.tags.robot('exclude'):
            self.suite_result.tests.pop()
            return
        if result.name in self.executed[-1]:
            self.output.warn(
                test_or_task(f"Multiple {{test}}s with name '{result.name}' executed "
                             f"in suite '{result.parent.full_name}'.", settings.rpa))
        self.executed[-1][result.name] = True
        self.context.start_test(data, result)
        status = TestStatus(self.suite_status, result, settings.skip_on_failure,
                            settings.rpa)
        if status.exit:
            self._add_exit_combine()
            result.tags.add('robot:exit')
        if status.passed:
            if not data.error:
                if not data.name:
                    data.error = 'Test name cannot be empty.'
                elif not data.body:
                    data.error = 'Test cannot be empty.'
            if data.error:
                if settings.rpa:
                    data.error = data.error.replace('Test', 'Task')
                status.test_failed(data.error)
            elif result.tags.robot('skip'):
                status.test_skipped(
                    self._get_skipped_message(['robot:skip'], settings.rpa)
                )
            elif self.skipped_tags.match(result.tags):
                status.test_skipped(
                    self._get_skipped_message(self.skipped_tags, settings.rpa)
                )
        self._run_setup(data, status, result)
        if status.passed:
            runner = BodyRunner(self.context, templated=bool(data.template))
            try:
                runner.run(data, result)
            except PassExecution as exception:
                err = exception.earlier_failures
                if err:
                    status.test_failed(error=err)
                else:
                    result.message = exception.message
            except ExecutionStatus as err:
                status.test_failed(error=err)
        elif status.skipped:
            status.test_skipped(status.message)
        else:
            status.test_failed(status.message)
        result.status = status.status
        result.message = status.message or result.message
        with self.context.test_teardown(result):
            self._run_teardown(data, status, result)
        if status.passed and result.timeout and result.timeout.timed_out():
            status.test_failed(result.timeout.get_message())
            result.message = status.message
        if status.skip_on_failure_after_tag_changes:
            result.message = status.message or result.message
        result.status = status.status
        result.end_time = datetime.now()
        failed_before_listeners = result.failed
        # TODO: can this be removed to context
        self.output.end_test(data, result)
        if result.failed and not failed_before_listeners:
            status.failure_occurred()
        self.context.end_test(result)
        self._clear_result(result)

    def _get_skipped_message(self, tags, rpa):
        kind = 'tag' if getattr(tags, 'is_constant', True) else 'tag pattern'
        return test_or_task(f"{{Test}} skipped using {seq2str(tags)} {kind}{s(tags)}.",
                            rpa)

    def _clear_result(self, result: 'SuiteResult|TestResult'):
        if result.has_setup:
            result.setup = None
        if result.has_teardown:
            result.teardown = None
        if hasattr(result, 'body'):
            result.body.clear()

    def _add_exit_combine(self):
        exit_combine = ('NOT robot:exit', '')
        if exit_combine not in self.settings['TagStatCombine']:
            self.settings['TagStatCombine'].append(exit_combine)

    def _get_timeout(self, test: TestData):
        if not test.timeout:
            return None
        return TestTimeout(test.timeout, self.variables, rpa=test.parent.rpa)

    def _run_setup(self, item: 'SuiteData|TestData',
                   status: 'SuiteStatus|TestStatus',
                   result: 'SuiteResult|TestResult',
                   run: bool = True):
        if run and status.passed:
            if item.has_setup:
                exception = self._run_setup_or_teardown(item.setup, result.setup)
            else:
                exception = None
            status.setup_executed(exception)
            if isinstance(exception, PassExecution) and isinstance(result, TestResult):
                result.message = exception.message
        elif status.parent and status.parent.skipped:
            status.skipped = True

    def _run_teardown(self, item: 'SuiteData|TestData',
                      status: 'SuiteStatus|TestStatus',
                      result: 'SuiteResult|TestResult'):
        if status.teardown_allowed:
            if item.has_teardown:
                exception = self._run_setup_or_teardown(item.teardown, result.teardown)
            else:
                exception = None
            status.teardown_executed(exception)
            failed = exception and not isinstance(exception, PassExecution)
            if isinstance(result, TestResult) and exception:
                if failed or status.skipped or exception.skip:
                    result.message = status.message
                else:
                    # Pass execution used in teardown,
                    # and it overrides previous failure message
                    result.message = exception.message
            return exception if failed else None

    def _run_setup_or_teardown(self, data: KeywordData, result: KeywordResult):
        try:
            name = self.variables.replace_string(data.name)
        except DataError as err:
            if self.settings.dry_run:
                return None
            return ExecutionFailed(message=err.message)
        if name.upper() in ('', 'NONE'):
            return None
        try:
            KeywordRunner(self.context).run(data, result, name=name)
        except ExecutionStatus as err:
            return err
