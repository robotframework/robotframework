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
from threading import currentThread
import signal
if sys.platform.startswith('java'):
    from java.lang import IllegalArgumentException
else:
    IllegalArgumentException = ValueError

from robot.errors import ExecutionFailed
from robot.output import LOGGER


class _StopSignalMonitor(object):

    def __init__(self):
        self._signal_count = 0
        self._running_keyword = False
        self._orig_sigint = None
        self._orig_sigterm = None

    def __call__(self, signum, frame):
        self._signal_count += 1
        LOGGER.info('Received signal: %s.' % signum)
        if self._signal_count > 1:
            sys.__stderr__.write('Execution forcefully stopped.\n')
            raise SystemExit()
        sys.__stderr__.write('Second signal will force exit.\n')
        if self._running_keyword and not sys.platform.startswith('java'):
            self._stop_execution_gracefully()

    def _stop_execution_gracefully(self):
        raise ExecutionFailed('Execution terminated by signal', exit=True)

    def __enter__(self):
        if self._can_register_signal:
            self._orig_sigint = signal.getsignal(signal.SIGINT)
            self._orig_sigterm = signal.getsignal(signal.SIGTERM)
            for signum in signal.SIGINT, signal.SIGTERM:
                self._register_signal_handler(signum)
        return self

    def __exit__(self, *exc_info):
        if self._can_register_signal:
            signal.signal(signal.SIGINT, self._orig_sigint)
            signal.signal(signal.SIGTERM, self._orig_sigterm)

    @property
    def _can_register_signal(self):
        return signal and currentThread().getName() == 'MainThread'

    def _register_signal_handler(self, signum):
        try:
            signal.signal(signum, self)
        except (ValueError, IllegalArgumentException) as err:
            # IllegalArgumentException due to http://bugs.jython.org/issue1729
            self._warn_about_registeration_error(signum, err)

    def _warn_about_registeration_error(self, signum, err):
        name, ctrlc = {signal.SIGINT: ('INT', 'or with Ctrl-C '),
                       signal.SIGTERM: ('TERM', '')}[signum]
        LOGGER.warn('Registering signal %s failed. Stopping execution '
                    'gracefully with this signal %sis not possible. '
                    'Original error was: %s' % (name, ctrlc, err))

    def start_running_keyword(self, in_teardown):
        self._running_keyword = True
        if self._signal_count and not in_teardown:
            self._stop_execution_gracefully()

    def stop_running_keyword(self):
        self._running_keyword = False


STOP_SIGNAL_MONITOR = _StopSignalMonitor()
