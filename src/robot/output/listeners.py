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
from loggerhelper import AbstractLoggerProxy
from logger import LOGGER

if utils.is_jython:
    from java.lang import Object
        

class Listeners:
    
    def __init__(self, listeners):
        self._listeners = self._import_listneres(listeners)

    def __nonzero__(self):
        return len(self._listeners) > 0

    def _import_listneres(self, listener_data):
        listeners = []
        for name, args in listener_data:
            try:
                listeners.append(_ListenerProxy(name, args))
            except:
                message, details = utils.get_error_details()
                if args:
                    name += ':' + ':'.join(args)
                LOGGER.error("Taking listener '%s' into use failed: %s"
                             % (name, message))
                LOGGER.info("Details:\n%s" % details)
        return listeners

    def start_suite(self, suite):
        for li in self._listeners:
            if li.version == 1:
                li.call_method(li.start_suite, suite.name, suite.doc)
            else:
                li.call_method(li.start_suite, suite.name, 
                               self._get_args(suite, ['doc']))

    def end_suite(self, suite):
        for li in self._listeners:
            if li.version == 1:
                li.call_method(li.end_suite, suite.status, 
                               suite.get_full_message())
            else:
                args = self._get_args(suite, ['status'], 
                                      {'message': 'get_full_message'})
                li.call_method(li.end_suite, suite.name, args)
    
    def start_test(self, test):
        for li in self._listeners:
            if li.version == 1:
                li.call_method(li.start_test, test.name, test.doc, test.tags)
            else:
                li.call_method(li.start_test, test.name, 
                               self._get_args(test, ['doc', 'tags']))
                
    def end_test(self, test):
        for li in self._listeners:
            if li.version == 1:
                li.call_method(li.end_test, test.status, test.message)
            else:
                li.call_method(li.end_test, test.name, 
                               self._get_args(test, ['status', 'message']))

    def start_keyword(self, kw):
        for li in self._listeners:
            if li.version == 1:
                li.call_method(li.start_keyword, kw.name, kw.args)
            else:
                li.call_method(li.start_keyword, kw.name, 
                               self._get_args(kw, ['args']))
        
    def end_keyword(self, kw):
        for li in self._listeners:
            if li.version == 1:
                li.call_method(li.end_keyword, kw.status)
            else:
                li.call_method(li.end_keyword, kw.name, 
                               self._get_args(kw, ['status']))

    def output_file(self, name, path):
        for li in self._listeners:
            li.call_method(getattr(li, '%s_file' % name.lower()), path)
            
    def close(self):
        for li in self._listeners:
            li.call_method(li.close)

    def _get_args(self, item, name_list=None, name_dict=None):
        if not name_dict:
            name_dict = {}
        if name_list:
            name_dict.update(dict([(n, n) for n in name_list]))
        attrs = {}
        for name, attr in name_dict.items():
            attr = getattr(item, attr)
            if callable(attr):
                attr = attr()
            attrs[name] = attr
        return attrs
    
 
class _ListenerProxy(AbstractLoggerProxy):
    _methods = ['start_suite', 'end_suite', 'start_test', 'end_test', 
                'start_keyword', 'end_keyword', 'output_file', 'summary_file', 
                'report_file', 'log_file', 'debug_file', 'close']

    def __init__(self, name, args):
        listener = self._import_listener(name, args)
        AbstractLoggerProxy.__init__(self, listener)
        self.name = name
        self.version = getattr(listener, 'ROBOT_LISTENER_API_VERSION', 1)
        self.is_java = utils.is_jython and isinstance(listener, Object)

    def _import_listener(self, name, args):
        listener, source = utils.import_(name, 'listener')
        if not isinstance(listener, types.ModuleType):
            listener = listener(*args)
        elif args:
            raise DataError("Listeners implemented as modules do not take arguments")
        LOGGER.info("Imported listener '%s' with arguments %s (source %s)" 
                    % (name, utils.seq2str2(args), source))
        return listener

    def call_method(self, method, *args):
        if self.is_java and len(args) == 2 and isinstance(args[1], dict):
            args = (args[0], utils.dict2map(args[1]))
        try:
            method(*args)
        except:
            message, details = utils.get_error_details()
            LOGGER.error("Calling '%s' method of listener '%s' failed: %s"
                         % (method.__name__, self.name, message))
            LOGGER.info("Details:\n%s" % details)

