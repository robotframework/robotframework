#  Copyright 2008-2014 Nokia Solutions and Networks
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

__version__ = '1.0.1'

import errno
import re
import select
import sys
import inspect
import traceback
from StringIO import StringIO
from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import Binary
try:
    import signal
except ImportError:
    signal = None
try:
    from collections import Mapping
except ImportError:
    Mapping = dict


BINARY = re.compile('[\x00-\x08\x0B\x0C\x0E-\x1F]')
NON_ASCII = re.compile('[\x80-\xff]')


class RobotRemoteServer(SimpleXMLRPCServer):
    allow_reuse_address = True
    _generic_exceptions = (AssertionError, RuntimeError, Exception)
    _fatal_exceptions = (SystemExit, KeyboardInterrupt)

    def __init__(self, library, host='127.0.0.1', port=8270, port_file=None,
                 allow_stop=True):
        """Configure and start-up remote server.

        :param library:     Test library instance or module to host.
        :param host:        Address to listen. Use ``'0.0.0.0'`` to listen
                            to all available interfaces.
        :param port:        Port to listen. Use ``0`` to select a free port
                            automatically. Can be given as an integer or as
                            a string.
        :param port_file:   File to write port that is used. ``None`` means
                            no such file is written.
        :param allow_stop:  Allow/disallow stopping the server using
                            ``Stop Remote Server`` keyword.
        """
        SimpleXMLRPCServer.__init__(self, (host, int(port)), logRequests=False)
        self._library = library
        self._allow_stop = allow_stop
        self._shutdown = False
        self._register_functions()
        self._register_signal_handlers()
        self._announce_start(port_file)
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
        for name in 'SIGINT', 'SIGTERM', 'SIGHUP':
            if hasattr(signal, name):
                signal.signal(getattr(signal, name), stop_with_signal)

    def _announce_start(self, port_file=None):
        host, port = self.server_address
        self._log('Robot Framework remote server at %s:%s starting.'
                  % (host, port))
        if port_file:
            pf = open(port_file, 'w')
            try:
                pf.write(str(port))
            finally:
                pf.close()

    def serve_forever(self):
        if hasattr(self, 'timeout'):
            self.timeout = 0.5
        elif sys.platform.startswith('java'):
            self.socket.settimeout(0.5)
        while not self._shutdown:
            try:
                self.handle_request()
            except (OSError, select.error), err:
                if err.args[0] != errno.EINTR:
                    raise

    def stop_remote_server(self):
        prefix = 'Robot Framework remote server at %s:%s ' % self.server_address
        if self._allow_stop:
            self._log(prefix + 'stopping.')
            self._shutdown = True
        else:
            self._log(prefix + 'does not allow stopping.', 'WARN')
        return self._shutdown

    def get_keyword_names(self):
        get_kw_names = getattr(self._library, 'get_keyword_names', None) or \
                       getattr(self._library, 'getKeywordNames', None)
        if self._is_function_or_method(get_kw_names):
            names = get_kw_names()
        else:
            names = [attr for attr in dir(self._library) if attr[0] != '_' and
                     self._is_function_or_method(getattr(self._library, attr))]
        return names + ['stop_remote_server']

    def _is_function_or_method(self, item):
        # Cannot use inspect.isroutine because it returns True for
        # object().__init__ with Jython and IronPython
        return inspect.isfunction(item) or inspect.ismethod(item)

    def run_keyword(self, name, args, kwargs=None):
        args, kwargs = self._handle_binary_args(args, kwargs or {})
        result = {'status': 'FAIL'}
        self._intercept_std_streams()
        try:
            return_value = self._get_keyword(name)(*args, **kwargs)
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            self._add_to_result(result, 'error',
                                self._get_error_message(exc_type, exc_value))
            self._add_to_result(result, 'traceback',
                                self._get_error_traceback(exc_tb))
            self._add_to_result(result, 'continuable',
                                self._get_error_attribute(exc_value, 'CONTINUE'),
                                default=False)
            self._add_to_result(result, 'fatal',
                                self._get_error_attribute(exc_value, 'EXIT'),
                                default=False)
        else:
            try:
                self._add_to_result(result, 'return',
                                    self._handle_return_value(return_value))
            except:
                exc_type, exc_value, _ = sys.exc_info()
                self._add_to_result(result, 'error',
                                    self._get_error_message(exc_type, exc_value))
            else:
                result['status'] = 'PASS'
        self._add_to_result(result, 'output', self._restore_std_streams())
        return result

    def _handle_binary_args(self, args, kwargs):
        args = [self._handle_binary_arg(a) for a in args]
        kwargs = dict([(k, self._handle_binary_arg(v)) for k, v in kwargs.items()])
        return args, kwargs

    def _handle_binary_arg(self, arg):
        if isinstance(arg, Binary):
            return arg.data
        return arg

    def _add_to_result(self, result, key, value, default=''):
        if value != default:
            result[key] = value

    def get_keyword_arguments(self, name):
        kw = self._get_keyword(name)
        if not kw:
            return []
        return self._arguments_from_kw(kw)

    def _arguments_from_kw(self, kw):
        args, varargs, kwargs, defaults = inspect.getargspec(kw)
        if inspect.ismethod(kw):
            args = args[1:]  # drop 'self'
        if defaults:
            args, names = args[:-len(defaults)], args[-len(defaults):]
            args += ['%s=%s' % (n, d) for n, d in zip(names, defaults)]
        if varargs:
            args.append('*%s' % varargs)
        if kwargs:
            args.append('**%s' % kwargs)
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
        if not self._is_function_or_method(kw):
            return None
        return kw

    def _get_error_message(self, exc_type, exc_value):
        if exc_type in self._fatal_exceptions:
            self._restore_std_streams()
            raise
        name = exc_type.__name__
        message = self._get_message_from_exception(exc_value)
        if not message:
            return name
        if exc_type in self._generic_exceptions \
                or getattr(exc_value, 'ROBOT_SUPPRESS_NAME', False):
            return message
        return '%s: %s' % (name, message)

    def _get_message_from_exception(self, value):
        # UnicodeError occurs below 2.6 and if message contains non-ASCII bytes
        try:
            msg = unicode(value)
        except UnicodeError:
            msg = ' '.join([self._str(a, handle_binary=False) for a in value.args])
        return self._handle_binary_result(msg)

    def _get_error_traceback(self, exc_tb):
        # Latest entry originates from this class so it can be removed
        entries = traceback.extract_tb(exc_tb)[1:]
        trace = ''.join(traceback.format_list(entries))
        return 'Traceback (most recent call last):\n' + trace

    def _get_error_attribute(self, exc_value, name):
        return bool(getattr(exc_value, 'ROBOT_%s_ON_FAILURE' % name, False))

    def _handle_return_value(self, ret):
        if isinstance(ret, basestring):
            return self._handle_binary_result(ret)
        if isinstance(ret, (int, long, float)):
            return ret
        if isinstance(ret, Mapping):
            return dict([(self._str(key), self._handle_return_value(value))
                         for key, value in ret.items()])
        try:
            return [self._handle_return_value(item) for item in ret]
        except TypeError:
            return self._str(ret)

    def _handle_binary_result(self, result):
        if not self._contains_binary(result):
            return result
        try:
            result = str(result)
        except UnicodeError:
            raise ValueError("Cannot represent %r as binary." % result)
        return Binary(result)

    def _contains_binary(self, result):
        return (BINARY.search(result) or isinstance(result, str) and
                sys.platform != 'cli' and NON_ASCII.search(result))

    def _str(self, item, handle_binary=True):
        if item is None:
            return ''
        if not isinstance(item, basestring):
            item = unicode(item)
        if handle_binary:
            return self._handle_binary_result(item)
        return item

    def _intercept_std_streams(self):
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def _restore_std_streams(self):
        stdout = sys.stdout.getvalue()
        stderr = sys.stderr.getvalue()
        close = [sys.stdout, sys.stderr]
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        for stream in close:
            stream.close()
        if stdout and stderr:
            if not stderr.startswith(('*TRACE*', '*DEBUG*', '*INFO*', '*HTML*',
                                      '*WARN*')):
                stderr = '*INFO* %s' % stderr
            if not stdout.endswith('\n'):
                stdout += '\n'
        return self._handle_binary_result(stdout + stderr)

    def _log(self, msg, level=None):
        if level:
            msg = '*%s* %s' % (level.upper(), msg)
        self._write_to_stream(msg, sys.stdout)
        if sys.__stdout__ is not sys.stdout:
            self._write_to_stream(msg, sys.__stdout__)

    def _write_to_stream(self, msg, stream):
        stream.write(msg + '\n')
        stream.flush()


if __name__ == '__main__':
    import xmlrpclib

    def stop(uri):
        server = test(uri, log_success=False)
        if server is not None:
            print 'Stopping remote server at %s.' % uri
            server.stop_remote_server()

    def test(uri, log_success=True):
        server = xmlrpclib.ServerProxy(uri)
        try:
            server.get_keyword_names()
        except:
            print 'No remote server running at %s.' % uri
            return None
        if log_success:
            print 'Remote server running at %s.' % uri
        return server

    def parse_args(args):
        actions = {'stop': stop, 'test': test}
        if not args or len(args) > 2 or args[0] not in actions:
            sys.exit('Usage:  python -m robotremoteserver test|stop [uri]')
        uri = len(args) == 2 and args[1] or 'http://127.0.0.1:8270'
        if '://' not in uri:
            uri = 'http://' + uri
        return actions[args[0]], uri

    action, uri = parse_args(sys.argv[1:])
    action(uri)
