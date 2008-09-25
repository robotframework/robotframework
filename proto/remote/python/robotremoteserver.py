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
  
    def __init__(self, library, port=8270):
        SimpleXMLRPCServer.__init__(self, ('localhost', int(port)),
                                    logRequests=False)
        self._library = library
        self.register_function(self.get_keyword_names)
        self.register_function(self.run_keyword)
        self.register_function(self.get_keyword_arguments)
        self.register_function(self.get_keyword_documentation)
        self.register_function(self.stop_remote_server)
        callback = lambda signum, frame: self.stop_remote_server()
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, callback)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, callback)
        self.serve_forever()

    def serve_forever(self):
        self._shutdown = False
        while not self._shutdown:
            self.handle_request()

    def stop_remote_server(self):
        self._shutdown = True
        return True

    def get_keyword_names(self):
        names = [ attr for attr in dir(self._library) if attr[0] != '_'
                  and callable(getattr(self._library, attr)) ]
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
        args, varargs, _, defaults = inspect.getargspec(kw)
        if inspect.ismethod(kw):
            args = args[1:]  # drop 'self'
        if defaults:
            args, names = args[:-len(defaults)], args[-len(defaults):]
            args += [ '%s=%s' % (name, value)
                      for name, value in zip(names, defaults) ]
        if varargs:
            args.append('*%s' % varargs)
        return args

    # TODO: Not tested
    def get_keyword_documentation(self, name):
        return inspect.getdoc(self._get_keyword(name)) or ''

    def _get_keyword(self, name):
        if name == 'stop_remote_server':
            return self.stop_remote_server
        return getattr(self._library, name)

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
            return [ self._handle_return_value(item) for item in ret ]
        if isinstance(ret, dict):
            return dict([ (self._str(key), self._handle_return_value(value))
                          for key, value in ret.items() ])
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
