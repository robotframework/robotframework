import sys


class empty_listenerlibrary(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.level = 'suite'

    def _start_test(self, name, attrs):
        self._stderr("START TEST")
        self.level = 'test'

    def _end_test(self, name, attrs):
        self._stderr("END TEST")

    def log_message(self, msg):
        self._stderr("MESSAGE %s" % msg['message'])

    def _close(self):
        self._stderr("CLOSE (%s)" % self.level)

    def _stderr(self, msg):
        sys.__stderr__.write("%s\n" % msg)
