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
from threading import current_thread, Lock, Timer


class Timeout:

    def __init__(self, timeout, error):
        self._runner_thread_id = current_thread().ident
        self._timer = Timer(timeout, self._timed_out)
        self._error = error
        self._timeout_occurred = False
        self._finished = False
        self._lock = Lock()

    def execute(self, runnable):
        try:
            self._start_timer()
            try:
                result = runnable()
            finally:
                self._cancel_timer()
            self._wait_for_raised_timeout()
            return result
        finally:
            if self._timeout_occurred:
                raise self._error

    def _start_timer(self):
        self._timer.start()

    def _cancel_timer(self):
        with self._lock:
            self._finished = True
            self._timer.cancel()

    def _wait_for_raised_timeout(self):
        if self._timeout_occurred:
            while True:
                time.sleep(0)

    def _timed_out(self):
        with self._lock:
            if self._finished:
                return
            self._timeout_occurred = True
        self._raise_timeout()

    def _raise_timeout(self):
        # See the following for the original recipe and API docs.
        # https://code.activestate.com/recipes/496960-thread2-killable-threads/
        # https://docs.python.org/3/c-api/init.html#c.PyThreadState_SetAsyncExc
        tid = ctypes.c_ulong(self._runner_thread_id)
        error = ctypes.py_object(type(self._error))
        modified = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, error)
        # This should never happen. Better anyway to check the return value
        # and report the very unlikely error than ignore it.
        if modified != 1:
            raise ValueError(
                f"Expected 'PyThreadState_SetAsyncExc' to return 1, got {modified}."
            )
