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
from robot.utils import file_writer, seq2str2

from .logger import LOGGER
from .loggerapi import LoggerApi
from .loggerhelper import IsLogged

LOG_LEVEL_DEBUG_FILE = "INFO" # output caused by code in this file, depends on this trace level, compared against 'log_level'

def DebugFile(path, log_level):
    if not path:
        LOGGER.info('No debug file')
        return None
    try:
        outfile = file_writer(path, usage='debug')
    except DataError as err:
        LOGGER.error(err.message)
        return None
    else:
        LOGGER.info('Debug file: %s' % path)
        return _DebugFileWriter(outfile, log_level)


class _DebugFileWriter(LoggerApi):
    _separators = {'SUITE': '=', 'TEST': '-', 'KEYWORD': '~'}

    def __init__(self, outfile, log_level):
        self._indent                 = 0
        self._kw_level               = 0
        self._separator_written_last = False
        self._outfile                = outfile
        self._is_logged              = IsLogged(log_level) # previously hard coded level 'DEBUG' replaced by actual level 'log_level'

    def get_level_from_kw_args(self, args=None):
        # args expected to be a 'kw.args' tuple
        supported_levels = ('ERROR', 'WARN', 'USER', 'INFO', 'DEBUG', 'TRACE') # not using LEVELS from loggerhelper.py here, because of more states inside there. A more strict separation is desired here.
        identified_level = LOG_LEVEL_DEBUG_FILE
        if args is None:
            return identified_level
        for arg in args:
            if arg in supported_levels:
                identified_level = arg
                break
        return identified_level

    def start_suite(self, data, result):
        if self._is_logged(LOG_LEVEL_DEBUG_FILE):
            self._separator('SUITE')
            self._start('SUITE', data.full_name, result.start_time)
            self._separator('SUITE')

    def end_suite(self, data, result):
        if self._is_logged(LOG_LEVEL_DEBUG_FILE):
            self._separator('SUITE')
            self._end('SUITE', data.full_name, result.end_time, result.elapsed_time)
            self._separator('SUITE')
            if self._indent == 0:
                LOGGER.debug_file(Path(self._outfile.name))
                self.close()

    def start_test(self, data, result):
        if self._is_logged(LOG_LEVEL_DEBUG_FILE):
            self._separator('TEST')
            self._start('TEST', result.name, result.start_time)
            self._separator('TEST')

    def end_test(self, data, result):
        if self._is_logged(LOG_LEVEL_DEBUG_FILE):
            self._separator('TEST')
            self._end('TEST', result.name, result.end_time, result.elapsed_time)
            self._separator('TEST')

    def start_keyword(self, data, result):
        # inits
        log_kw_start = True
        msg_level = LOG_LEVEL_DEBUG_FILE
        if result.full_name == 'BuiltIn.Log':
            # this keyword has it's own log level
            msg_level = self.get_level_from_kw_args(result.args)
        if self._is_logged(msg_level):
            log_kw_start = True
        else:
            # suppress the logging because the trace level does not match
            log_kw_start = False
        if log_kw_start is True:
            if self._kw_level == 0:
                self._separator('KEYWORD')
            self._start(result.type, result.full_name, result.start_time, seq2str2(result.args))
            self._kw_level += 1

    def end_keyword(self, data, result):
        # inits
        log_kw_end = True
        msg_level = LOG_LEVEL_DEBUG_FILE
        if result.full_name == 'BuiltIn.Log':
            # this keyword has it's own log level
            msg_level = self.get_level_from_kw_args(result.args)
        if self._is_logged(msg_level):
            log_kw_end = True
        else:
            # suppress the logging because the trace level does not match
            log_kw_end = False
        if log_kw_end is True:
            self._end(result.type, result.full_name, result.end_time, result.elapsed_time)
            self._kw_level -= 1

    def start_body_item(self, data, result):
        if self._kw_level == 0:
            self._separator('KEYWORD')
        self._start(result.type, result._log_name, result.start_time)
        self._kw_level += 1

    def end_body_item(self, data, result):
        self._end(result.type, result._log_name, result.end_time, result.elapsed_time)
        self._kw_level -= 1

    def log_message(self, msg):
        if self._is_logged(msg.level):
            self._write(f'{msg.timestamp} - {msg.level} - {msg.message}')

    def close(self):
        if not self._outfile.closed:
            self._outfile.close()

    def _start(self, type, name, timestamp, extra=''):
        if self._is_logged(LOG_LEVEL_DEBUG_FILE):
            if extra:
                extra = f' {extra}'
            indent = '-' * self._indent
            self._write(f'{timestamp} - INFO - +{indent} START {type}: {name}{extra}')
            self._indent += 1

    def _end(self, type, name, timestamp, elapsed):
        if self._is_logged(LOG_LEVEL_DEBUG_FILE):
            self._indent -= 1
            indent = '-' * self._indent
            elapsed = elapsed.total_seconds()
            self._write(f'{timestamp} - INFO - +{indent} END {type}: {name} ({elapsed} s)')

    def _separator(self, type_):
        self._write(self._separators[type_] * 78, separator=True)

    def _write(self, text, separator=False):
        if separator and self._separator_written_last:
            return
        self._outfile.write(text.rstrip() + '\n')
        self._outfile.flush()
        self._separator_written_last = separator
