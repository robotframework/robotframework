import sys

from robot.api import logger


class InitLogging:
    called = 0

    def __init__(self):
        InitLogging.called += 1
        print("*WARN* Warning via stdout in init", self.called)
        print("Info via stderr in init", self.called, file=sys.stderr)
        logger.warn(f"Warning via API in init {self.called}")

    def keyword(self):
        pass
