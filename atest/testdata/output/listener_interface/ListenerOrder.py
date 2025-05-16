import os
import tempfile
from pathlib import Path

from robot.api.deco import library


@library(listener="SELF", scope="GLOBAL")
class ListenerOrder:
    tempdir = Path(os.getenv("TEMPDIR", tempfile.gettempdir()))

    def __init__(self, name, priority=None):
        if priority is not None:
            self.ROBOT_LISTENER_PRIORITY = priority
        self.name = f"{name} ({priority})"

    def start_suite(self, data, result):
        self._write("start_suite")

    def log_message(self, msg):
        self._write("log_message")

    def end_test(self, data, result):
        self._write("end_test")

    def close(self):
        self._write("close", "listener_close_order.log")

    def _write(self, msg, name="listener_order.log"):
        with open(self.tempdir / name, "a", encoding="ASCII") as file:
            file.write(f"{self.name}: {msg}\n")
