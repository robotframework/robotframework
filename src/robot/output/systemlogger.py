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


from robot import utils
from robot.conf import RobotSettings

from abstractlogger import AbstractLogger, Message
from monitor import CommandLineMonitor
import robot.output


class SystemLogger2(AbstractLogger):

    def __init__(self):
        self._writers = []
        self._output_filers = []
        self._closers = []

    def register_logger(self, *loggers):
        for logger in loggers:
            if hasattr(logger, 'write'):
                self._writers.append(logger.write)
            if hasattr(logger, 'output_file'):
                self._output_filers.append(logger.output_file)
            if hasattr(logger, 'close'):
                self._closers.append(logger.close)

    def register_file_logger(self, path=None, level='INFO'):
        if not path:
            path = os.env.get('ROBOT_SYSLOG_FILE', None)
            level = os.env.get('ROBOT_SYSLOG_LEVEL', level)
        if path:
            self.register_logger(_FileLogger(path, level))

    def write(self, message, level='INFO'):
        msg = Message(message, level)
        for write in self._writers:
            write(msg, level)

    def output_file(self, name, path):
        for output_file in self._output_filers:
            output_file(name, path)

    def close(self):
        for close in self._closers:
            close()


class SystemLogger(AbstractLogger):
    
    def __init__(self, settings=None, monitor=None):
        AbstractLogger.__init__(self, 'WARN')
        self.messages = []
        self.listeners = None
        if settings is None:
            settings = RobotSettings()
        if monitor is None:
            self.monitor = CommandLineMonitor(settings['MonitorWidth'],
                                              settings['MonitorColors'])
        else:
            self.monitor = monitor
        try:
            self._file_logger = self._get_file_logger(settings['SyslogFile'],
                                                      settings['SyslogLevel'])
        except:
            self._file_logger = None
            self.error("Opening syslog file '%s' failed: %s"  
                       % (settings['SyslogFile'], utils.get_error_message()))
        robot.output.SYSLOG = self
        
    def register_listeners(self, listeners):
        self.listeners = listeners
        
    def _get_file_logger(self, path, level):
        if utils.eq(path, 'NONE'):
            return None
        return _FileLogger(path, level)

    def write(self, msg, level='INFO'):
        if self._file_logger is not None:
            self._file_logger.write(msg, level)
        AbstractLogger.write(self, msg, level)
        
    def _write(self, message):
        self.monitor.error_message(message.message, message.level)
        self.messages.append(message)

    def close(self):
        if self._file_logger is not None:
            self._file_logger.close()
        self._file_logger = None

    def serialize(self, serializer):
        serializer.start_syslog(self)
        for msg in self.messages:
            serializer.message(msg)
        serializer.end_syslog(self)
        
    def output_file(self, name, path):
        self.write('%s: %s' % (name, path))
        self.monitor.output_file(name, path)
        if self.listeners is not None:
            self.listeners.output_file(name, path)


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
        
    def close(self):
        self._writer.close()
