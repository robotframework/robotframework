#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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
try:
    import signal
except ImportError:
    signal = None  # IronPython 2.6 doesn't have signal module by default
if sys.platform.startswith('java'):
    from java.lang import IllegalArgumentException
else:
    IllegalArgumentException = None

from robot.errors import ExecutionFailed
from robot.output import LOGGER


class _StopSignalMonitor(object):

    def __init__(self):
        self._signal_count = 0
        self._running_keyword = False

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

    def start(self):
        if signal:
            for signum in signal.SIGINT, signal.SIGTERM:
                self._register_signal_handler(signum)

    def _register_signal_handler(self, signum):
        try:
            signal.signal(signum, self)
        except (ValueError, IllegalArgumentException), err:
            # ValueError occurs e.g. if Robot doesn't run on main thread.
            # IllegalArgumentException is http://bugs.jython.org/issue1729
            if currentThread().getName() == 'MainThread':
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
