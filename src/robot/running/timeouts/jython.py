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

import sys

from java.lang import Thread, Runnable

from robot.errors import TimeoutError


class Timeout(object):

    def __init__(self, timeout, error):
        self._timeout = timeout
        self._error = error

    def execute(self, runnable):
        runner = Runner(runnable)
        thread = Thread(runner, name='RobotFrameworkTimeoutThread')
        thread.setDaemon(True)
        thread.start()
        thread.join(int(self._timeout * 1000))
        if thread.isAlive():
            thread.stop()
            raise TimeoutError(self._error)
        return runner.get_result()


class Runner(Runnable):

    def __init__(self, runnable):
        self._runnable = runnable
        self._result = None
        self._error = None

    def run(self):
        try:
            self._result = self._runnable()
        except:
            self._error = sys.exc_info()

    def get_result(self):
        if not self._error:
            return self._result
        raise self._error[0], self._error[1], self._error[2]
