import sys
from remoteserver import DirectResultRemoteServer


class SpecialErrors:

    def continuable(self, message, traceback):
        return self._special_error(message, traceback, continuable=True)

    def fatal(self, message, traceback):
        return self._special_error(message, traceback,
                                   fatal='this wins', continuable=42)

    def _special_error(self, message, traceback, continuable=False, fatal=False):
        return {'status': 'FAIL', 'error': message, 'traceback': traceback,
                'continuable': continuable, 'fatal': fatal}


if __name__ == '__main__':
    DirectResultRemoteServer(SpecialErrors(), *sys.argv[1:])
