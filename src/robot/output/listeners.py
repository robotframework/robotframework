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


import types

from robot import utils
from robot.errors import DataError
from systemlogger import SYSLOG


class Listeners:
    
    def __init__(self, listeners):
        self._listeners = []
        for name, args in listeners:
            try:
                self._listeners.append(_Listener(name, args))
            except:
                message, details = utils.get_error_details()
                if args:
                    name += ':' + ':'.join(args)
                SYSLOG.error("Taking listener '%s' into use failed: %s"
                             % (name, message))
                SYSLOG.info("Details:\n%s" % details)

    def __nonzero__(self):
        return len(self._listeners) > 0
                
    def start_suite(self, suite):
        for listener in self._listeners:
            listener.start_suite(suite.name, suite.doc)
        
    def end_suite(self, suite):
        for listener in self._listeners:
            listener.end_suite(suite.status, suite.get_full_message())
    
    def start_test(self, test):
        for listener in self._listeners:
            listener.start_test(test.name, test.doc, test.tags)

    def end_test(self, test):
        for listener in self._listeners:
            listener.end_test(test.status, test.message)

    def start_keyword(self, kw):
        for listener in self._listeners:
            listener.start_keyword(kw.name, kw.args)
        
    def end_keyword(self, kw):
        for listener in self._listeners:
            listener.end_keyword(kw.status)

    def output_file(self, name, path):
        for listener in self._listeners:
            getattr(listener, '%s_file' % name.lower())(path)
            
    def close(self):
        for listener in self._listeners:
            listener.close()

    
class _Listener:
    
    def __init__(self, name, args):
        self._handlers = {}
        listener, source = utils.import_(name, 'listener')
        if not isinstance(listener, types.ModuleType):
            listener = listener(*args)
        elif args:
            raise DataError("Listeners implemented as modules do not take arguments")
        SYSLOG.info("Imported listener '%s' with arguments %s (source %s)" 
                    % (name, utils.seq2str2(args), source))
        for func in ['start_suite', 'end_suite', 'start_test', 'end_test', 
                     'start_keyword', 'end_keyword', 'output_file', 
                     'summary_file', 'report_file', 'log_file', 'debug_file', 
                     'close']:
            self._handlers[func] = _Handler(listener, name, func)

    def __getattr__(self, name):
        try:
            return self._handlers[name]
        except KeyError:
            raise AttributeError
    

class _Handler:
    
    def __init__(self, listener, listener_name, name):
        try:
            self._handler, self._name = self._get_handler(listener, name)
        except AttributeError:
            self._handler = self._name = None
            SYSLOG.debug("Listener '%s' does not have method '%s'" 
                         % (listener_name, name))
        else:
            SYSLOG.debug("Listener '%s' has method '%s'" 
                         % (listener_name, self._name))
        self._listener_name = listener_name
            
    def __call__(self, *args):
        try:
            if self._handler is not None:
                self._handler(*args)
        except:
            message, details = utils.get_error_details()
            SYSLOG.error("Calling '%s' method of listener '%s' failed: %s"
                               % (self._name, self._listener_name, message))
            SYSLOG.info("Details:\n%s" % details)
            
    def _get_handler(self, listener, name):
        try:
            return getattr(listener, name), name
        except AttributeError:
            name =  self._toCamelCase(name)
            return getattr(listener, name), name
    
    def _toCamelCase(self, name):
        parts = name.split('_')
        return ''.join([parts[0]] + [part.capitalize() for part in parts[1:]])

