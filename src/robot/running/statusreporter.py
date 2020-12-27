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

from robot.errors import (ExecutionFailed, ExecutionStatus, DataError,
                          HandlerExecutionFailed, KeywordError, VariableError)
from robot.utils import ErrorDetails, get_timestamp


class StatusReporter(object):

    def __init__(self, context, result, dry_run_lib_kw=False):
        self._context = context
        self._result = result
        self._pass_status = 'PASS' if not dry_run_lib_kw else 'NOT_RUN'
        self._test_passed = None

    def __enter__(self):
        if self._context.test:
            self._test_passed = self._context.test.passed
        self._result.starttime = get_timestamp()
        self._context.start_keyword(self._result)
        self._warn_if_deprecated(self._result.doc, self._result.name)
        return self

    def _warn_if_deprecated(self, doc, name):
        if doc.startswith('*DEPRECATED') and '*' in doc[1:]:
            message = ' ' + doc.split('*', 2)[-1].strip()
            self._context.warn("Keyword '%s' is deprecated.%s" % (name, message))

    def __exit__(self, exc_type, exc_val, exc_tb):
        context = self._context
        result = self._result
        failure = self._get_failure(exc_type, exc_val, exc_tb, context)
        if failure is None:
            result.status = self._pass_status
        else:
            result.status = failure.status
            if result.type == result.TEARDOWN_TYPE:
                result.message = failure.message
        if context.test:
            status = self._get_status(result)
            context.test.status = status
        result.endtime = get_timestamp()
        context.end_keyword(result)
        if failure is not exc_val:
            raise failure

    def mark_as_not_run(self):
        self._pass_status = 'NOT_RUN'

    def _get_status(self, result):
        if result.status == 'SKIP':
            return 'SKIP'
        if self._test_passed and result.passed:
            return 'PASS'
        return 'FAIL'

    def _get_failure(self, exc_type, exc_value, exc_tb, context):
        if exc_value is None:
            return None
        if isinstance(exc_value, ExecutionStatus):
            return exc_value
        if isinstance(exc_value, DataError):
            msg = exc_value.message
            context.fail(msg)
            syntax = not isinstance(exc_value, (KeywordError, VariableError))
            return ExecutionFailed(msg, syntax=syntax)
        exc_info = (exc_type, exc_value, exc_tb)
        failure = HandlerExecutionFailed(ErrorDetails(exc_info))
        if failure.timeout:
            context.timeout_occurred = True
        if failure.skip:
            context.skip(failure.full_message)
        else:
            context.fail(failure.full_message)
        if failure.traceback:
            context.debug(failure.traceback)
        return failure
