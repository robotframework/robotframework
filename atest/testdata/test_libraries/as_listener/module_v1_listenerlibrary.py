import sys


class Listener(object):

    def start_test(self, name, doc, tags):
        self._stderr("START TEST %s %s %s" % (name, doc, tags))

    def end_test(self, status, message):
        self._stderr("END TEST %s %s" % (status, message))

    def close(self):
        self._stderr("CLOSE")

    def _stderr(self, msg):
        sys.__stderr__.write("%s\n" % msg)

ROBOT_LIBRARY_LISTENER = Listener()
