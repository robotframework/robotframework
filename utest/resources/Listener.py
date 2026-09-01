import sys


class Listener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, name="X"):
        self.name = name

    def start_suite(self, name, attrs):
        self._log(f"from listener {self.name}")

    def close(self):
        self._log("listener close")

    def report_file(self, path):
        self._log(f"report {path}")

    def log_file(self, path):
        self._log(f"log {path}")

    def output_file(self, path):
        self._log(f"output {path}")

    def _log(self, message):
        sys.__stdout__.write(f"[{message}]\n")
