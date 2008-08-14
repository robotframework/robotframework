from SimpleXMLRPCServer import SimpleXMLRPCServer
from types import *
from StringIO import StringIO
from datetime import datetime

SUPPORTED_TYPES = [datetime(1,1,1).__class__, IntType, FloatType, 
                   BooleanType, StringType, TupleType, DictType, ListType]


class RobotXMLRPCServer(SimpleXMLRPCServer):
  
    def __init__(self, library, port=8080):
        SimpleXMLRPCServer.__init__(self, ('localhost', port))
        self.library = library

    def get_keyword_names(self):
        print dir(library)
        return dir(library)

    def run_keyword(self, name, args):
        self._redirect_stdout()
        result = {'status':'PASS', 'return':'', 'message':'',  'output':''}
        try:
            method = getattr(name, self.library)
            return_value = self.library.method(*args)
            result['return'] = self._convert_value_for_xmlrpc(return_value)
        except Exception, exception:
            result['status'] = 'FAIL'
            result['message'] = exception[0]
        result['output'] = self._restore_stdout()
        return result
  
    def _convert_value_for_xmlrpc(self, return_value):
        # Because ruby's xmlrpc does not support sending nil values, 
        # those have to be converter to empty strings
        #    if return_value == nil
        #      return ''
        #    end
        if SUPPORTED_TYPES.count(return_value.__class__) > 0:
            return return_value
        else:
            return str(return_value)

    def _redirect_stdout(self):
        self.io = StringIO
        sys.stdout = self.io
        sys.stderr = self.io
  
    def _restore_stdout(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        result = self.io.read() 
        self.io.close()
        return result
  
    def stop(self):
        self.server_close()
