from robot.api import logger
from robot.api.deco import library


@library(listener='SELF')
class AddMessageToTestBody:

    def start_test(self, data, result):
        if data.name == 'Messages in test body are ignored':
            logger.info('Hello says listener!')

    def end_test(self, data, result):
        if data.name == 'Messages in test body are ignored':
            logger.info('Bye says listener!')
