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

from io import StringIO
import sys

from robot.output import LOGGER
from robot.utils import console_decode, console_encode


class OutputCapturer:

    def __init__(self, library_import=False):
        self._library_import = library_import
        self._python_out = PythonCapturer(stdout=True)
        self._python_err = PythonCapturer(stdout=False)

    def __enter__(self):
        if self._library_import:
            LOGGER.enable_library_import_logging()
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        self._release_and_log()
        if self._library_import:
            LOGGER.disable_library_import_logging()
        return False

    def _release_and_log(self):
        stdout, stderr = self._release()
        if stdout:
            LOGGER.log_output(stdout)
        if stderr:
            LOGGER.log_output(stderr)
            sys.__stderr__.write(console_encode(stderr, stream=sys.__stderr__))

    def _release(self):
        stdout = self._python_out.release()
        stderr = self._python_err.release()
        return stdout, stderr


class PythonCapturer:

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
        try:
            return self._get_value(self._stream)
        finally:
            self._stream.close()
            self._avoid_at_exit_errors(self._stream)

    def _get_value(self, stream):
        try:
            return console_decode(stream.getvalue())
        except UnicodeError:
            # Error occurs if non-ASCII chars logged both as str and unicode.
            stream.buf = console_decode(stream.buf)
            stream.buflist = [console_decode(item) for item in stream.buflist]
            return stream.getvalue()

    def _avoid_at_exit_errors(self, stream):
        # Avoid ValueError at program exit when logging module tries to call
        # methods of streams it has intercepted that are already closed.
        # Which methods are called, and does logging silence possible errors,
        # depends on Python version. For related discussion see
        # http://bugs.python.org/issue6333
        stream.write = lambda s: None
        stream.flush = lambda: None
