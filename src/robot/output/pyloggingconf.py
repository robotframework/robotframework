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

from contextlib import contextmanager
import logging
import traceback

from robot.utils import get_error_details, unic

from . import librarylogger


LEVELS = {'TRACE': logging.NOTSET,
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARN': logging.WARNING,
          'ERROR': logging.ERROR}


@contextmanager
def robot_handler_enabled(level):
    root = logging.getLogger()
    if any(isinstance(h, RobotHandler) for h in root.handlers):
        yield
        return
    handler = RobotHandler()
    old_raise = logging.raiseExceptions
    root.addHandler(handler)
    logging.raiseExceptions = False
    set_level(level)
    try:
        yield
    finally:
        root.removeHandler(handler)
        logging.raiseExceptions = old_raise


def set_level(level):
    try:
        level = LEVELS[level.upper()]
    except KeyError:
        return
    logging.getLogger().setLevel(level)


class RobotHandler(logging.Handler):

    def emit(self, record):
        message, error = self._get_message(record)
        if record.exc_info:
            tb_lines = traceback.format_exception(*record.exc_info)
            message = ''.join([message, '\n'] + tb_lines).rstrip()
        method = self._get_logger_method(record.levelno)
        method(message)
        if error:
            librarylogger.debug(error)

    def _get_message(self, record):
        try:
            return record.getMessage(), None
        except:
            message = 'Failed to log following message properly: %s' \
                        % unic(record.msg)
            error = '\n'.join(get_error_details())
            return message, error

    def _get_logger_method(self, level):
        if level >= logging.ERROR:
            return librarylogger.error
        if level >= logging.WARNING:
            return librarylogger.warn
        if level >= logging.INFO:
            return librarylogger.info
        if level >= logging.DEBUG:
            return librarylogger.debug
        return librarylogger.trace
