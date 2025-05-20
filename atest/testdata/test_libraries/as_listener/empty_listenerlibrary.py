import sys

from robot.api.deco import library


class listener:
    ROBOT_LISTENER_API_VERSION = "2"

    def start_test(self, name, attrs):
        self._stderr("START TEST")

    def end_test(self, name, attrs):
        self._stderr("END TEST")

    def log_message(self, msg):
        self._stderr(f"MESSAGE {msg['message']}")

    def close(self):
        self._stderr("CLOSE")

    def _stderr(self, msg):
        sys.__stderr__.write(f"{msg}\n")


@library(scope="TEST", listener=listener())
class empty_listenerlibrary:
    pass
