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
from StringIO import StringIO

from robot.output import LOGGER


class OutputCapturer:

    def __init__(self, library_import=False):
        if library_import:
            LOGGER.enable_library_import_logging()
        self._library_import = library_import
        self._python_out = _PythonCapturer(stdout=True)
        self._python_err = _PythonCapturer(stdout=False)
        self._java_out = _JavaCapturer(stdout=True)
        self._java_err = _JavaCapturer(stdout=False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.release_and_log()
        return False

    def release_and_log(self):
        stdout, stderr = self._release()
        if stdout:
            LOGGER.log_output(stdout)
        if stderr:
            LOGGER.log_output(stderr)
            sys.__stderr__.write(stderr+'\n')
        if self._library_import:
            LOGGER.disable_library_import_logging()

    def _release(self):
        py_out = self._python_out.release()
        py_err = self._python_err.release()
        java_out = self._java_out.release()
        java_err = self._java_err.release()
        # This should return both Python and Java stdout/stderr.
        # It is unfortunately not possible to do py_out+java_out here, because
        # java_out is always Unicode and py_out is bytes (=str). When py_out
        # contains non-ASCII bytes catenation fails with UnicodeError.
        # Unfortunately utils.unic(py_out) doesn't work either, because later
        # splitting the output to levels and messages fails. Should investigate
        # why that happens. It also seems that the byte message are never
        # converted to Unicode - at least Message class doesn't do that.
        # It's probably safe to leave this code like it is in RF 2.5, because
        # a) the earlier versions worked the same way, and b) this code is
        # used so that there should never be output both from Python and Java.
        return (py_out, py_err) if (py_out or py_err) else (java_out, java_err)


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
