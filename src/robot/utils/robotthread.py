#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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


import os
import sys
import threading

from robot.errors import FrameworkError

if os.name == 'java':
    from java.lang import Runnable, Throwable
    from java.lang import Thread as JavaThread
    java_exceptions = (Throwable,)
else:
    from stoppablethread import StoppablePythonThread
    class Runnable:
        pass
    java_exceptions = ()


class _FakeSemaphore:
    def acquire(self):
        pass
    def release(self):
        pass

def Semaphore():
    # Cygwin Python threads are buggy so use a fake semaphore when possible
    if sys.platform.count('cygwin') > 0 \
            and threading.currentThread().getName() == 'MainThread':
        return _FakeSemaphore()
    return threading.Semaphore()


Event = threading.Event


def current_thread():
    if os.name == 'java':
        return JavaThread.currentThread()
    return threading.currentThread()


class Runner(Runnable):

    def __init__(self, runnable, args=None, kwargs=None, notifier=None):
        self._runnable = runnable
        self._args = args is not None and args or ()
        self._kwargs = kwargs is not None and kwargs or {}
        self._notifier = notifier is not None and notifier or threading.Event()
        self._result = None
        self._error = None

    def run(self):
        if self.is_done():
            raise FrameworkError('Runner can be run only once')
        try:
            self._result = self._runnable(*self._args, **self._kwargs)
        except java_exceptions, error:
            self._error = error
        except:
            self._error = sys.exc_info()[1]
        self._notifier.set()

    __call__ = run

    def is_done(self):
        return self._notifier.isSet()

    def get_result(self):
        if not self.is_done():
            self._notifier.wait()
        if self._error is not None:
            raise self._error
        return self._result


def Thread(runner, stoppable=False, daemon=False, name=None):
    if os.name == 'java':
        thread = JavaThread(runner)   # This is always stoppable
    elif not stoppable:
        thread = threading.Thread(target=runner)
    else:
        thread = StoppablePythonThread(target=runner)
    thread.setDaemon(daemon)
    if name is not None:
        thread.setName(name)
    return thread
