import xmlrpclib

try:
    from robot.errors import RemoteError
except ImportError:
    RemoteError = None


class Remote:
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, uri='http://localhost:8270'):
        if '://' not in uri:
            uri = 'http://' + uri
        self._library = xmlrpclib.Server(uri)

    def get_keyword_names(self):
        # TODO: Support also getKeywordNames (and runKeyword etc.)
        return self._library.get_keyword_names()

    def get_keyword_arguments(self, name):
        # TODO: Handle errors
        return self._library.get_keyword_arguments(name)

    def get_keyword_documentation(self, name):
        return self._library.get_keyword_documentation(name)

    def run_keyword(self, name, args):
        args = [ self._handle_argument(arg) for arg in args ]
        try:
            result = self._library.run_keyword(name, args)
        except xmlrpclib.Fault, err:
            raise RuntimeError(err.faultString)
        print result['output']
        if result['status'] != 'PASS':
            self._raise_failed(result['error'], result.get('traceback', ''))
        return result['return']

    def _handle_argument(self, arg):
        if isinstance(arg, (basestring, int, long, float, bool)):
            return arg
        if isinstance(arg, (tuple, list)):
            return [ self._handle_argument(item) for item in arg ]
        if isinstance(arg, dict):
            return dict([ (self._str(key), self._handle_argument(value))
                          for key, value in arg.items() ])
        return self._str(arg)

    def _str(self, item):
        if item is None:
            return ''
        return str(item)

    def _raise_failed(self, message, traceback):
        if RemoteError is not None:
            raise RemoteError(message, traceback)
        # Support for Robot Framework 2.0.2 and earlier.
        print '*INFO*', traceback
        raise AssertionError(message)

