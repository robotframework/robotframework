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

from robot.errors import (BreakLoop, ContinueLoop, DataError, ExecutionFailed,
                          ExecutionStatus, HandlerExecutionFailed, ReturnFromKeyword)
from robot.utils import ErrorDetails


class StatusReporter:

    def __init__(self, data, result, context, run=True, suppress=False,
                 implementation=None):
        self.data = data
        self.result = result
        self.implementation = implementation
        self.context = context
        if run:
            self.pass_status = result.PASS
            result.status = result.NOT_SET
        else:
            self.pass_status = result.status = result.NOT_RUN
        self.suppress = suppress
        self.initial_test_status = None

    def __enter__(self):
        context = self.context
        result = self.result
        self.initial_test_status = context.test.status if context.test else None
        if not result.start_time:
            result.start_time = datetime.now()
        context.start_body_item(self.data, result, self.implementation)
        if result.type in result.KEYWORD_TYPES:
            self._warn_if_deprecated(result.doc, result.full_name)
        return self

    def _warn_if_deprecated(self, doc, name):
        if doc.startswith('*DEPRECATED') and '*' in doc[1:]:
            message = ' ' + doc.split('*', 2)[-1].strip()
            self.context.warn(f"Keyword '{name}' is deprecated.{message}")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        context = self.context
        result = self.result
        failure = self._get_failure(exc_value, context)
        if failure is None:
            result.status = self.pass_status
        else:
            result.status = failure.status
            if not isinstance(failure, (BreakLoop, ContinueLoop, ReturnFromKeyword)):
                result.message = failure.message
        if self.initial_test_status == 'PASS':
            context.test.status = result.status
        result.elapsed_time = datetime.now() - result.start_time
        orig_status = (result.status, result.message)
        context.end_body_item(self.data, result, self.implementation)
        if orig_status != (result.status, result.message):
            if result.passed or result.not_run:
                return True
            raise ExecutionFailed(result.message, skip=result.skipped)
        if failure is not exc_value and not self.suppress:
            raise failure
        return self.suppress

    def _get_failure(self, exc_value, context):
        if exc_value is None:
            return None
        if isinstance(exc_value, ExecutionStatus):
            return exc_value
        if isinstance(exc_value, DataError):
            msg = exc_value.message
            context.fail(msg)
            return ExecutionFailed(msg, syntax=exc_value.syntax)
        error = ErrorDetails(exc_value)
        failure = HandlerExecutionFailed(error)
        if failure.timeout:
            context.timeout_occurred = True
        if failure.skip:
            context.skip(error.message)
        else:
            context.fail(error.message)
        if error.traceback:
            context.debug(error.traceback)
        return failure
