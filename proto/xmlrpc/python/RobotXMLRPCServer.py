import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from StringIO import StringIO
from datetime import datetime
from types import MethodType, FunctionType


class RobotXmlRpcServer(SimpleXMLRPCServer):
  
    _supported_types = (datetime, int, long, float, bool, basestring, 
                        tuple, dict, list)
    # TODO: What about tuple/dict/list containing non-supported types?
    # Same issue also with the ruby version.
    
    def __init__(self, library, port=8080):
        SimpleXMLRPCServer.__init__(self, ('localhost', int(port)),
                                    allow_none=True)
        # TODO: allow_none doesn't seem to be available in Python 2.3
        self._library = library
        self.register_function(self.get_keyword_names)
        self.register_function(self.run_keyword)
        self.register_function(self.stop)
        self.register_introspection_functions()
        self.serve_forever()

    def stop(self):
        self.server_close()

    def get_keyword_names(self):
        return [ attr for attr in dir(self._library) if attr[0] != '_'
                 and isinstance(getattr(self._library, attr),
                                (MethodType, FunctionType)) ]

    def run_keyword(self, name, args):
        self._redirect_stdout()
        result = {'status':'PASS', 'return':'', 'message':'',  'output':''}
        try:
            return_value = getattr(self._library, name)(*args)
            result['return'] = self._convert_value_for_xmlrpc(return_value)
        except Exception, exception:
            result['status'] = 'FAIL'
            result['message'] = exception[0]
        result['output'] = self._restore_stdout()
        return result
  
    def _convert_value_for_xmlrpc(self, return_value):
        if isinstance(return_value, self._supported_types):
            return return_value
        else:
            return str(return_value)

    def _redirect_stdout(self):
        # TODO: What about stderr?
        sys.stdout = StringIO()
  
    def _restore_stdout(self):
        output = sys.stdout.read()
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        return output
