import xmlrpclib
import socket
import time
import sys
try:
    from xml.parsers.expat import ExpatError
except ImportError:
    ExpatError = None   # Support for Jython 2.2

from robot.errors import RemoteError


class Remote:
    
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, uri='http://localhost:8270'):
        if '://' not in uri:
            uri = 'http://' + uri
        if uri.startswith('rmi://'):
            self._client = RmiRemoteClient(uri)
        else:
            self._client = XmlRpcRemoteClient(uri)

    def get_keyword_names(self, attempts=5):
        for i in range(attempts):
            try:
                return self._client.get_keyword_names()
            except TypeError, err:
                time.sleep(1)
        raise RuntimeError('Connecting remote server failed: %s' % err)

    def get_keyword_arguments(self, name):
        try:
            return self._client.get_keyword_arguments(name)
        except TypeError:
            return ['*args']

    def get_keyword_documentation(self, name):
        try:
            return self._client.get_keyword_documentation(name)
        except TypeError:
            return ''

    def run_keyword(self, name, args):
        args = [ self._handle_argument(arg) for arg in args ]
        result = RemoteResult(self._client.run_keyword(name, args))
        sys.stdout.write(result.output)
        if result.status != 'PASS':
            raise RemoteError(result.error, result.traceback)
        return result.return_

    def _handle_argument(self, arg):
        # TODO: Should handle also basic Java types
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


class RemoteResult:

    def __init__(self, result):
        try:
            self.status = result['status']
            self.output = result.get('output', '')
            self.return_ = result.get('return', '')
            self.error = result.get('error', '')
            self.traceback = result.get('traceback', '')
        except (KeyError, AttributeError):
            raise RuntimeError('Invalid remote result dictionary: %s' % result)


class XmlRpcRemoteClient:

    def __init__(self, uri):
        self._server = xmlrpclib.ServerProxy(uri, encoding='UTF-8')

    def get_keyword_names(self):
        try:
            return self._server.get_keyword_names()
        except socket.error, (errno, err):
            raise TypeError(err)
        except xmlrpclib.Error, err:
            raise TypeError(err)

    def get_keyword_arguments(self, name):
        try:
            return self._server.get_keyword_arguments(name)
        except xmlrpclib.Error:
            raise TypeError

    def get_keyword_documentation(self, name):
        try:
            return self._server.get_keyword_documentation(name)
        except xmlrpclib.Error:
            raise TypeError

    def run_keyword(self, name, args):
        try:
            return self._server.run_keyword(name, args)
        except xmlrpclib.Error, err:
            raise RuntimeError(err.faultString)
        except socket.error, (errno, err):
            raise RuntimeError('Connection to remote server broken: %s' % err)
        except ExpatError, err:
            raise RuntimeError('Processing XML-RPC return value failed. '
                               'Most often this happens when the return value '
                               'contains characters that are not valid in XML. '
                               'Original error was: ExpatError: %s' % err)


if not sys.platform.startswith('java'):

    def RmiRemoteClient(uri):
        raise RuntimeError('Using RMI requires running tests with Jython')

else:

    # from java.xxx import RMIStuff

    class RmiRemoteClient:

        def __init__(self, uri):
            pass

        def get_keyword_names(self):
            return ['test']

        def get_keyword_arguments(self, name):
            raise TypeError

        def get_keyword_documentation(self, name):
            raise TypeError

        def run_keyword(self, name, args):
            return {'status': 'PASS', 'output': 'Hello, world!\n'}
