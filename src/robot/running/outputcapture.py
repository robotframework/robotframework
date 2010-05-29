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
from StringIO import StringIO


class OutputCapturer:

    def __init__(self):
        self._python_out = _PythonCapturer(stdout=True)
        self._python_err = _PythonCapturer(stdout=False)
        self._java_out = _JavaCapturer(stdout=True)
        self._java_err = _JavaCapturer(stdout=False)

    def release(self):
        # Only either Python or Java output generally contains something
        stdout = self._python_out.release() + self._java_out.release()
        stderr = self._python_err.release() + self._java_err.release()
        return stdout, stderr


class _PythonCapturer(object):

    def __init__(self, stdout=True):
        if stdout:
            self._original = sys.stdout
            self._set_stream = self._set_stdout
        else:
            self._original = sys.stderr
            self._set_stream = self._set_stderr
        self._stream = StringIO()
        self._set_stream(self._stream)

    def _set_stdout(self, stream):
        sys.stdout = stream 

    def _set_stderr(self, stream):
        sys.stderr = stream 

    def release(self):
        # Original stream must be restored before closing the current
        self._set_stream(self._original)
        self._stream.flush()
        output = self._stream.getvalue()
        self._stream.close()
        return output


if not sys.platform.startswith('java'):

    class _JavaCapturer(object):
        def __init__(self, stdout):
            pass
        def release(self):
            return ''

else:

    from java.io import PrintStream, ByteArrayOutputStream
    from java.lang import System


    class _JavaCapturer(object):

        def __init__(self, stdout=True):
            if stdout:
                self._original = System.out
                self._set_stream = System.setOut
            else:
                self._original = System.err
                self._set_stream = System.setErr
            self._bytes = ByteArrayOutputStream()
            self._stream = PrintStream(self._bytes, False, 'UTF-8')
            self._set_stream(self._stream)

        def release(self):
            # Original stream must be restored before closing the current
            self._set_stream(self._original)
            self._stream.close()
            output = self._bytes.toString('UTF-8')
            self._bytes.reset()
            return output
