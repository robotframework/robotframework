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

from signal import ITIMER_REAL, setitimer, SIG_DFL, SIGALRM, signal

from robot.errors import DataError, TimeoutExceeded

from .runner import Runner


class PosixRunner(Runner):
    _started = 0

    def __init__(
        self,
        timeout: float,
        timeout_error: TimeoutExceeded,
        data_error: "DataError|None" = None,
    ):
        super().__init__(timeout, timeout_error, data_error)
        self._orig_alrm = None

    def _run(self, runnable):
        self._start_timer()
        try:
            return runnable()
        finally:
            self._stop_timer()

    def _start_timer(self):
        if not self._started:
            self._orig_alrm = signal(SIGALRM, self._raise_timeout)
            setitimer(ITIMER_REAL, self.timeout)
        type(self)._started += 1

    def _raise_timeout(self, signum, frame):
        self.exceeded = True
        if not self.paused:
            raise self.timeout_error

    def _stop_timer(self):
        type(self)._started -= 1
        if not self._started:
            setitimer(ITIMER_REAL, 0)
            signal(SIGALRM, self._orig_alrm or SIG_DFL)
