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

import ctypes
import thread
import threading
import time
from robot.errors import TimeoutError
from robot.running.timeouts.timeoutbase import _Timeout


class TimeoutError(TimeoutError):
    global_message = ''

    def __unicode__(self):
        return TimeoutError.global_message

class TimeoutSignaler(object):

    def __init__(self, timeout, timeout_error):
        self._runner_thread_id = thread.get_ident()
        TimeoutError.global_message = timeout_error
        self._timer = threading.Timer(timeout, self)
        self._timeout_occurred = False

    def start(self):
        self._timer.start()

    def cancel(self):
        self._timer.cancel()
        # In case timeout has occurred but the exception has not yet been
        # thrown we need to do this to ensure that the exception
        # is not thrown in an unsafe location
        if self._timeout_occurred:
            self._cancel_exception()
            raise TimeoutError()

    def __call__(self):
        self._timeout_occurred = True
        return_code = self._try_to_raise_timeout_error_in_runner_thread()
        while return_code > 1:
            self._cancel_exception()
            time.sleep(0) # yield so that other threads will get time
            return_code = self._try_to_raise_timeout_error_in_runner_thread()

    def _try_to_raise_timeout_error_in_runner_thread(self):
        return ctypes.pythonapi.PyThreadState_SetAsyncExc(
            self._runner_thread_id,
            ctypes.py_object(TimeoutError))

    def _cancel_exception(self):
        ctypes.pythonapi.PyThreadState_SetAsyncExc(self._runner_thread_id, None)


class TimeoutWithTimerThrowingException(_Timeout):

    def _execute_with_timeout(self, timeout, runnable, args, kwargs):
        self._enable_timeout(timeout)
        try:
            return runnable(*(args or ()), **(kwargs or {}))
        finally:
            self._disable_timeout()

    def _enable_timeout(self, timeout):
        self._signaler = TimeoutSignaler(timeout, self._get_timeout_error())
        self._signaler.start()

    def _disable_timeout(self):
        self._signaler.cancel()
