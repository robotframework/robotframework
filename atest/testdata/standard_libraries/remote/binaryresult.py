import sys
from xmlrpc.client import Binary

from remoteserver import DirectResultRemoteServer


class BinaryResult:

    def return_binary(self, *ordinals):
        return self._result(return_=self._binary(ordinals))

    def return_binary_list(self, *ordinals):
        return self._result(return_=[self._binary([o]) for o in ordinals])

    def return_binary_dict(self, **ordinals):
        ret = dict((k, self._binary([v])) for k, v in ordinals.items())
        return self._result(return_=ret)

    def return_nested_binary(self, *stuff, **more):
        ret_list = [self._binary([o]) for o in stuff]
        ret_dict = dict((k, self._binary([v])) for k, v in more.items())
        ret_dict['list'] = ret_list[:]
        ret_dict['dict'] = ret_dict.copy()
        ret_list.append(ret_dict)
        return self._result(return_=ret_list)

    def log_binary(self, *ordinals):
        return self._result(output=self._binary(ordinals))

    def fail_binary(self, *ordinals):
        return self._result(error=self._binary(ordinals, b'Error: '),
                            traceback=self._binary(ordinals, b'Traceback: '))

    def _binary(self, ordinals, extra=b''):
        return Binary(extra + bytes(int(o) for o in ordinals))

    def _result(self, return_='', output='', error='', traceback=''):
        return {'status': 'PASS' if not error else 'FAIL',
                'return': return_, 'output': output,
                'error': error, 'traceback': traceback}


if __name__ == '__main__':
    DirectResultRemoteServer(BinaryResult(), *sys.argv[1:])
