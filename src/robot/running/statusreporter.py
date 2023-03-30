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
                          HandlerExecutionFailed)
from robot.utils import ErrorDetails, get_timestamp

from .modelcombiner import ModelCombiner


class StatusReporter:

    def __init__(self, data, result, context, run=True, suppress=False):
        self.data = data
        self.result = result
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
        if not result.starttime:
            result.starttime = get_timestamp()
        context.start_keyword(ModelCombiner(self.data, result))
        self._warn_if_deprecated(result.doc, result.name)
        return self

    def _warn_if_deprecated(self, doc, name):
        if doc.startswith('*DEPRECATED') and '*' in doc[1:]:
            message = ' ' + doc.split('*', 2)[-1].strip()
            self.context.warn("Keyword '%s' is deprecated.%s" % (name, message))

    def __exit__(self, exc_type, exc_val, exc_tb):
        context = self.context
        result = self.result
        failure = self._get_failure(exc_type, exc_val, exc_tb, context)
        if failure is None:
            result.status = self.pass_status
        else:
            result.status = failure.status
            if result.type == result.TEARDOWN:
                result.message = failure.message
        if self.initial_test_status == 'PASS':
            context.test.status = result.status
        result.endtime = get_timestamp()
        context.end_keyword(ModelCombiner(self.data, result))
        if failure is not exc_val and not self.suppress:
            raise failure
        return self.suppress

    def _get_failure(self, exc_type, exc_value, exc_tb, context):
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
