import sys


class Listener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, name='X'):
        self.name = name

    def start_suite(self, name, attrs):
        self._log("from listener {0}".format(self.name))

    def close(self):
        self._log("listener close")

    def report_file(self, path):
        self._log("report {0}".format(path))

    def log_file(self, path):
        self._log("log {0}".format(path))

    def output_file(self, path):
        self._log("output {0}".format(path))

    def _log(self, message):
        sys.__stdout__.write("[{0}]\n".format(message))
