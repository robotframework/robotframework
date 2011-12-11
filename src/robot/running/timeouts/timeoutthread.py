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
from robot.running.timeouts.timeoutbase import _Timeout
from robot.utils.robotthread import ThreadedRunner


class TimeoutWithThread(_Timeout):

    def _execute_with_timeout(self, timeout, runnable, args, kwargs):
        runner = ThreadedRunner(runnable, args, kwargs)
        if runner.run_in_thread(timeout):
            return runner.get_result()
        try:
            runner.stop_thread()
        except:
            raise TimeoutError('Stopping keyword after %s failed: %s'
                               % (self.type.lower(), utils.get_error_message()))
        raise TimeoutError(self._get_timeout_error())

_Timeout = TimeoutWithThread
