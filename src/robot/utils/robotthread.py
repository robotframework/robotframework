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


import sys
from threading import Event


if sys.platform.startswith('java'):
    from java.lang import Thread, Runnable, Throwable
    JAVA_EXCEPTIONS = (Throwable,)

else:
    from stoppablethread import Thread
    class Runnable(object):
        pass
    JAVA_EXCEPTIONS = ()


class ThreadedRunner(Runnable):

    def __init__(self, runnable, args=None, kwargs=None, notifier=None):
        self._runnable = lambda: runnable(*(args or ()), **(kwargs or {}))
        self._notifier = Event()
        self._result = None
        self._error = None
        self._thread = None

    def run(self):
        try:
            self._result = self._runnable()
        except JAVA_EXCEPTIONS, error:
            self._error = error
        except:
            self._error = sys.exc_info()[1]
        self._notifier.set()

    __call__ = run

    def run_in_thread(self, timeout):
        self._thread = Thread(self)
        self._thread.setDaemon(True)
        self._thread.start()
        self._notifier.wait(timeout)
        return self._notifier.isSet()

    def get_result(self):
        if self._error:
            raise self._error
        return self._result

    def stop_thread(self):
        self._thread.stop()
