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

import ctypes
import time
from threading import current_thread, Timer

from robot.errors import DataError, TimeoutExceeded

from .runner import Runner


class WindowsRunner(Runner):

    def __init__(
        self,
        timeout: float,
        timeout_error: TimeoutExceeded,
        data_error: "DataError|None" = None,
    ):
        super().__init__(timeout, timeout_error, data_error)
        self._runner_thread_id = current_thread().ident
        self._timeout_pending = False

    def _run(self, runnable):
        timer = Timer(self.timeout, self._timeout_exceeded)
        timer.start()
        try:
            result = runnable()
        except TimeoutExceeded:
            self._timeout_pending = False
            raise
        finally:
            timer.cancel()
        self._wait_for_pending_timeout()
        return result

    def _timeout_exceeded(self):
        self.exceeded = True
        if not self.paused:
            self._timeout_pending = True
            self._raise_async_timeout()

    def _raise_async_timeout(self):
        # See the following for the original recipe and API docs.
        # https://code.activestate.com/recipes/496960-thread2-killable-threads/
        # https://docs.python.org/3/c-api/init.html#c.PyThreadState_SetAsyncExc
        tid = ctypes.c_ulong(self._runner_thread_id)
        error = ctypes.py_object(type(self.timeout_error))
        modified = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, error)
        # This should never happen. Better anyway to check the return value
        # and report the very unlikely error than ignore it.
        if modified != 1:
            raise ValueError(
                f"Expected 'PyThreadState_SetAsyncExc' to return 1, got {modified}."
            )

    def _wait_for_pending_timeout(self):
        # Wait for asynchronously raised timeout that hasn't yet been received.
        # This can happen if a timeout occurs at the same time when the executed
        # function returns. If the execution ever gets here, the timeout should
        # happen immediately. The while loop shouldn't need a limit, but better
        # to have it to avoid a deadlock even if our code had a bug.
        if self._timeout_pending:
            self._timeout_pending = False
            end = time.time() + 1
            while time.time() < end:
                time.sleep(0)

    def pause(self):
        super().pause()
        self._wait_for_pending_timeout()
