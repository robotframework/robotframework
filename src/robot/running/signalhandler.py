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

import signal
import sys
from threading import current_thread, main_thread

from robot.errors import ExecutionFailed
from robot.output import LOGGER


class _StopSignalMonitor:

    def __init__(self):
        self._signal_count = 0
        self._running_keyword = False
        self._orig_sigint = None
        self._orig_sigterm = None

    def __call__(self, signum, frame):
        self._signal_count += 1
        LOGGER.info(f"Received signal: {signum}.")
        if self._signal_count > 1:
            self._write_to_stderr("Execution forcefully stopped.")
            raise SystemExit
        self._write_to_stderr("Second signal will force exit.")
        if self._running_keyword:
            self._stop_execution_gracefully()

    def _write_to_stderr(self, message):
        if sys.__stderr__:
            sys.__stderr__.write(message + "\n")

    def _stop_execution_gracefully(self):
        raise ExecutionFailed("Execution terminated by signal", exit=True)

    def __enter__(self):
        if self._can_register_signal:
            self._orig_sigint = signal.getsignal(signal.SIGINT)
            self._orig_sigterm = signal.getsignal(signal.SIGTERM)
            for signum in signal.SIGINT, signal.SIGTERM:
                self._register_signal_handler(signum)
        return self

    def __exit__(self, *exc_info):
        self._signal_count = 0
        if self._can_register_signal:
            signal.signal(signal.SIGINT, self._orig_sigint or signal.SIG_DFL)
            signal.signal(signal.SIGTERM, self._orig_sigterm or signal.SIG_DFL)

    @property
    def _can_register_signal(self):
        return signal and current_thread() is main_thread()

    def _register_signal_handler(self, signum):
        try:
            signal.signal(signum, self)
        except ValueError as err:
            if signum == signal.SIGINT:
                name = "INT"
                or_ctrlc = "or with Ctrl-C "
            else:
                name = "TERM"
                or_ctrlc = ""
            LOGGER.warn(
                f"Registering signal {name} failed. Stopping execution gracefully with "
                f"this signal {or_ctrlc}is not possible. Original error was: {err}"
            )

    def start_running_keyword(self, in_teardown):
        self._running_keyword = True
        if self._signal_count and not in_teardown:
            self._stop_execution_gracefully()

    def stop_running_keyword(self):
        self._running_keyword = False


STOP_SIGNAL_MONITOR = _StopSignalMonitor()
