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

import sys
from threading import Event

from robot.errors import TimeoutError

if sys.platform.startswith('java'):
    from java.lang import Thread, Runnable
else:
    from .stoppablethread import Thread
    Runnable = object


TIMEOUT_THREAD_NAME = 'RobotFrameworkTimeoutThread'


class ThreadedRunner(Runnable):

    def __init__(self, runnable):
        self._runnable = runnable
        self._notifier = Event()
        self._result = None
        self._error = None
        self._traceback = None
        self._thread = None

    def run(self):
        try:
            self._result = self._runnable()
        except:
            self._error, self._traceback = sys.exc_info()[1:]
        self._notifier.set()

    __call__ = run

    def run_in_thread(self, timeout):
        self._thread = Thread(self, name=TIMEOUT_THREAD_NAME)
        self._thread.setDaemon(True)
        self._thread.start()
        self._notifier.wait(timeout)
        return self._notifier.isSet()

    def get_result(self):
        if self._error:
            raise self._error, None, self._traceback
        return self._result

    def stop_thread(self):
        self._thread.stop()


class Timeout(object):

    def __init__(self, timeout, error):
        self._timeout = timeout
        self._error = error

    def execute(self, runnable):
        runner = ThreadedRunner(runnable)
        if runner.run_in_thread(self._timeout):
            return runner.get_result()
        runner.stop_thread()
        raise TimeoutError(self._error)


