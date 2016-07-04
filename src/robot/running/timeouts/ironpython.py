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

import sys
import threading

from System.Threading import Thread, ThreadStart


class Timeout(object):

    def __init__(self, timeout, error):
        self._timeout = timeout
        self._error = error

    def execute(self, runnable):
        runner = Runner(runnable)
        thread = Thread(ThreadStart(runner))
        thread.IsBackground = True
        thread.Start()
        if not thread.Join(self._timeout * 1000):
            thread.Abort()
            raise self._error
        return runner.get_result()


class Runner(object):

    def __init__(self, runnable):
        self._runnable = runnable
        self._result = None
        self._error = None

    def __call__(self):
        threading.currentThread().setName('RobotFrameworkTimeoutThread')
        try:
            self._result = self._runnable()
        except:
            self._error = sys.exc_info()

    def get_result(self):
        if not self._error:
            return self._result
        raise self._error[0], self._error[1], self._error[2]
