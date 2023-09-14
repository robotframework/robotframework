import datetime
import sys

from remoteserver import RemoteServer


class ReturnValues:

    def string(self):
        return 'Hyvä tulos!'

    def integer(self):
        return 42

    def float(self):
        return 3.14

    def boolean(self):
        return False

    def datetime(self):
        return datetime.datetime(2023, 9, 14, 17, 30, 23)

    def list(self):
        return [1, 2, 'lolme']

    def dict(self):
        return {'a': 1, 'b': [2, 3]}


if __name__ == '__main__':
    RemoteServer(ReturnValues(), *sys.argv[1:])
