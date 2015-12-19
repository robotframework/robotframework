#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.errors import TimeoutError
from robot.utils import py2to3


class Timeout(object):

    def __init__(self, timeout, error):
        self._runner_thread_id = current_thread().ident
        self._timeout_error = self._create_timeout_error_class(error)
        self._timer = Timer(timeout, self._raise_timeout_error)
        self._timeout_occurred = False
        self._finished = False
        self._lock = Lock()

    def _create_timeout_error_class(self, error):
        return py2to3(type(TimeoutError.__name__, (TimeoutError,),
                           {'__unicode__': lambda self: error}))

    def execute(self, runnable):
        try:
            self._start_timer()
            result = runnable()
            self._cancel_timer()
            self._wait_for_raised_timeout()
            return result
        finally:
            if self._timeout_occurred:
                raise self._timeout_error()

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

    def _raise_timeout_error(self):
        with self._lock:
            if self._finished:
                return
            self._timeout_occurred = True
        return_code = self._try_to_raise_timeout_error_in_runner_thread()
        # return code tells how many threads have been influenced
        while return_code > 1: # if more than one then cancel and retry
            self._cancel_exception()
            time.sleep(0) # yield so that other threads will get time
            return_code = self._try_to_raise_timeout_error_in_runner_thread()

    def _try_to_raise_timeout_error_in_runner_thread(self):
        return ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self._runner_thread_id),
            ctypes.py_object(self._timeout_error))

    def _cancel_exception(self):
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self._runner_thread_id), None)
