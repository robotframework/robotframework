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


import sys
import os
from StringIO import StringIO

from robotthread import Semaphore, current_thread

if os.name == 'java':
    from java.io import OutputStream, ByteArrayOutputStream, PrintStream
    from java.lang import System


def capture_output():
    _OUTPUT_CAPTURE.capture_output()

def release_output():
    return _OUTPUT_CAPTURE.release_output()


class _Output:

    def __init__(self):
        self._outs = {}
        self._sema = Semaphore()

    def write(self, msg):
        self._sema.acquire()
        thrd = current_thread()
        key = thrd.getName() == 'TIMED_RUN' and 'TIMED' or thrd
        if not self._outs.has_key(key):
            self._outs[key] = self._get_stream()
        self._outs[key].write(msg)
        self._sema.release()

    def get_value(self):
        self._sema.acquire()
        thrd = current_thread()
        key = self._outs.has_key('TIMED') and 'TIMED' or thrd
        if self._outs.has_key(key):
            self._outs[key].flush()
            msg = self._get_msg(key)
            del(self._outs[key])
            if key is not thrd and self._outs.has_key(thrd):
                del(self._outs[thrd])
        else:
            msg = ''
        self._sema.release()
        return msg


class _PythonOutput(_Output):

    def _get_stream(self):
        return StringIO()

    def _get_msg(self, key):
        return self._outs[key].getvalue()

    def flush(self):
        self._sema.acquire()
        thrd = current_thread()
        key = self._outs.has_key('TIMED') and 'TIMED' or thrd
        if self._outs.has_key(key):
            self._outs[key].flush()
        self._sema.release()


if os.name == 'java':

    class _JavaOutput(_Output, OutputStream):

        def __init__(self):
            OutputStream.__init__(self)
            _Output.__init__(self)

        def _get_stream(self):
            return ByteArrayOutputStream()

        def _get_msg(self, key):
            output = self._outs[key]
            output.flush()
            return output.toString('UTF-8')


class _OutputCapture:

    def __init__(self):
        self._count = 0
        self._sema = Semaphore()

    def capture_output(self):
        self._sema.acquire()
        if self._count == 0:
            self._capture_output()
        self._count += 1
        self._sema.release()

    def _capture_output(self):
        sys.stdout = _PythonOutput()
        sys.stderr = _PythonOutput()
        if os.name == 'java':
            self._orig_java_out = System.out
            self._orig_java_err = System.err
            self._capt_java_out = _JavaOutput()
            self._capt_java_err = _JavaOutput()
            System.setOut(PrintStream(self._capt_java_out, False, 'UTF-8'))
            System.setErr(PrintStream(self._capt_java_err, False, 'UTF-8'))

    def release_output(self):
        self._sema.acquire()
        out, err = self._get_output()
        self._count -= 1
        if self._count == 0:
            self._release_output()
        self._sema.release()
        return out, err

    def _get_output(self):
        if os.name == 'java':
            out = self._capt_java_out.get_value()
            err = self._capt_java_err.get_value()
            if out or err:
                return out, err
        return sys.stdout.get_value(), sys.stderr.get_value()

    def _release_output(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if os.name == 'java':
            System.setOut(self._orig_java_out)
            System.setErr(self._orig_java_err)


_OUTPUT_CAPTURE = _OutputCapture()
