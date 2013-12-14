import sys
from xmlrpclib import Binary

from remoteserver import RemoteServer


class DirectResultRemoteServer(RemoteServer):

    def run_keyword(self, name, args, kwargs=None):
        return getattr(self.library, name)(*args, **(kwargs or {}))


class BinaryResult(object):

    def return_binary(self, *ordinals):
        return self._result(return_=self._binary(ordinals))

    def log_binary(self, *ordinals):
        return self._result(output=self._binary(ordinals))

    def fail_binary(self, *ordinals):
        return self._result(error=self._binary(ordinals, 'Error: '),
                            traceback=self._binary(ordinals, 'Traceback: '))

    def _binary(self, ordinals, extra=''):
        return Binary(extra + ''.join(chr(int(o)) for o in ordinals))

    def _result(self, return_='', output='', error='', traceback=''):
        return {'status': 'PASS' if not error else 'FAIL',
                'return': return_, 'output': output,
                'error': error, 'traceback': traceback}


if __name__ == '__main__':
    DirectResultRemoteServer(BinaryResult(), *sys.argv[1:])
