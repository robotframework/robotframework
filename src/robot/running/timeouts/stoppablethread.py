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
import threading


class Thread(threading.Thread):
    """A subclass of threading.Thread, with a stop() method.

    Original version posted by Connelly Barnes to python-list and available at
    http://mail.python.org/pipermail/python-list/2004-May/219465.html

    This version mainly has kill() changed to stop() to match java.lang.Thread.

    This is a hack but seems to be the best way the get this done. Only used
    in Python because in Jython we can use java.lang.Thread.
    """

    def __init__(self, runner, name=None):
        threading.Thread.__init__(self, target=runner, name=name)
        self._stopped = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def stop(self):
        self._stopped = True

    def __run(self):
        """Hacked run function, which installs the trace."""
        sys.settrace(self._globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def _globaltrace(self, frame, why, arg):
        if why == 'call':
            return self._localtrace
        else:
            return None

    def _localtrace(self, frame, why, arg):
        if self._stopped:
            if why == 'line':
                raise SystemExit()
        return self._localtrace
