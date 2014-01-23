#  Copyright 2008-2014 Nokia Solutions and Networks
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

import sys
import os
import time

from robot import utils
from robot.errors import TimeoutError, DataError, FrameworkError

if sys.platform == 'cli':
    from .timeoutthread import Timeout
elif os.name == 'nt':
    from .timeoutwin import Timeout
else:
    try:
        # python 2.6 or newer in *nix or mac
        from .timeoutsignaling import Timeout
    except ImportError:
        # python < 2.6 and jython don't have complete signal module
        from .timeoutthread import Timeout


class _Timeout(object):

    def __init__(self, timeout=None, message='', variables=None):
        self.string = timeout or ''
        self.message = message
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
            self.secs = utils.timestr_to_secs(self.string)
            self.string = utils.secs_to_timestr(self.secs)
            self.message = variables.replace_string(self.message)
        except (DataError, ValueError), err:
            self.secs = 0.000001 # to make timeout active
            self.error = 'Setting %s timeout failed: %s' \
                    % (self.type.lower(), unicode(err))

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

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.string

    def __cmp__(self, other):
        return cmp(not self.active, not other.active) \
            or cmp(self.time_left(), other.time_left())

    def __nonzero__(self):
        return bool(self.string and self.string.upper() != 'NONE')

    def run(self, runnable, args=None, kwargs=None):
        if self.error:
            raise DataError(self.error)
        if not self.active:
            raise FrameworkError('Timeout is not active')
        timeout = self.time_left()
        if timeout <= 0:
            raise TimeoutError(self.get_message())
        executable = lambda: runnable(*(args or ()), **(kwargs or {}))
        return Timeout(timeout, self._timeout_error).execute(executable)

    def get_message(self):
        if not self.active:
            return '%s timeout not active.' % self.type
        if not self.timed_out():
            return '%s timeout %s active. %s seconds left.' \
                % (self.type, self.string, self.time_left())
        return self._timeout_error

    @property
    def _timeout_error(self):
        if self.message:
            return self.message
        return '%s timeout %s exceeded.' % (self.type, self.string)


class TestTimeout(_Timeout):
    type = 'Test'
    _keyword_timeout_occurred = False

    def set_keyword_timeout(self, timeout_occurred):
        if timeout_occurred:
            self._keyword_timeout_occurred = True

    def any_timeout_occurred(self):
        return self.timed_out() or self._keyword_timeout_occurred


class KeywordTimeout(_Timeout):
    type = 'Keyword'
