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


class Listeners:
    
    def __init__(self, names, syslog):
        self._listeners = []
        for name in names:
            try:
                self._listeners.append(_Listener(name, syslog))
            except:
                message, details = utils.get_error_details()
                syslog.error("Taking listener '%s' into use failed: %s"
                             % (name, message))
                syslog.info("Details:\n%s" % details)
                
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
    
    def __init__(self, listener_name, syslog):
        self._handlers = {}
        listener_class, _ = utils.import_(listener_name, 'listener')
        listener = listener_class()
        for name in ['start_suite', 'end_suite', 'start_test', 'end_test', 
                     'start_keyword', 'end_keyword', 'output_file', 
                     'summary_file', 'report_file', 'log_file', 'debug_file', 
                     'close']:
            self._handlers[name] = _Handler(listener, listener_name, name, syslog)
            
    def __getattr__(self, name):
        try:
            return self._handlers[name]
        except KeyError:
            raise AttributeError
    

class _Handler:
    
    def __init__(self, listener, listener_name, name, syslog):
        self._handler, self._name = self._get_handler(listener, name)
        self._listener_name = listener_name
        self._syslog = syslog
            
    def __call__(self, *args):
        try:
            if self._handler is not None:
                self._handler(*args)
        except:
            message, details = utils.get_error_details()
            self._syslog.error("Calling '%s' method of listener '%s' failed: %s"
                               % (self._name, self._listener_name, message))
            self._syslog.info("Details:\n%s" % details)
            
    def _get_handler(self, listener, name):
        try:
            try:
                return getattr(listener, name), name
            except AttributeError:
                name =  self._toCamelCase(name)
                return getattr(listener, name), name
        except AttributeError:
            return None, None
    
    def _toCamelCase(self, name):
        parts = name.split('_')
        return ''.join([parts[0]] + [part.capitalize() for part in parts[1:]])
