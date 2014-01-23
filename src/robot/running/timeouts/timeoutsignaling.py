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

from signal import setitimer, signal, SIGALRM, ITIMER_REAL

from robot.errors import TimeoutError


class Timeout(object):

    def __init__(self, timeout, error):
        self._timeout = timeout
        self._error = error

    def execute(self, runnable):
        self._start_timer()
        try:
            return runnable()
        finally:
            self._stop_timer()

    def _start_timer(self):
        signal(SIGALRM, self._raise_timeout_error)
        setitimer(ITIMER_REAL, self._timeout)

    def _raise_timeout_error(self, signum, frame):
        raise TimeoutError(self._error)

    def _stop_timer(self):
        setitimer(ITIMER_REAL, 0)
