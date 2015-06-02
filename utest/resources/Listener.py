import sys


class Listener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, name='X'):
        self.name = name

    def start_suite(self, name, attrs):
        self._log("from listener {}".format(self.name))

    def close(self):
        self._log("listener close")

    def report_file(self, path):
        self._log("report {}".format(path))

    def log_file(self, path):
        self._log("log {}".format(path))

    def output_file(self, path):
        self._log("output {}".format(path))

    def _log(self, message):
        sys.__stdout__.write("[{}]\n".format(message))
