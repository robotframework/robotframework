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

from levels import LEVELS
from abstractlogger import AbstractLogger
from monitor import CommandLineMonitor
from systemlogger import SystemLogger
from xmllogger import XmlLogger
from listeners import Listeners
from debugfile import DebugFile



class Output(AbstractLogger):
    
    def __init__(self, settings):
        AbstractLogger.__init__(self, settings['LogLevel'])
        self.monitor = CommandLineMonitor(settings['MonitorWidth'],
                                          settings['MonitorColors'])
        self.logger = None
        self.syslog = SystemLogger(settings, self.monitor)
        self.listeners = Listeners(settings['Listeners'], self.syslog)
        self.syslog.register_listeners(self.listeners)
        self._debugfile = DebugFile(settings['DebugFile'], self.syslog)
        self._namegen = self._get_log_name_generator(settings['Log'])
        self._settings = settings
        robot.output.OUTPUT = self
        
    def _get_log_name_generator(self, log):
        return log != 'NONE' and utils.FileNameGenerator(log) or None
        
    def close1(self, suite):
        stats = Statistics(suite, self._settings['SuiteStatLevel'], 
                           self._settings['TagStatInclude'], 
                           self._settings['TagStatExclude'], 
                           self._settings['TagStatCombine'],
                           self._settings['TagDoc'],
                           self._settings['TagStatLink'])
        stats.serialize(self.logger)
        self.syslog.serialize(self.logger)
        self.logger.close()
        self.syslog.output_file('Output', self._settings['Output'])
        if self._debugfile is not None:
            self.syslog.output_file('Debug', self._debugfile.path)
            self._debugfile.close()
            
    def close2(self):
        self.listeners.close()
        self.syslog.close()
    
    def start_suite(self, suite):
        self.syslog.info("Running test suite '%s'" % suite.longname)
        if self.logger is None:
            self.logger = XmlLogger(self._settings['Output'], 
                                    self._settings['SplitOutputs'])
        outpath = self.logger.start_suite(suite)
        if outpath is not None:
            suite.namespace.variables.set_global('${OUTPUT_FILE}', outpath)
            if self._namegen is not None:
                suite.namespace.variables.set_global('${LOG_FILE}', 
                                                     self._namegen.get_name())
        self.monitor.start_suite(suite)
        self.listeners.start_suite(suite)
        if self._debugfile is not None:
            self._debugfile.start_suite(suite)
        
    def end_suite(self, suite):
        outpath = self.logger.end_suite(suite)
        if outpath is not None:
            self.syslog.info('Output: %s' % outpath)
            self.listeners.output_file('Output', outpath)
            orig_outpath = self._settings['Output']
            suite.namespace.variables.set_global('${OUTPUT_FILE}', orig_outpath)
            self._create_split_log(outpath, suite)
        self.monitor.end_suite(suite)
        self.listeners.end_suite(suite)
        if self._debugfile is not None:
            self._debugfile.end_suite(suite)

    def _create_split_log(self, outpath, suite):
        if self._namegen is None:
            return
        logpath = self._namegen.get_prev()
        output = robot.serializing.SplitSubTestOutput(outpath)
        output.serialize_log(logpath)
        self.syslog.info('Log: %s' % logpath)
        self.listeners.output_file('Log', logpath)   
        suite.namespace.variables.set_global('${LOG_FILE}', self._namegen.get_base())
        
    def start_test(self, test):
        self.syslog.info("Running test case '%s'" % test.name)
        self.logger.start_test(test)
        self.monitor.start_test(test)
        self.listeners.start_test(test)
        if self._debugfile is not None:
            self._debugfile.start_test(test)
        
    def end_test(self, test):
        self.logger.end_test(test)
        self.monitor.end_test(test)
        self.listeners.end_test(test)
        if self._debugfile is not None:
            self._debugfile.end_test(test)
        
    def start_keyword(self, kw):
        self.logger.start_keyword(kw)
        self.listeners.start_keyword(kw)
        if self._debugfile is not None:
            self._debugfile.start_keyword(kw)
        
    def end_keyword(self, kw):
        self.logger.end_keyword(kw)
        self.listeners.end_keyword(kw)
        if self._debugfile is not None:
            self._debugfile.end_keyword(kw)
     
    def write(self, msg='', level='INFO', html=False):
        if self._debugfile is not None and self._is_logged(level, 'DEBUG'):
            self._debugfile.message(msg)
        AbstractLogger.write(self, msg, level, html)
        
    def _write(self, msg):
        self.logger.message(msg)
    
    def log_output(self, output):
        """Splits given output to levels and messages and logs them"""
        for msg, level, html in _OutputSplitter(output).messages:
            self.write(msg, level, html)
            
    def _split_output(self, output):
        output = output.strip()
        if output == '':
            return []
        tokens = self._split_output_regexp.split(output)
        # No levels, return output with INFO level
        if len(tokens) == 1:
            return [ (output, 'INFO') ]
        # Output started with a level
        if tokens[0] == '':
            tokens = tokens[1:]
        # No level in the beginning, default first msg to INFO
        else:
            tokens.insert(0, '*INFO*')
        ret = []
        for i in range(0, len(tokens), 2):
            level = tokens[i][1:-1]    # remove '*'s around level
            msg = tokens[i+1].strip()  
            ret.append((msg,level))
        return ret
    

class _OutputSplitter:
    
    _split_output_regexp = re.compile('^(\*(?:%s|HTML)\*)' % '|'.join(LEVELS.keys()),
                                      re.MULTILINE)
    
    def __init__(self, output):
        output = output.strip()
        if output == '':
            self.messages = []
        else:
            tokens = self._split_output_regexp.split(output)
            if len(tokens) == 1:
                self.messages = [ (output, 'INFO', False) ]
            else:
                self.messages = self._get_messages(tokens)
            
    def _get_messages(self, tokens):
        # Output started with a level
        if tokens[0] == '':
            tokens = tokens[1:]
        # No level in the beginning, default first msg to INFO
        else:
            tokens.insert(0, '*INFO*')
        messages = []
        for i in range(0, len(tokens), 2):
            level, html = self._get_level_and_html(tokens[i][1:-1])    # remove '*'s around level
            msg = tokens[i+1].strip()  
            messages.append((msg,level, html))
        return messages

    def _get_level_and_html(self, token):
        if token == 'HTML':
            return 'INFO', True
        return token, False
