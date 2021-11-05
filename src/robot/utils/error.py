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

import os
import sys
import traceback

from robot.errors import RobotError

from .platform import RERAISED_EXCEPTIONS


EXCLUDE_ROBOT_TRACES = not os.getenv('ROBOT_INTERNAL_TRACES')


def get_error_message():
    """Returns error message of the last occurred exception.

    This method handles also exceptions containing unicode messages. Thus it
    MUST be used to get messages from all exceptions originating outside the
    framework.
    """
    return ErrorDetails().message


def get_error_details(exclude_robot_traces=EXCLUDE_ROBOT_TRACES):
    """Returns error message and details of the last occurred exception."""
    details = ErrorDetails(exclude_robot_traces=exclude_robot_traces)
    return details.message, details.traceback


class ErrorDetails:
    """Object wrapping the last occurred exception.

    It has attributes `message`, `traceback` and `error`, where `message`
    contains type and message of the original error, `traceback` contains the
    traceback and `error` contains the original error instance.
    """
    _generic_names = frozenset(('AssertionError', 'Error', 'Exception', 'RuntimeError'))

    def __init__(self, exc_info=None, exclude_robot_traces=EXCLUDE_ROBOT_TRACES):
        exc_type, exc_value, exc_traceback = exc_info or sys.exc_info()
        if exc_type in RERAISED_EXCEPTIONS:
            raise exc_value
        self.error = exc_value
        self._exc_traceback = exc_traceback
        self._exclude_robot_traces = exclude_robot_traces
        self._message = None
        self._traceback = None

    @property
    def message(self):
        if self._message is None:
            self._message = self._format_message(self.error)
        return self._message

    @property
    def traceback(self):
        if self._traceback is None:
            self._traceback = self._get_details()
        return self._traceback

    def _get_details(self):
        if isinstance(self.error, RobotError):
            return self.error.details
        return 'Traceback (most recent call last):\n' + self._get_traceback()

    def _get_traceback(self):
        tb = self._exc_traceback
        while tb and self._is_excluded_traceback(tb):
            tb = tb.tb_next
        if not tb:
            return '  None'
        return ''.join(traceback.format_tb(tb)).rstrip()

    def _is_excluded_traceback(self, tb):
        if self._exclude_robot_traces:
            module = tb.tb_frame.f_globals.get('__name__')
            return module and module.startswith('robot.')
        return False

    def _format_message(self, error):
        name = type(error).__name__.split('.')[-1]  # Use only the last part
        message = str(error)
        if not message:
            return name
        if self._suppress_name(name, error):
            return message
        if message.startswith('*HTML*'):
            name = '*HTML* ' + name
            message = message.split('*', 2)[-1].lstrip()
        return '%s: %s' % (name, message)

    def _suppress_name(self, name, error):
        return (name in self._generic_names
                or isinstance(error, RobotError)
                or getattr(error, 'ROBOT_SUPPRESS_NAME', False))
