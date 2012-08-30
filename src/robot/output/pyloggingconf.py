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

import logging

from robot.api import logger
from robot import utils

LEVELS = {'TRACE': logging.NOTSET,
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARN': logging.WARNING}


def initialize(level):
    logging.raiseExceptions = False
    logging.getLogger().addHandler(RobotHandler())
    set_level(level)


def set_level(level):
    try:
        level = LEVELS[level.upper()]
    except KeyError:
        return
    logging.getLogger().setLevel(level)


class RobotHandler(logging.Handler):

    def emit(self, record):
        message, error = self._get_message(record)
        method = self._get_logger_method(record.levelno)
        method(message)
        if error:
            logger.debug(error)

    def _get_message(self, record):
        try:
            return record.getMessage(), None
        except:
            message = 'Failed to log following message properly: %s' \
                        % utils.unic(record.msg)
            error = '\n'.join(utils.get_error_details())
            return message, error

    def _get_logger_method(self, level):
        if level >= logging.WARNING:
            return logger.warn
        if level >= logging.INFO:
            return logger.info
        if level >= logging.DEBUG:
            return logger.debug
        return logger.trace
