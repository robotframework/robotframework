#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

import signal
import sys

from robot.errors import ExecutionFailed
from robot.output import LOGGER

class _StopSignalMonitor(object):

    def __init__(self):
        self._signal_count = 0
        self._running_keyword = False
        self._error_reported = False

    def __call__(self, signum, frame):
        self._signal_count += 1
        LOGGER.info('Received signal: %s.' % signum)
        if self._signal_count > 1:
            sys.__stderr__.write('Execution forcefully stopped.')
            raise SystemExit()
        sys.__stderr__.write('Second signal will force exit.')
        if self._running_keyword and not sys.platform.startswith('java'):
            self._stop_execution_gracefully()

    def _stop_execution_gracefully(self):
        if not self._error_reported:
            self._error_reported = True
            raise ExecutionFailed('Execution terminated by signal', exit=True)

    def start(self):
        signal.signal(signal.SIGINT, self)
        signal.signal(signal.SIGTERM, self)

    def start_running_keyword(self):
        self._running_keyword = True
        if self._signal_count:
            self._stop_execution_gracefully()

    def stop_running_keyword(self):
        self._running_keyword = False


STOP_SIGNAL_MONITOR = _StopSignalMonitor()