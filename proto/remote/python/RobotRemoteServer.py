import sys
from datetime import datetime
from StringIO import StringIO
from types import MethodType, FunctionType
from SimpleXMLRPCServer import SimpleXMLRPCServer
try:
    import signal
except ImportError:
    signal = None


class RobotRemoteServer(SimpleXMLRPCServer):
  
    _supported_types = (basestring, int, long, float, bool, 
                        datetime, tuple, dict, list)
    
    def __init__(self, library, port=8270):
        # Cannot use allow_none attribute since it's been added in 2.5
        SimpleXMLRPCServer.__init__(self, ('localhost', int(port)))
        self._library = library
        self.register_function(self.get_keyword_names)
        self.register_function(self.run_keyword)
        self.register_function(self.stop_remote_server)
        # May want to enable this later. May also want to use DocXMLRPCServer.
        # self.register_introspection_functions()
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
        self._redirect_stdout()
        result = {'status':'PASS', 'return':'', 'message':'',  'output':''}
        try:
            return_value = getattr(self._library, name)(*args)
            result['return'] = self._handle_return_value(return_value)
        except Exception, exp:
            result['status'] = 'FAIL'
            result['message'] = str(exp) #cepexception[0]
        result['output'] = self._restore_stdout()
        return result
  
    def _handle_return_value(self, return_value):
        # Can't set 'allow_none' in init because it's only in Python 2.5
        if return_value is None:
            return ''
        # TODO: What about tuple/dict/list containing non-supported types?
        # Same issue also with the ruby version.
        elif isinstance(return_value, self._supported_types):
            return return_value
        else:
            return str(return_value)

    def _redirect_stdout(self):
        # TODO: What about stderr?
        sys.stdout = StringIO()

    def _restore_stdout(self):
        output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        return output

