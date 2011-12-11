#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from signal import setitimer, signal, SIGALRM, ITIMER_REAL
from robot.errors import TimeoutError
from robot.running.timeouts.timeoutbase import _Timeout


class TimeoutWithSignaling(_Timeout):

    def _execute_with_timeout(self, timeout, runnable, args, kwargs):
        self._start_timer(timeout)
        try:
            return runnable(*(args or ()), **(kwargs or {}))
        finally:
            self._stop_timer()

    def _start_timer(self, timeout):
        signal(SIGALRM, self._raise_timeout_error)
        setitimer(ITIMER_REAL, timeout)

    def _raise_timeout_error(self, *args):
        raise TimeoutError(self._get_timeout_error())

    def _stop_timer(self):
        setitimer(ITIMER_REAL, 0)
