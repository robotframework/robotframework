#  Copyright 2008 Nokia Siemens Networks Oyj
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

from robot import utils

from abstractlogger import AbstractLogger, Message
from monitor import CommandLineMonitor


class SystemLogger(AbstractLogger):
    """Global system logger, to which new loggers may be registered.

    Whenever something is written to SYSLOG in code, all registered loggers are
    notified.  Messages are also cached and cached messasges written to new
    loggers when they are registered.

    Tools using Robot Framework's internal modules should register their own
    loggers at least to get notifications about errors and warnings. A shortcut
    to get errors/warnings into console is using 'register_console_logger'.
    """

    def __init__(self):
        self._loggers = []
        self._message_cache = []

    def disable_message_cache(self):
        self._message_cache = None

    def register_logger(self, *loggers):
        for log in loggers:
            logger = _Logger(log)
            self._loggers.append(logger)
            if self._message_cache:
                for msg in self._message_cache:
                    logger.write(msg, msg.level)

    def register_console_logger(self, width=78, colors=True):
        monitor = CommandLineMonitor(width, colors)
        self.register_logger(monitor)

    def register_file_logger(self, path=None, level='INFO'):
        if not path:
            path = os.environ.get('ROBOT_SYSLOG_FILE', 'NONE')
            level = os.environ.get('ROBOT_SYSLOG_LEVEL', level)
        if path.upper() == 'NONE':
            return
        try:
            logger = _FileLogger(path, level)
        except:
            self.error("Opening syslog file '%s' failed: %s"  
                       % (path, utils.get_error_message()))
        else:
            self.register_logger(logger)

    def write(self, message, level='INFO'):
        msg = Message(message, level)
        for logger in self._loggers:
            logger.write(msg, level)
        if self._message_cache is not None:
            self._message_cache.append(msg)

    def start_suite(self, suite):
        for logger in self._loggers:
            logger.start_suite(suite)

    def end_suite(self, suite):
        for logger in self._loggers:
            logger.end_suite(suite)

    def start_test(self, test):
        for logger in self._loggers:
            logger.start_test(test)

    def end_test(self, test):
        for logger in self._loggers:
            logger.end_test(test)

    def start_keyword(self, keyword):
        for logger in self._loggers:
            logger.start_keyword(keyword)

    def end_keyword(self, keyword):
        for logger in self._loggers:
            logger.end_keyword(keyword)

    def output_file(self, name, path):
        for logger in self._loggers:
            logger.output_file(name, path)

    def close(self):
        for logger in self._loggers:
            logger.close()
        self.__init__()


class _Logger:

    def __init__(self, logger):
        for name in ['write', 'output_file', 'close',
                     'start_suite', 'end_suite', 'start_test', 'end_test',
                     'start_keyword', 'end_keyword']:
            method = getattr(logger, name, lambda *args: None)
            setattr(self, name, method)


class _FileLogger(AbstractLogger):

    def __init__(self, path, level):
        AbstractLogger.__init__(self, level)
        self._writer = self._get_writer(path)
        
    def _get_writer(self, path):
        # Hook for unittests
        return open(path, 'wb')
    
    def _write(self, message):
        entry = '%s | %s | %s\n' % (message.timestamp, message.level.ljust(5), 
                                    message.message)
        self._writer.write(utils.unic(entry).encode('UTF-8'))
        
    def output_file(self, name, path):
        self.info('%s: %s' % (name, path))

    def close(self):
        self._writer.close()


SYSLOG = SystemLogger()
