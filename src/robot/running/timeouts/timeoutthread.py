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
from robot import utils
from robot.errors import TimeoutError
from robot.utils.robotthread import ThreadedRunner


class Timeout(object):

    def __init__(self, timeout, error, timeout_type):
        self._timeout = timeout
        self._error = error
        self._timeout_type = timeout_type

    def execute(self, runnable, args, kwargs):
        runner = ThreadedRunner(runnable, args, kwargs)
        if runner.run_in_thread(self._timeout):
            return runner.get_result()
        try:
            runner.stop_thread()
        except:
            raise TimeoutError('Stopping keyword after timeout failed: %s'
                               % (self._timeout_type, utils.get_error_message()))
        raise TimeoutError(self._error)
