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

import time

from robot import utils
from robot.utils.robotthread import Thread, Runner, Event
from robot.errors import TimeoutError, DataError, FrameworkError


class _Timeout:

    _defaults = ('', -1, None)

    def __init__(self, *params):
        try:
            self.string, self.secs, self.message = self._process_params(params)
            self.error = None
        except DataError, err:
            self.string, self.secs, self.message = self._defaults
            self.secs = 0.000001
            self.error = 'Setting %s timeout failed: %s' % (self.type, err)
        self.starttime = 0

    def _process_params(self, params):
        if len(params) == 0:
            return self._defaults
        secs = utils.timestr_to_secs(params[0])
        msg = len(params) > 1 and ' '.join(params[1:]) or None
        return utils.secs_to_timestr(secs), secs, msg

    def start(self):
        self.starttime = time.time()

    def time_left(self):
        if self.starttime == 0:
            raise FrameworkError('Timeout not started')
        elapsed = time.time() - self.starttime
        return self.secs - elapsed

    def active(self):
        return self.secs > 0

    def timed_out(self):
        return self.active() and self.time_left() < 0

    def __str__(self):
        return self.string

    def __cmp__(self, other):
        if utils.is_str(other):
            return cmp(str(self), other)
        if not self.active():
            return 1
        if not other.active():
            return -1
        return cmp(self.time_left(), other.time_left())

    def run(self, runnable, args=None, kwargs=None, logger=None):
        if self.error is not None:
            raise DataError(self.error)
        if not self.active():
            raise FrameworkError('Timeout is not active')
        timeout = self.time_left()
        if timeout <= 0:
            raise TimeoutError(self.get_message())
        if logger is not None:
            logger.debug('%s timeout %s active. %s seconds left.'
                         % (self.type.capitalize(), self.string, round(timeout, 3)))
        notifier = Event()
        runner = Runner(runnable, args, kwargs, notifier)
        # Thread's name is important - it's used in utils.outputcapture
        thread = Thread(runner, stoppable=True, daemon=True, name='TIMED_RUN')
        thread.start()
        time.sleep(0.001)
        notifier.wait(timeout)
        if runner.is_done():
            return runner.get_result()
        try:
            thread.stop()
        except utils.RERAISED_EXCEPTIONS:
            raise
        except:
            pass
        raise TimeoutError(self.get_message())

    def get_message(self):
        if self.message is not None:
            return self.message
        return '%s timeout %s exceeded.' % (self.type.capitalize(), self.string)


class TestTimeout(_Timeout):
    type = 'test'


class KeywordTimeout(_Timeout):
    type = 'keyword'
