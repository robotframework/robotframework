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


from robot.common.statistics import Statistics
import re

from robot import utils
import robot

from loggerhelper import AbstractLogger, Message, LEVELS
from logger import LOGGER
from xmllogger import XmlLogger
from listeners import Listeners
from debugfile import DebugFile


class Output(AbstractLogger):
    
    def __init__(self, settings):
        AbstractLogger.__init__(self)
        self._xmllogger = XmlLogger(settings['Output'], settings['LogLevel'],
                                    settings['SplitOutputs'])
        self._register_loggers(settings['Listeners'], settings['DebugFile'])
        self._namegen = self._get_log_name_generator(settings['Log'])
        self._settings = settings
        robot.output.OUTPUT = self
        
    def _register_loggers(self, listeners, debugfile):
        LOGGER.register_logger(self._xmllogger)
        for logger in Listeners(listeners), DebugFile(debugfile):
            if logger: LOGGER.register_logger(logger)
        LOGGER.disable_message_cache()

    def _get_log_name_generator(self, log):
        return log != 'NONE' and utils.FileNameGenerator(log) or None
        
    def close(self, suite):
        stats = Statistics(suite, self._settings['SuiteStatLevel'], 
                           self._settings['TagStatInclude'], 
                           self._settings['TagStatExclude'], 
                           self._settings['TagStatCombine'],
                           self._settings['TagDoc'],
                           self._settings['TagStatLink'])
        stats.serialize(self._xmllogger)
        self._xmllogger.close(serialize_errors=True)
        LOGGER.output_file('Output', self._settings['Output'])
            
    def start_suite(self, suite):
        LOGGER.start_suite(suite)
        if self._xmllogger.started_output:
            suite.namespace.variables.set_global('${OUTPUT_FILE}',
                                                 self._xmllogger.started_output)
            if self._namegen:
                suite.namespace.variables.set_global('${LOG_FILE}', 
                                                     self._namegen.get_name())
        
    def end_suite(self, suite):
        LOGGER.end_suite(suite)
        if self._xmllogger.ended_output:
            LOGGER.output_file('Output', self._xmllogger.ended_output)
            orig_outpath = self._settings['Output']
            suite.namespace.variables.set_global('${OUTPUT_FILE}', orig_outpath)
            self._create_split_log(self._xmllogger.ended_output, suite)

    def _create_split_log(self, outpath, suite):
        if self._namegen is None:
            return
        logpath = self._namegen.get_prev()
        output = robot.serializing.SplitSubTestOutput(outpath)
        output.serialize_log(logpath)
        suite.namespace.variables.set_global('${LOG_FILE}', self._namegen.get_base())
        
    def start_test(self, test):
        LOGGER.start_test(test)
        
    def end_test(self, test):
        LOGGER.end_test(test)
        
    def start_keyword(self, kw):
        LOGGER.start_keyword(kw)
        
    def end_keyword(self, kw):
        LOGGER.end_keyword(kw)

    def log_output(self, output):
        """Splits given output to levels and messages and logs them"""
        for msg in _OutputSplitter(output).messages:
            self._write(msg)

    def _write(self, msg):
        # Called also by AbstractLogger.write
        LOGGER.log_message(msg)
            
    def set_log_level(self, level):
        return self._xmllogger.set_log_level(level)


class _OutputSplitter:
    
    _split_output_regexp = re.compile('^(\*(?:%s|HTML)\*)' % '|'.join(LEVELS),
                                      re.MULTILINE)
    
    def __init__(self, output):
        self.messages = self._get_messages(output.strip())

    def _get_messages(self, output):
        if not output:
            return []
        tokens = self._split_output_regexp.split(output)
        if len(tokens) == 1:
            return [Message(output, 'INFO', False)]
        return self._split_messages(tokens)
            
    def _split_messages(self, tokens):
        # Output started with a level
        if tokens[0] == '':
            tokens = tokens[1:]
        # No level in the beginning, default first msg to INFO
        else:
            tokens.insert(0, '*INFO*')
        messages = []
        for i in range(0, len(tokens), 2):
            level, html = self._get_level_and_html(tokens[i][1:-1])
            msg = tokens[i+1].strip()  
            messages.append(Message(msg,level, html))
        return messages

    def _get_level_and_html(self, token):
        if token == 'HTML':
            return 'INFO', True
        return token, False
