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

from robot.utils import file_writer

from .loggerapi import LoggerApi
from .loggerhelper import AbstractLogger
from .loglevel import LogLevel


class FileLogger(AbstractLogger, LoggerApi):

    def __init__(self, path, level):
        self._log_level = LogLevel(level)
        self._writer = self._get_writer(path)  # unit test hook

    def _get_writer(self, path):
        return file_writer(path, usage="syslog")

    def set_level(self, level):
        self._log_level.set(level)

    def message(self, msg):
        if self._log_level.is_logged(msg) and not self._writer.closed:
            entry = f"{msg.timestamp} | {msg.level:5} | {msg.message}\n"
            self._writer.write(entry)

    def start_suite(self, data, result):
        self.info(f"Started suite '{result.name}'.")

    def end_suite(self, data, result):
        self.info(f"Ended suite '{result.name}'.")

    def start_test(self, data, result):
        self.info(f"Started test '{result.name}'.")

    def end_test(self, data, result):
        self.info(f"Ended test '{result.name}'.")

    def start_body_item(self, data, result):
        self.debug(
            lambda: (
                f"Started keyword '{result.name}'."
                if result.type in result.KEYWORD_TYPES
                else result._log_name
            )
        )

    def end_body_item(self, data, result):
        self.debug(
            lambda: (
                f"Ended keyword '{result.name}'."
                if result.type in result.KEYWORD_TYPES
                else result._log_name
            )
        )

    def result_file(self, kind, path):
        self.info(f"{kind}: {path}")

    def close(self):
        self._writer.close()
