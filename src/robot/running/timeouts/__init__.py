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

import time

from robot.utils import Sortable, secs_to_timestr, timestr_to_secs, WINDOWS
from robot.errors import TimeoutError, DataError, FrameworkError

if WINDOWS:
    from .windows import Timeout
else:
    try:
        from .posix import Timeout
    except ImportError:
        from .nosupport import Timeout


class _Timeout(Sortable):
    type: str

    def __init__(self, timeout=None, variables=None):
        self.string = timeout or ''
        self.secs = -1
        self.starttime = -1
        self.error = None
        if variables:
            self.replace_variables(variables)

    @property
    def active(self):
        return self.starttime > 0

    def replace_variables(self, variables):
        try:
            self.string = variables.replace_string(self.string)
            if not self:
                return
            self.secs = timestr_to_secs(self.string)
            self.string = secs_to_timestr(self.secs)
        except (DataError, ValueError) as err:
            self.secs = 0.000001  # to make timeout active
            self.error = ('Setting %s timeout failed: %s' % (self.type.lower(), err))

    def start(self):
        if self.secs > 0:
            self.starttime = time.time()

    def time_left(self):
        if not self.active:
            return -1
        elapsed = time.time() - self.starttime
        # Timeout granularity is 1ms. Without rounding some timeout tests fail
        # intermittently on Windows, probably due to threading.Event.wait().
        return round(self.secs - elapsed, 3)

    def timed_out(self):
        return self.active and self.time_left() <= 0

    def run(self, runnable, args=None, kwargs=None):
        if self.error:
            raise DataError(self.error)
        if not self.active:
            raise FrameworkError('Timeout is not active')
        timeout = self.time_left()
        error = TimeoutError(self._timeout_error,
                             test_timeout=isinstance(self, TestTimeout))
        if timeout <= 0:
            raise error
        executable = lambda: runnable(*(args or ()), **(kwargs or {}))
        return Timeout(timeout, error).execute(executable)

    def get_message(self):
        if not self.active:
            return '%s timeout not active.' % self.type
        if not self.timed_out():
            return '%s timeout %s active. %s seconds left.' \
                % (self.type, self.string, self.time_left())
        return self._timeout_error

    @property
    def _timeout_error(self):
        return '%s timeout %s exceeded.' % (self.type, self.string)

    def __str__(self):
        return self.string

    def __bool__(self):
        return bool(self.string and self.string.upper() != 'NONE')

    @property
    def _sort_key(self):
        return not self.active, self.time_left()

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)


class TestTimeout(_Timeout):
    type = 'Test'
    _keyword_timeout_occurred = False

    def __init__(self, timeout=None, variables=None, rpa=False):
        if rpa:
            self.type = 'Task'
        super().__init__(timeout, variables)

    def set_keyword_timeout(self, timeout_occurred):
        if timeout_occurred:
            self._keyword_timeout_occurred = True

    def any_timeout_occurred(self):
        return self.timed_out() or self._keyword_timeout_occurred


class KeywordTimeout(_Timeout):
    type = 'Keyword'
