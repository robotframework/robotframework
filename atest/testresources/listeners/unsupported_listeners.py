import sys


def close():
    sys.exit('This should not be called')


class V1Listener:
    ROBOT_LISTENER_API_VERSION = 1

    def close(self):
        close()


class V4Listener:
    ROBOT_LISTENER_API_VERSION = '4'

    def close(self):
        close()


class InvalidVersionListener:
    ROBOT_LISTENER_API_VERSION = 'kekkonen'

    def close(self):
        close()
