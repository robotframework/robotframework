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
    """

    def __init__(self):
        self._writers = []
        self._output_filers = []
        self._closers = []
        self._message_cache = []
        self.monitor = None

    def disable_message_cache(self):
        self._message_cache = None

    def register_logger(self, *loggers):
        for logger in loggers:
            if hasattr(logger, 'write'):
                self._writers.append(logger.write)
                if self._message_cache:
                    for msg in self._message_cache:
                        logger.write(msg, msg.level)
            if hasattr(logger, 'output_file'):
                self._output_filers.append(logger.output_file)
            if hasattr(logger, 'close'):
                self._closers.append(logger.close)

    def register_command_line_monitor(self, width=78, colors=True):
        self.monitor = CommandLineMonitor(width, colors)
        self.register_logger(self.monitor)

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
        for write in self._writers:
            write(msg, level)
        if self._message_cache is not None:
            self._message_cache.append(msg)

    def output_file(self, name, path):
        for output_file in self._output_filers:
            output_file(name, path)

    def close(self):
        for close in self._closers:
            close()
        self.__init__()


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
