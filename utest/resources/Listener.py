import sys


class Listener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, name):
        self.name = name

    def start_suite(self, name, attrs):
        sys.__stdout__.write("[from listener {}]\n".format(self.name))

    def close(self):
        sys.__stdout__.write("[listener close]\n")

    def report_file(self, path):
        sys.__stdout__.write("[report {}]\n".format(path))

    def log_file(self, path):
        sys.__stdout__.write("[report {}]\n".format(path))

    def output_file(self, path):
        sys.__stdout__.write("[report {}]\n".format(path))
