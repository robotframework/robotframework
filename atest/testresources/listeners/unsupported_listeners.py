import sys


def close():
    sys.exit('This should not be called')


class V1ClassListener:
    ROBOT_LISTENER_API_VERSION = 1

    def close(self):
        close()


class InvalidVersionClassListener:
    ROBOT_LISTENER_API_VERSION = 'kekkonen'

    def close(self):
        close()
