import sys
from StringIO import StringIO
from types import MethodType, FunctionType
from SimpleXMLRPCServer import SimpleXMLRPCServer
try:
    import signal
except ImportError:
    signal = None


class RobotRemoteServer(SimpleXMLRPCServer):
  
    def __init__(self, library, port=8270):
        SimpleXMLRPCServer.__init__(self, ('localhost', int(port)))
        self._library = library
        self.register_function(self.get_keyword_names)
        self.register_function(self.run_keyword)
        self.register_function(self.stop_remote_server)
        if signal:
            callback = lambda signum, frame: self.stop_remote_server()
            signal.signal(signal.SIGHUP, callback)
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
        return [ attr for attr in dir(self._library) if attr[0] != '_'
                 and isinstance(getattr(self._library, attr),
                                (MethodType, FunctionType)) ]

    def run_keyword(self, name, args):
        result = {'status':'PASS', 'return':'', 'message':'',  'output':''}
        self._redirect_stdout()
        try:
            return_value = getattr(self._library, name)(*args)
        except Exception, exp:
            result['status'] = 'FAIL'
            result['message'] = str(exp)
        else:
            result['return'] = self._handle_return_value(return_value)
        result['output'] = self._restore_stdout()
        return result
  
    def _handle_return_value(self, ret):
        if isinstance(ret, (basestring, int, long, float, bool)):
            return ret
        if isinstance(ret, (tuple, list)):
            return [ self._handle_return_value(item) for item in ret ]
        if isinstance(ret, dict):
            return dict([ (self._return_value_to_str(key),
                           self._handle_return_value(value))
                          for key, value in ret.items() ])
        return self._return_value_to_str(ret)

    def _return_value_to_str(self, ret):
        if ret is None:
            return ''
        return str(ret)

    def _redirect_stdout(self):
        # TODO: What about stderr?
        sys.stdout = StringIO()

    def _restore_stdout(self):
        output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        return output

