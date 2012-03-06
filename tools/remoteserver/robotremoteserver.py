#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

import sys
import inspect
import traceback
from StringIO import StringIO
from SimpleXMLRPCServer import SimpleXMLRPCServer
try:
    import signal
except ImportError:
    signal = None


class RobotRemoteServer(SimpleXMLRPCServer):
    allow_reuse_address = True

    def __init__(self, library, host='localhost', port=8270, allow_stop=True):
        SimpleXMLRPCServer.__init__(self, (host, int(port)), logRequests=False)
        self._library = library
        self._allow_stop = allow_stop
        self._register_functions()
        self._register_signal_handlers()
        self._log('Robot Framework remote server starting at %s:%s'
                  % (host, port))
        self.serve_forever()

    def _register_functions(self):
        self.register_function(self.get_keyword_names)
        self.register_function(self.run_keyword)
        self.register_function(self.get_keyword_arguments)
        self.register_function(self.get_keyword_documentation)
        self.register_function(self.stop_remote_server)

    def _register_signal_handlers(self):
        def stop_with_signal(signum, frame):
            self._allow_stop = True
            self.stop_remote_server()
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, stop_with_signal)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, stop_with_signal)

    def serve_forever(self):
        self._shutdown = False
        while not self._shutdown:
            self.handle_request()

    def stop_remote_server(self):
        prefix = 'Robot Framework remote server at %s:%s ' % self.server_address
        if self._allow_stop:
            self._log(prefix + 'stopping')
            self._shutdown = True
        else:
            self._log(prefix + 'does not allow stopping', 'WARN')
        return True

    def get_keyword_names(self):
        get_kw_names = getattr(self._library, 'get_keyword_names', None) or \
                       getattr(self._library, 'getKeywordNames', None)
        if inspect.isroutine(get_kw_names):
            names = get_kw_names()
        else:
            names = [attr for attr in dir(self._library) if attr[0] != '_'
                     and inspect.isroutine(getattr(self._library, attr))]
        return names + ['stop_remote_server']

    def run_keyword(self, name, args):
        result = {'status': 'PASS', 'return': '', 'output': '',
                  'error': '', 'traceback': ''}
        self._intercept_stdout()
        try:
            return_value = self._get_keyword(name)(*args)
        except:
            result['status'] = 'FAIL'
            result['error'], result['traceback'] = self._get_error_details()
        else:
            result['return'] = self._handle_return_value(return_value)
        result['output'] = self._restore_stdout()
        return result

    def get_keyword_arguments(self, name):
        kw = self._get_keyword(name)
        if not kw:
            return []
        return self._arguments_from_kw(kw)

    def _arguments_from_kw(self, kw):
        args, varargs, _, defaults = inspect.getargspec(kw)
        if inspect.ismethod(kw):
            args = args[1:]  # drop 'self'
        if defaults:
            args, names = args[:-len(defaults)], args[-len(defaults):]
            args += ['%s=%s' % (n, d) for n, d in zip(names, defaults)]
        if varargs:
            args.append('*%s' % varargs)
        return args

    def get_keyword_documentation(self, name):
        if name == '__intro__':
            return inspect.getdoc(self._library) or ''
        if name == '__init__' and inspect.ismodule(self._library):
            return ''
        return inspect.getdoc(self._get_keyword(name)) or ''

    def _get_keyword(self, name):
        if name == 'stop_remote_server':
            return self.stop_remote_server
        kw = getattr(self._library, name, None)
        if inspect.isroutine(kw):
            return kw
        return None

    def _get_error_details(self):
        exc_type, exc_value, exc_tb = sys.exc_info()
        if exc_type in (SystemExit, KeyboardInterrupt):
            self._restore_stdout()
            raise
        return (self._get_error_message(exc_type, exc_value),
                self._get_error_traceback(exc_tb))

    def _get_error_message(self, exc_type, exc_value):
        name = exc_type.__name__
        message = str(exc_value)
        if not message:
            return name
        if name in ('AssertionError', 'RuntimeError', 'Exception'):
            return message
        return '%s: %s' % (name, message)

    def _get_error_traceback(self, exc_tb):
        # Latest entry originates from this class so it can be removed
        entries = traceback.extract_tb(exc_tb)[1:]
        trace = ''.join(traceback.format_list(entries))
        return 'Traceback (most recent call last):\n' + trace

    def _handle_return_value(self, ret):
        if isinstance(ret, (basestring, int, long, float)):
            return ret
        if isinstance(ret, (tuple, list)):
            return [self._handle_return_value(item) for item in ret]
        if isinstance(ret, dict):
            return dict([(self._str(key), self._handle_return_value(value))
                         for key, value in ret.items()])
        return self._str(ret)

    def _str(self, item):
        if item is None:
            return ''
        return str(item)

    def _intercept_stdout(self):
        # TODO: What about stderr?
        sys.stdout = StringIO()

    def _restore_stdout(self):
        output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        return output

    def _log(self, msg, level=None):
        if level:
            msg = '*%s* %s' % (level.upper(), msg)
        print msg
