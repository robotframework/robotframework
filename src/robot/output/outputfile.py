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

from pathlib import Path

from robot.errors import DataError
from robot.utils import get_error_message

from .loggerapi import LoggerApi
from .loglevel import LogLevel
from .jsonlogger import JsonLogger
from .xmllogger import LegacyXmlLogger, NullLogger, XmlLogger


class OutputFile(LoggerApi):

    def __init__(self, path: 'Path|None', log_level: LogLevel, rpa: bool = False,
                 legacy_output: bool = False):
        # `self.logger` is replaced with `NullLogger` when flattening.
        self.logger = self.real_logger = self._get_logger(path, rpa, legacy_output)
        self.is_logged = log_level.is_logged
        self.flatten_level = 0
        self.errors = []

    def _get_logger(self, path, rpa, legacy_output):
        if not path:
            return NullLogger()
        try:
            file = open(path, 'w', encoding='UTF-8')
        except Exception:
            raise DataError(f"Opening output file '{path}' failed: "
                            f"{get_error_message()}")
        if path.suffix.lower() == '.json':
            return JsonLogger(file, rpa)
        if legacy_output:
            return LegacyXmlLogger(file, rpa)
        return XmlLogger(file, rpa)

    def start_suite(self, data, result):
        self.logger.start_suite(result)

    def end_suite(self, data, result):
        self.logger.end_suite(result)

    def start_test(self, data, result):
        self.logger.start_test(result)

    def end_test(self, data, result):
        self.logger.end_test(result)

    def start_keyword(self, data, result):
        self.logger.start_keyword(result)
        if result.tags.robot('flatten'):
            self.flatten_level += 1
            self.logger = NullLogger()

    def end_keyword(self, data, result):
        if self.flatten_level and result.tags.robot('flatten'):
            self.flatten_level -= 1
            if self.flatten_level == 0:
                self.logger = self.real_logger
        self.logger.end_keyword(result)

    def start_for(self, data, result):
        self.logger.start_for(result)

    def end_for(self, data, result):
        self.logger.end_for(result)

    def start_for_iteration(self, data, result):
        self.logger.start_for_iteration(result)

    def end_for_iteration(self, data, result):
        self.logger.end_for_iteration(result)

    def start_while(self, data, result):
        self.logger.start_while(result)

    def end_while(self, data, result):
        self.logger.end_while(result)

    def start_while_iteration(self, data, result):
        self.logger.start_while_iteration(result)

    def end_while_iteration(self, data, result):
        self.logger.end_while_iteration(result)

    def start_if(self, data, result):
        self.logger.start_if(result)

    def end_if(self, data, result):
        self.logger.end_if(result)

    def start_if_branch(self, data, result):
        self.logger.start_if_branch(result)

    def end_if_branch(self, data, result):
        self.logger.end_if_branch(result)

    def start_try(self, data, result):
        self.logger.start_try(result)

    def end_try(self, data, result):
        self.logger.end_try(result)

    def start_try_branch(self, data, result):
        self.logger.start_try_branch(result)

    def end_try_branch(self, data, result):
        self.logger.end_try_branch(result)

    def start_group(self, data, result):
        self.logger.start_group(result)

    def end_group(self, data, result):
        self.logger.end_group(result)

    def start_var(self, data, result):
        self.logger.start_var(result)

    def end_var(self, data, result):
        self.logger.end_var(result)

    def start_break(self, data, result):
        self.logger.start_break(result)

    def end_break(self, data, result):
        self.logger.end_break(result)

    def start_continue(self, data, result):
        self.logger.start_continue(result)

    def end_continue(self, data, result):
        self.logger.end_continue(result)

    def start_return(self, data, result):
        self.logger.start_return(result)

    def end_return(self, data, result):
        self.logger.end_return(result)

    def start_error(self, data, result):
        self.logger.start_error(result)

    def end_error(self, data, result):
        self.logger.end_error(result)

    def log_message(self, message):
        if self.is_logged(message):
            # Use the real logger also when flattening.
            self.real_logger.message(message)

    def message(self, message):
        if message.level in ('WARN', 'ERROR'):
            self.errors.append(message)

    def statistics(self, stats):
        self.logger.statistics(stats)

    def close(self):
        self.logger.errors(self.errors)
        self.logger.close()
