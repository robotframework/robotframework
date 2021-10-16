import sys
from remoteserver import DirectResultRemoteServer


class Invalid:

    def non_dict_result_dict(self):
        return 42

    def invalid_result_dict(self):
        return {}

    def invalid_char_in_xml(self):
        return {'status': 'PASS', 'return': '\x00'}

    def exception(self, message):
        raise Exception(message)

    def shutdown(self):
        sys.exit()


if __name__ == '__main__':
    DirectResultRemoteServer(Invalid(), *sys.argv[1:])
