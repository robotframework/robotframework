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

import os.path
import sys
import re
import traceback

from unic import unic
from robot.errors import DataError, TimeoutError, RemoteError

_is_java = sys.platform.startswith('java')
RERAISED_EXCEPTIONS = (KeyboardInterrupt, SystemExit, MemoryError)
if _is_java:
    from java.io import StringWriter, PrintWriter
    from java.lang import Throwable, OutOfMemoryError
    RERAISED_EXCEPTIONS += (OutOfMemoryError,)

_java_trace_re = re.compile('^\s+at (\w.+)')
_ignored_java_trace = ('org.python.', 'robot.running.', 'robot$py.',
                       'sun.reflect.', 'java.lang.reflect.')
_ignore_trace_until = (os.path.join('robot','running','handlers.py'), '<lambda>')
_generic_exceptions = ('AssertionError', 'AssertionFailedError', 'Exception',
                       'Error', 'RuntimeError', 'RuntimeException',
                       'DataError', 'TimeoutError', 'RemoteError')


def get_error_message():
    """Returns error message of the last occurred exception.

    This method handles also exceptions containing unicode messages. Thus it
    MUST be used to get messages from all exceptions originating outside the
    framework.
    """
    return ErrorDetails().message


def get_error_details():
    """Returns error message and details of the last occurred exception.
    """
    details = ErrorDetails()
    return details.message, details.traceback


def ErrorDetails():
    """This factory returns an object that wraps the last occurred exception

    It has attributes `message`, `traceback` and `error`, where `message`
    contains type and message of the original error, `traceback` contains the
    traceback/stack trace and `error` contains the original error instance.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_type in RERAISED_EXCEPTIONS:
        raise exc_value
    if _is_java and isinstance(exc_value, Throwable):
        return _JavaErrorDetails(exc_type, exc_value, exc_traceback)
    return _PythonErrorDetails(exc_type, exc_value, exc_traceback)


class _ErrorDetails(object):

    def __init__(self, exc_type, exc_value, exc_traceback):
        self.error = exc_value
        self._exc_value = exc_value
        self._exc_type = exc_type
        self._exc_traceback = exc_traceback
        self._message = None
        self._traceback = None

    @property
    def message(self):
        if self._message is None:
            self._message = self._get_message()
        return self._message

    @property
    def traceback(self):
        if self._traceback is None:
            self._traceback = self._get_details()
        return self._traceback

    def _get_name(self, exc_type):
        try:
            return exc_type.__name__
        except AttributeError:
            return unic(exc_type)

    def _format_message(self, name, message):
        message = unic(message or '')
        message = self._clean_up_message(message, name)
        name = name.split('.')[-1]  # Use only last part of the name
        if message == '':
            return name
        if name in _generic_exceptions:
            return message
        return '%s: %s' % (name, message)

    def _clean_up_message(self, message, name):
        return message


class _PythonErrorDetails(_ErrorDetails):

    def _get_message(self):
        # If exception is a "string exception" without a message exc_value is None
        if self._exc_value is None:
            return unic(self._exc_type)
        name = self._get_name(self._exc_type)
        try:
            msg = unicode(self._exc_value)
        except UnicodeError:  # Happens if message is Unicode and version < 2.6
            msg = ' '.join(unic(a) for a in self._exc_value.args)
        return self._format_message(name, msg)

    def _get_details(self):
        if isinstance(self._exc_value, (DataError, TimeoutError)):
            return ''
        if isinstance(self._exc_value, RemoteError):
            return self._exc_value.traceback
        tb = traceback.extract_tb(self._exc_traceback)
        for row, (path, _, func, _) in enumerate(tb):
            if path.endswith(_ignore_trace_until[0]) and func == _ignore_trace_until[1]:
                tb = tb[row+1:]
                break
        details = 'Traceback (most recent call last):\n' \
                + ''.join(traceback.format_list(tb))
        return details.strip()


class _JavaErrorDetails(_ErrorDetails):

    def _get_message(self):
        exc_name = self._get_name(self._exc_type)
        # OOME.getMessage and even toString seem to throw NullPointerException
        if not self._is_out_of_memory_error(self._exc_type):
            exc_msg = self._exc_value.getMessage()
        else:
            exc_msg = str(self._exc_value)
        return self._format_message(exc_name, exc_msg)

    def _is_out_of_memory_error(self, exc_type):
        return exc_type is OutOfMemoryError

    def _get_details(self):
        # OOME.printStackTrace seems to throw NullPointerException
        if self._is_out_of_memory_error(self._exc_type):
            return ''
        output = StringWriter()
        self._exc_value.printStackTrace(PrintWriter(output))
        lines = [ line for line in output.toString().splitlines()
                  if line and not self._is_ignored_stack_trace_line(line) ]
        details = '\n'.join(lines)
        msg = unic(self._exc_value.getMessage() or '')
        if msg:
            details = details.replace(msg, '', 1)
        return details

    def _is_ignored_stack_trace_line(self, line):
        res = _java_trace_re.match(line)
        if res is None:
            return False
        location = res.group(1)
        for entry in _ignored_java_trace:
            if location.startswith(entry):
                return True
        return False

    def _clean_up_message(self, msg, name):
        msg = self._remove_stack_trace_lines(msg)
        return self._remove_exception_name(msg, name).strip()

    def _remove_stack_trace_lines(self, msg):
        lines = msg.splitlines()
        while lines:
            if _java_trace_re.match(lines[-1]):
                lines.pop()
            else:
                break
        return '\n'.join(lines)

    def _remove_exception_name(self, msg, name):
        tokens = msg.split(':', 1)
        if len(tokens) == 2 and tokens[0] == name:
            msg = tokens[1]
        return msg
