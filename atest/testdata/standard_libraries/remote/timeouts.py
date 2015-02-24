import sys
import time
from remoteserver import RemoteServer


class Timeouts(object):

    def sleep(self, secs):
        time.sleep(int(secs))


if __name__ == '__main__':
    RemoteServer(Timeouts(), *sys.argv[1:])
