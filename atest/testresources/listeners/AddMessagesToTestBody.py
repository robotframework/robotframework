from robot.api import logger
from robot.api.deco import library


@library(listener='SELF')
class AddMessagesToTestBody:

    def __init__(self, name=None):
        self.name = name

    def start_test(self, data, result):
        if data.name == self.name or not self.name:
            logger.info(f"Hello '{data.name}', says listener!")

    def end_test(self, data, result):
        if data.name == self.name or not self.name:
            logger.info(f"Bye '{data.name}', says listener!")
