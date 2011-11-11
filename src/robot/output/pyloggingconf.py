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

import logging

from robot.api import logger


LEVELS = {'TRACE': logging.NOTSET,
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARN': logging.WARNING}


def initialize(level):
    logging.basicConfig(level=LEVELS[level.upper()], stream=NullStream())
    logging.getLogger().addHandler(RobotHandler())


def set_level(level):
    logging.getLogger().setLevel(LEVELS[level.upper()])


class RobotHandler(logging.Handler):

    def emit(self, record):
        method = self._get_logger_method(record.levelno)
        method(record.getMessage())

    def _get_logger_method(self, level):
        if level >= logging.WARNING:
            return logger.warn
        if level >= logging.INFO:
            return logger.info
        if level >= logging.DEBUG:
            return logger.debug
        return logger.trace


class NullStream(object):

    def write(self, message):
        pass

    def close(self):
        pass

    def flush(self):
        pass
