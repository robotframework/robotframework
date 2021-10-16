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
        # See, for example, http://tomerfiliba.com/recipes/Thread2/
        # for more information about using PyThreadState_SetAsyncExc
        tid = ctypes.c_long(self._runner_thread_id)
        error = ctypes.py_object(type(self._error))
        while ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, error) > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            time.sleep(0)  # give time for other threads
