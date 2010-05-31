#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

RERAISED_EXCEPTIONS = (KeyboardInterrupt, SystemExit, MemoryError)
if sys.platform.startswith('java'):
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
    dets = ErrorDetails()
    return dets.message, dets.traceback


class ErrorDetails(object):
    """This class wraps the last occurred exception

    It has attributes message, traceback and error, where message contains
    type and message of the original error, traceback it's contains traceback
    (or stack trace in case of Java exception) and error contains the original
    error instance

    This class handles also exceptions containing unicode messages. Thus it
    MUST be used to get messages from all exceptions originating outside the
    framework.
    """

    def __init__(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type in RERAISED_EXCEPTIONS:
            raise exc_value
        if _is_java_exception(exc_value):
            self.message = _get_java_message(exc_type, exc_value)
            self.traceback = _get_java_details(exc_value)
        else:
            self.message = _get_python_message(exc_type, exc_value)
            self.traceback = _get_python_details(exc_value, exc_traceback)
        self.error = exc_value


def _is_java_exception(exc):
    return sys.platform.startswith('java') and isinstance(exc, Throwable)

def _get_name(exc_type):
    try:
        return exc_type.__name__
    except AttributeError:
        return unic(exc_type)


def _get_java_message(exc_type, exc_value):
    exc_name = _get_name(exc_type)
    # OOME.getMessage and even toString seem to throw NullPointerException
    if exc_type is OutOfMemoryError:
        exc_msg = str(exc_value)
    else:
        exc_msg = exc_value.getMessage()
    return _format_message(exc_name, exc_msg, java=True)


def _get_java_details(exc_value):
    # OOME.printStackTrace seems to throw NullPointerException
    if isinstance(exc_value, OutOfMemoryError):
        return ''
    output = StringWriter()
    exc_value.printStackTrace(PrintWriter(output))
    lines = [ line for line in output.toString().splitlines()
              if line and not _is_ignored_stacktrace_line(line) ]
    details = '\n'.join(lines)
    msg = unic(exc_value.getMessage() or '')
    if msg:
        details = details.replace(msg, '', 1)
    return details

def _is_ignored_stacktrace_line(line):
    res = _java_trace_re.match(line)
    if res is None:
        return False
    location = res.group(1)
    for entry in _ignored_java_trace:
        if location.startswith(entry):
            return True
    return False


def _get_python_message(exc_type, exc_value):
    # If exception is a "string exception" without a message exc_value is None
    if exc_value is None:
        return unic(exc_type)
    name = _get_name(exc_type)
    try:
        msg = unicode(exc_value)
    except UnicodeError:  # Happens if message is Unicode and version < 2.6
        msg = ' '.join(unic(a) for a in exc_value.args)
    return _format_message(name, msg)


def _get_python_details(exc_value, exc_tb):
    if isinstance(exc_value, (DataError, TimeoutError)):
        return ''
    if isinstance(exc_value, RemoteError):
        return exc_value.traceback
    tb = traceback.extract_tb(exc_tb)
    for row, (path, _, func, _) in enumerate(tb):
        if path.endswith(_ignore_trace_until[0]) and func == _ignore_trace_until[1]:
            tb = tb[row+1:]
            break
    details = 'Traceback (most recent call last):\n' \
            + ''.join(traceback.format_list(tb))
    return details.strip()


def _format_message(name, message, java=False):
    message = unic(message or '')
    if java:
        message = _clean_up_java_message(message, name)
    name = name.split('.')[-1]  # Use only last part of the name
    if message == '':
        return name
    if name in _generic_exceptions:
        return message
    return '%s: %s' % (name, message)


def _clean_up_java_message(msg, name):
    # Remove possible stack trace from messages
    lines = msg.splitlines()
    while lines:
        if _java_trace_re.match(lines[-1]):
            lines.pop()
        else:
            break
    msg = '\n'.join(lines)
    # Remove possible exception name from the message
    tokens = msg.split(':', 1)
    if len(tokens) == 2 and tokens[0] == name:
        msg = tokens[1]
    return msg.strip()
