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

import ctypes
import thread
import time
from threading import Timer

from robot.errors import TimeoutError


class Timeout(object):

    def __init__(self, timeout, timeout_error):
        self._runner_thread_id = thread.get_ident()
        self._timeout_error = self._create_timeout_error_class(timeout_error)
        self._timer = Timer(timeout, self._raise_timeout_error)
        self._timeout_occurred = False

    def _create_timeout_error_class(self, timeout_error):
        return type(TimeoutError.__name__,
                   (TimeoutError,),
                   {'__unicode__': lambda self: timeout_error})

    def execute(self, runnable):
        self._start_timer()
        try:
            return runnable()
        finally:
            self._stop_timer()

    def _start_timer(self):
        self._timer.start()

    def _stop_timer(self):
        self._timer.cancel()
        # In case timeout has occurred but the exception has not yet been
        # thrown we need to do this to ensure that the exception
        # is not thrown in an unsafe location
        if self._timeout_occurred:
            self._cancel_exception()
            raise self._timeout_error()

    def _raise_timeout_error(self):
        self._timeout_occurred = True
        return_code = self._try_to_raise_timeout_error_in_runner_thread()
        # return code tells how many threads have been influenced
        while return_code > 1: # if more than one then cancel and retry
            self._cancel_exception()
            time.sleep(0) # yield so that other threads will get time
            return_code = self._try_to_raise_timeout_error_in_runner_thread()

    def _try_to_raise_timeout_error_in_runner_thread(self):
        return ctypes.pythonapi.PyThreadState_SetAsyncExc(
            self._runner_thread_id,
            ctypes.py_object(self._timeout_error))

    def _cancel_exception(self):
        ctypes.pythonapi.PyThreadState_SetAsyncExc(self._runner_thread_id, None)
